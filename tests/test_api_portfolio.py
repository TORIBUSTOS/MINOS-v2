"""
BN-008: Tests de la API de consulta patrimonial.
Correr con: pytest tests/test_api_portfolio.py -v
"""
from datetime import datetime, timezone

import pytest

from src.services.market_data import PriceResult
from tests.conftest import make_asset, make_portfolio, make_position, make_source


@pytest.fixture(autouse=True)
def no_live_quotes(monkeypatch):
    def fake_get_quote(ticker, exchange=None, instrument_type=None):
        now = datetime(2026, 4, 30, tzinfo=timezone.utc)
        return PriceResult(
            input_ticker=ticker,
            resolved_symbol=ticker,
            source="test",
            price=None,
            currency="ARS",
            timestamp=None,
            fetched_at=now,
            instrument_type=instrument_type,
            exchange=exchange,
            quote_unit="PRICE",
            status="FETCH_ERROR",
            is_stale=False,
            error="test quote unavailable",
        )

    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", fake_get_quote)


def _seed(db_session):
    src_b = make_source(db_session, "Balanz")
    src_i = make_source(db_session, "IOL")
    port1 = make_portfolio(db_session, "Principal", src_b)
    port2 = make_portfolio(db_session, "Conservadora", src_i)
    a_ggal = make_asset(db_session, "GGAL")
    a_aapl = make_asset(db_session, "AAPL")
    make_position(db_session, port1, a_ggal, "GGAL", valuation=3000.0, currency="ARS")
    make_position(db_session, port1, a_aapl, "AAPL", valuation=2000.0, currency="USD")
    make_position(db_session, port2, a_ggal, "GGAL", valuation=1000.0, currency="ARS")
    db_session.commit()


# ── GET /api/v1/portfolio/summary ─────────────────────────────────────────────

