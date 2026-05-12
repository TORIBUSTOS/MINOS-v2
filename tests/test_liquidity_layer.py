from tests.conftest import make_asset, make_portfolio, make_position, make_source


def _asset(db_session, ticker: str, asset_type: str, name: str | None = None):
    asset = make_asset(db_session, ticker)
    asset.asset_type = asset_type
    asset.name = name or ticker
    return asset


def test_portfolio_summary_reports_not_informed_when_no_liquidity(db_session):
    source = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", source)
    asset = _asset(db_session, "AL30", "BOND")
    make_position(db_session, portfolio, asset, "AL30", quantity=10, valuation=100_000)
    db_session.commit()

    from src.services.portfolio_engine import consolidate

    summary = consolidate(db_session)

    assert summary["liquidity_summary"]["is_informed"] is False
    assert summary["liquidity_summary"]["status"] == "NOT_INFORMED"
    assert summary["liquidity_summary"]["total"] == 0.0
    assert summary["liquidity_summary"]["items"] == []
    assert summary["by_asset"][0]["is_liquidity"] is False
    assert summary["by_asset"][0]["liquidity_kind"] is None


def test_portfolio_summary_detects_cash_position_as_liquidity(db_session):
    source = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", source)
    cash = _asset(db_session, "ARS", "CASH", "Caja pesos")
    equity = _asset(db_session, "AL30", "BOND")
    make_position(db_session, portfolio, cash, "ARS", quantity=150_000, valuation=150_000)
    make_position(db_session, portfolio, equity, "AL30", quantity=10, valuation=350_000)
    db_session.commit()

    from src.services.portfolio_engine import consolidate

    summary = consolidate(db_session)
    liquidity = summary["liquidity_summary"]
    cash_row = next(asset for asset in summary["by_asset"] if asset["ticker"] == "ARS")

    assert liquidity["is_informed"] is True
    assert liquidity["status"] == "INFORMED"
    assert liquidity["total"] == 150_000.0
    assert liquidity["pct"] == 30.0
    assert liquidity["items"][0]["ticker"] == "ARS"
    assert liquidity["items"][0]["liquidity_kind"] == "CASH"
    assert liquidity["by_currency"] == [{"currency": "ARS", "valuation": 150_000.0, "pct": 100.0}]
    assert cash_row["is_liquidity"] is True
    assert cash_row["liquidity_kind"] == "CASH"


def test_portfolio_summary_detects_money_market_fund_only_when_identifiable(db_session):
    source = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", source)
    money_market = _asset(db_session, "BCMMUSDA", "FUND", "Balanz money market usd")
    generic_fund = _asset(db_session, "CPRIVADA", "FUND", "Fondo comun ordinario")
    make_position(db_session, portfolio, money_market, "BCMMUSDA", quantity=1, valuation=200_000)
    make_position(db_session, portfolio, generic_fund, "CPRIVADA", quantity=1, valuation=300_000)
    db_session.commit()

    from src.services.portfolio_engine import consolidate

    summary = consolidate(db_session)
    liquidity = summary["liquidity_summary"]

    assert liquidity["is_informed"] is True
    assert liquidity["total"] == 200_000.0
    assert [item["ticker"] for item in liquidity["items"]] == ["BCMMUSDA"]
    assert liquidity["items"][0]["liquidity_kind"] == "MONEY_MARKET"
    assert next(asset for asset in summary["by_asset"] if asset["ticker"] == "CPRIVADA")["is_liquidity"] is False


def test_reallocation_connects_informed_liquidity_with_releasable_capital():
    from src.services.reallocation import ReallocationEngine

    summary = {
        "total_valuation": 800_000.0,
        "liquidity_summary": {"is_informed": True, "total": 50_000.0},
        "by_asset": [
            {
                "ticker": "ARS",
                "valuation": 50_000.0,
                "pct": 6.25,
                "is_liquidity": True,
                "valuation_status": "NO_DYNAMIC_QUOTE",
            },
            {
                "ticker": "GGAL",
                "valuation": 700_000.0,
                "pct": 87.5,
                "is_liquidity": False,
                "valuation_status": "OK",
            },
            {
                "ticker": "YPFD",
                "valuation": 50_000.0,
                "pct": 6.25,
                "is_liquidity": False,
                "valuation_status": "OK",
            },
        ],
    }
    result = ReallocationEngine().suggest(summary)

    assert result["informed_liquidity"] == 50_000.0
    assert result["releasable_capital"] == 700_000.0
    assert result["available_capital"] == 750_000.0
    assert all(rotation["from"] != "ARS" for rotation in result["rotations"])


def test_api_portfolio_summary_exposes_liquidity_summary(client, db_session):
    source = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", source)
    cash = _asset(db_session, "USD", "CASH", "Caja dolares")
    make_position(db_session, portfolio, cash, "USD", quantity=1_000, currency="USD", valuation=1_000)
    db_session.commit()

    response = client.get("/api/v1/portfolio/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["liquidity_summary"]["is_informed"] is True
    assert body["liquidity_summary"]["items"][0]["ticker"] == "USD"