def test_portfolio_summary_returns_200(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/portfolio/summary").status_code == 200


def test_portfolio_summary_total_valuation(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/summary").json()
    assert body["total_valuation"] == 6000.0


def test_portfolio_summary_has_by_asset(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/summary").json()
    tickers = {item["ticker"] for item in body["by_asset"]}
    assert {"GGAL", "AAPL"} == tickers


def test_portfolio_summary_has_by_source(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/summary").json()
    sources = {item["source"] for item in body["by_source"]}
    assert {"Balanz", "IOL"} == sources


def test_portfolio_summary_has_by_currency(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/summary").json()
    currencies = {item["currency"] for item in body["by_currency"]}
    assert {"ARS", "USD"} == currencies


def test_portfolio_summary_empty_db(client):
    body = client.get("/api/v1/portfolio/summary").json()
    assert body["total_valuation"] == 0.0
    assert body["by_asset"] == []
    assert body["live_market"]["daily_pnl_total"] == 0.0
    assert body["live_market"]["freshness_summary"] == {}


# ── GET /api/v1/portfolio/by-source ──────────────────────────────────────────

def test_portfolio_by_source_returns_200(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/portfolio/by-source").status_code == 200


def test_portfolio_by_source_values(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/by-source").json()
    by_source = {item["source"]: item for item in body}
    assert by_source["Balanz"]["valuation"] == 5000.0
    assert by_source["IOL"]["valuation"] == 1000.0


# ── GET /api/v1/portfolio/by-currency ────────────────────────────────────────

def test_portfolio_by_currency_returns_200(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/portfolio/by-currency").status_code == 200


def test_portfolio_by_currency_values(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolio/by-currency").json()
    by_cur = {item["currency"]: item for item in body}
    assert by_cur["ARS"]["valuation"] == 4000.0
    assert by_cur["USD"]["valuation"] == 2000.0


# ── GET /api/v1/portfolios ────────────────────────────────────────────────────

def test_portfolios_list_returns_200(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/portfolios").status_code == 200


def test_portfolios_list_returns_all(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolios").json()
    names = {item["name"] for item in body}
    assert {"Principal", "Conservadora"} == names


def test_portfolios_list_position_count(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/portfolios").json()
    by_name = {item["name"]: item for item in body}
    assert by_name["Principal"]["position_count"] == 2
    assert by_name["Conservadora"]["position_count"] == 1


# ── GET /api/v1/tickers/unified ───────────────────────────────────────────────

def test_tickers_unified_returns_200(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/tickers/unified").status_code == 200


def test_tickers_unified_distinct_tickers(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/tickers/unified").json()
    tickers = [item["ticker"] for item in body]
    assert len(tickers) == len(set(tickers))
    assert set(tickers) == {"GGAL", "AAPL"}


def test_tickers_unified_ggal_presence_two(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/tickers/unified").json()
    by_ticker = {item["ticker"]: item for item in body}
    assert by_ticker["GGAL"]["presence"] == 2
    assert by_ticker["AAPL"]["presence"] == 1


# ── Variación intradiaria (day_change) ────────────────────────────────────────

def test_portfolio_summary_trace_has_day_change_fields_when_previous_close_available(
    client, db_session, monkeypatch
):
    """Cuando el quote incluye previous_close, el trace expone day_change y day_change_pct."""
    from decimal import Decimal
    from datetime import datetime, timezone
    from src.services.market_data import PriceResult

    _seed(db_session)

    def quote_with_prev_close(ticker, exchange=None, instrument_type=None):
        now = datetime(2026, 4, 30, tzinfo=timezone.utc)
        return PriceResult(
            input_ticker=ticker,
            resolved_symbol=ticker,
            source="test",
            price=Decimal("4500.0"),
            currency="ARS",
            timestamp=now,
            fetched_at=now,
            instrument_type=instrument_type,
            exchange=exchange,
            quote_unit="PRICE",
            status="OK",
            is_stale=False,
            error=None,
            previous_close=Decimal("4200.0"),
        )

    monkeypatch.setattr(
        "src.services.portfolio_engine.MarketDataService.get_quote",
        quote_with_prev_close,
    )

    body = client.get("/api/v1/portfolio/summary").json()
    by_ticker = {item["ticker"]: item for item in body["by_asset"]}
    trace = by_ticker["GGAL"]["valuation_trace"]

    assert trace["day_change"] == pytest.approx(300.0, abs=0.01)
    assert trace["day_change_pct"] == pytest.approx(7.14, abs=0.01)
    assert trace["day_impact"] is not None
    assert trace["data_freshness"] == "UNAVAILABLE"  # legacy test quote default


def test_portfolio_summary_exposes_live_market_aggregate(client, db_session, monkeypatch):
    from decimal import Decimal
    from src.services.market_data import PriceResult

    _seed(db_session)
    now = datetime(2026, 4, 30, 15, 30, tzinfo=timezone.utc)

    def quote_with_live_fields(ticker, exchange=None, instrument_type=None):
        return PriceResult(
            input_ticker=ticker,
            resolved_symbol=f"{ticker}.BA" if exchange == "BYMA" else ticker,
            source="test",
            price=Decimal("4500.0"),
            currency="ARS",
            timestamp=now,
            fetched_at=now,
            instrument_type=instrument_type,
            exchange=exchange,
            quote_unit="PRICE",
            status="OK",
            is_stale=False,
            error=None,
            previous_close=Decimal("4200.0"),
            data_freshness="LIVE",
            market_state="LIVE",
            last_market_time=now,
        )

    monkeypatch.setattr(
        "src.services.portfolio_engine.MarketDataService.get_quote",
        quote_with_live_fields,
    )

    body = client.get("/api/v1/portfolio/summary").json()
    live = body["live_market"]
    ggal = {item["ticker"]: item for item in body["by_asset"]}["GGAL"]

    assert live["daily_pnl_total"] > 0
    assert live["daily_pnl_pct"] > 0
    assert live["positive_count"] >= 1
    assert live["freshness_summary"]["LIVE"] >= 1
    assert live["last_market_time"] == now.isoformat()
    assert ggal["day_change"] == pytest.approx(300.0, abs=0.01)
    assert ggal["day_impact"] is not None
    assert ggal["data_freshness"] == "LIVE"
    assert ggal["market_state"] == "LIVE"


def test_portfolio_summary_trace_day_change_none_without_previous_close(client, db_session):
    """Sin previous_close, los campos de variación del día son None."""
    _seed(db_session)  # usa el fixture no_live_quotes que retorna previous_close=None

    body = client.get("/api/v1/portfolio/summary").json()
    by_ticker = {item["ticker"]: item for item in body["by_asset"]}
    trace = by_ticker["GGAL"]["valuation_trace"]

    # no_live_quotes retorna price=None → day_change no computable
    assert trace["day_change"] is None
    assert trace["day_change_pct"] is None
    assert trace["day_impact"] is None
    assert body["live_market"]["unavailable_count"] >= 1


# ── PPC / avg_cost correctness ────────────────────────────────────────────────

def test_ppc_computed_from_cost_basis_and_quantity_in_fallback(client, db_session):
    """PPC = cost_basis / quantity aunque pos.avg_cost tenga un valor incorrecto almacenado."""
    src = make_source(db_session, "Balanz")
    port = make_portfolio(db_session, "Test", src)
    asset = make_asset(db_session, "GGAL")
    pos = make_position(db_session, port, asset, "GGAL", quantity=80.0, valuation=369354.0)
    # Simulamos el valor incorrecto que guarda el CSV del broker (4616.93 / 80 = 57.71)
    pos.avg_cost = 57.71
    pos.cost_basis = 369354.0
    db_session.commit()

    body = client.get("/api/v1/portfolio/summary").json()
    by_ticker = {item["ticker"]: item for item in body["by_asset"]}
    trace = by_ticker["GGAL"]["valuation_trace"]

    # PPC correcto = 369354 / 80 = 4616.925 ≈ 4616.93
    assert trace["avg_cost"] == pytest.approx(4616.93, abs=0.01)


def test_ppc_equals_cost_basis_over_quantity(client, db_session):
    """Validar con casos reales: PAMP nominales=100, valor_inicial=205061 → PPC=2050.61."""
    src = make_source(db_session, "Balanz")
    port = make_portfolio(db_session, "Test", src)
    asset = make_asset(db_session, "PAMP")
    pos = make_position(db_session, port, asset, "PAMP", quantity=100.0, valuation=205061.0)
    pos.avg_cost = 20.51  # valor incorrecto almacenado
    pos.cost_basis = 205061.0
    db_session.commit()

    body = client.get("/api/v1/portfolio/summary").json()
    by_ticker = {item["ticker"]: item for item in body["by_asset"]}
    trace = by_ticker["PAMP"]["valuation_trace"]

    assert trace["avg_cost"] == pytest.approx(2050.61, abs=0.01)


def test_pnl_absolute_computed_from_market_value_minus_cost_basis(client, db_session):
    """Rendimiento = valor_actual - valor_inicial (calculado, no del CSV del broker)."""
    src = make_source(db_session, "Balanz")
    port = make_portfolio(db_session, "Test", src)
    asset = make_asset(db_session, "GGAL")
    pos = make_position(db_session, port, asset, "GGAL", quantity=80.0, valuation=400000.0)
    pos.cost_basis = 369354.0
    pos.pnl_absolute = -99999.0  # valor incorrecto almacenado — debe ser ignorado
    db_session.commit()

    body = client.get("/api/v1/portfolio/summary").json()
    by_ticker = {item["ticker"]: item for item in body["by_asset"]}
    trace = by_ticker["GGAL"]["valuation_trace"]

    # Rendimiento = 400000 - 369354 = 30646
    assert trace["pnl_absolute"] == pytest.approx(30646.0, abs=1.0)


def test_portfolio_summary_trace_day_change_none_when_price_ok_but_no_previous_close(
    client, db_session, monkeypatch
):
    """price presente pero sin previous_close → day fields son None en _quote_trace."""
    from decimal import Decimal
    from datetime import datetime, timezone
    from src.services.market_data import PriceResult

    _seed(db_session)

    def quote_no_prev_close(ticker, exchange=None, instrument_type=None):
        now = datetime(2026, 4, 30, tzinfo=timezone.utc)
        return PriceResult(
            input_ticker=ticker,
            resolved_symbol=ticker,
            source="test",
            price=Decimal("4500.0"),
            currency="ARS",
            timestamp=now,
            fetched_at=now,
            instrument_type=instrument_type,
            exchange=exchange,
            quote_unit="PRICE",
            status="OK",
            is_stale=False,
            error=None,
            previous_close=None,  # yfinance no retornó previous_close
        )

    monkeypatch.setattr(
        "src.services.portfolio_engine.MarketDataService.get_quote",
        quote_no_prev_close,
    )

    body = client.get("/api/v1/portfolio/summary").json()
    by_ticker = {item["ticker"]: item for item in body["by_asset"]}
    trace = by_ticker["GGAL"]["valuation_trace"]

    assert trace["day_change"] is None
    assert trace["day_change_pct"] is None
    assert trace["day_impact"] is None
