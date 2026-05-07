"""
BN-005: Tests del Portfolio Engine — consolidación multi-cartera.
Correr con: pytest tests/test_portfolio_engine.py -v
"""
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session

from src.services.market_data import PriceResult
from src.services.portfolio_engine import consolidate
from tests.conftest import make_asset, make_portfolio, make_position, make_source


# ── Helpers locales ───────────────────────────────────────────────────────────

def _no_quote(ticker, exchange=None, instrument_type=None):
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


def _seed_two_portfolios(db: Session):
    """Dos carteras, dos fuentes, dos monedas, un ticker compartido."""
    src_balanz = make_source(db, "Balanz")
    src_iol = make_source(db, "IOL")

    port_principal = make_portfolio(db, "Principal", src_balanz)
    port_conserv = make_portfolio(db, "Conservadora", src_iol)

    asset_ggal = make_asset(db, "GGAL")
    asset_aapl = make_asset(db, "AAPL")
    asset_pamp = make_asset(db, "PAMP")

    # Principal (Balanz): GGAL 3000 ARS + AAPL 2000 USD
    make_position(db, port_principal, asset_ggal, "GGAL", valuation=3000.0, currency="ARS")
    make_position(db, port_principal, asset_aapl, "AAPL", valuation=2000.0, currency="USD")

    # Conservadora (IOL): GGAL 1000 ARS + PAMP 4000 ARS
    make_position(db, port_conserv, asset_ggal, "GGAL", valuation=1000.0, currency="ARS")
    make_position(db, port_conserv, asset_pamp, "PAMP", valuation=4000.0, currency="ARS")

    db.commit()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_consolidate_empty_db_returns_zero(db_session):
    result = consolidate(db_session)
    assert result["total_valuation"] == 0.0
    assert result["by_asset"] == []
    assert result["by_source"] == []
    assert result["by_currency"] == []


def test_consolidate_total_valuation_sums_all_positions(monkeypatch, db_session):
    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", _no_quote)
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    assert result["total_valuation"] == 10000.0  # 3000 + 2000 + 1000 + 4000


def test_consolidate_by_asset_groups_same_ticker(monkeypatch, db_session):
    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", _no_quote)
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_asset = {item["ticker"]: item for item in result["by_asset"]}

    # GGAL aparece en dos carteras → valuación sumada
    assert by_asset["GGAL"]["valuation"] == 4000.0  # 3000 + 1000
    assert by_asset["AAPL"]["valuation"] == 2000.0
    assert by_asset["PAMP"]["valuation"] == 4000.0


def test_consolidate_exposes_cedear_metadata(monkeypatch, db_session):
    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", _no_quote)
    src_balanz = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", src_balanz)
    asset_meli = make_asset(db_session, "MELI")
    make_position(db_session, portfolio, asset_meli, "MELI", valuation=291850.0, currency="ARS")
    db_session.commit()

    result = consolidate(db_session)
    meli = result["by_asset"][0]

    assert meli["ticker"] == "MELI"
    assert meli["asset_type"] == "CEDEAR"
    assert meli["underlying"] == "MercadoLibre Inc."
    assert meli["valuation_trace"]["instrument_type"] == "CEDEAR"


def test_consolidate_by_asset_percentage_correct(monkeypatch, db_session):
    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", _no_quote)
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_asset = {item["ticker"]: item for item in result["by_asset"]}

    assert by_asset["GGAL"]["pct"] == pytest.approx(40.0)   # 4000/10000
    assert by_asset["AAPL"]["pct"] == pytest.approx(20.0)   # 2000/10000
    assert by_asset["PAMP"]["pct"] == pytest.approx(40.0)   # 4000/10000


def test_consolidate_by_asset_tracks_portfolios(monkeypatch, db_session):
    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", _no_quote)
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_asset = {item["ticker"]: item for item in result["by_asset"]}

    assert set(by_asset["GGAL"]["portfolios"]) == {"Principal", "Conservadora"}
    assert by_asset["AAPL"]["portfolios"] == ["Principal"]


def test_consolidate_by_source(monkeypatch, db_session):
    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", _no_quote)
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_source = {item["source"]: item for item in result["by_source"]}

    assert by_source["Balanz"]["valuation"] == 5000.0  # 3000 + 2000
    assert by_source["IOL"]["valuation"] == 5000.0     # 1000 + 4000
    assert by_source["Balanz"]["pct"] == pytest.approx(50.0)


def test_consolidate_by_currency(monkeypatch, db_session):
    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", _no_quote)
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_currency = {item["currency"]: item for item in result["by_currency"]}

    assert by_currency["ARS"]["valuation"] == 8000.0   # 3000 + 1000 + 4000
    assert by_currency["USD"]["valuation"] == 2000.0
    assert by_currency["ARS"]["pct"] == pytest.approx(80.0)
    assert by_currency["USD"]["pct"] == pytest.approx(20.0)


def test_consolidate_percentages_sum_to_100(monkeypatch, db_session):
    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", _no_quote)
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)

    asset_pcts = sum(item["pct"] for item in result["by_asset"])
    source_pcts = sum(item["pct"] for item in result["by_source"])
    currency_pcts = sum(item["pct"] for item in result["by_currency"])

    assert asset_pcts == pytest.approx(100.0)
    assert source_pcts == pytest.approx(100.0)
    assert currency_pcts == pytest.approx(100.0)


def test_consolidate_uses_dynamic_quote_for_balanz_bma(monkeypatch, db_session):
    src_balanz = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", src_balanz)
    asset_bma = make_asset(db_session, "BMA")
    asset_bma.asset_type = "EQUITY"
    make_position(
        db_session,
        portfolio,
        asset_bma,
        "BMA",
        quantity=65,
        valuation=613403.05,
        currency="ARS",
    )
    db_session.commit()

    now = datetime(2026, 4, 30, tzinfo=timezone.utc)

    def fake_get_quote(ticker, exchange=None, instrument_type=None):
        assert ticker == "BMA"
        assert exchange == "BYMA"
        assert instrument_type == "EQUITY"
        return PriceResult(
            input_ticker="BMA",
            resolved_symbol="BMA.BA",
            source="test",
            price=Decimal("10870.00"),
            currency="ARS",
            timestamp=now,
            fetched_at=now,
            instrument_type="EQUITY",
            exchange="BYMA",
            quote_unit="PRICE",
            status="OK",
            is_stale=False,
            error=None,
        )

    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", fake_get_quote)

    result = consolidate(db_session)
    bma = result["by_asset"][0]

    assert result["total_valuation"] == pytest.approx(706550.00)
    assert bma["ticker"] == "BMA"
    assert bma["valuation"] == pytest.approx(706550.00)
    assert bma["market_value"] == pytest.approx(706550.00)
    assert bma["cost_basis"] == pytest.approx(613403.05)
    assert bma["pnl_absolute"] == pytest.approx(93146.95)
    assert bma["pnl_percentage"] == pytest.approx(15.19)
    assert bma["portfolio_weight"] == pytest.approx(100.0)
    assert isinstance(bma["valuation_traces"], list)
    assert len(bma["valuation_traces"]) == 1
    assert bma["valuation_trace"] == bma["valuation_traces"][0]
    assert bma["valuation_status"] == "OK"
    assert bma["valuation_trace"]["quantity"] == 65.0
    assert bma["valuation_trace"]["avg_cost"] == pytest.approx(9436.97)
    assert bma["valuation_trace"]["resolved_symbol"] == "BMA.BA"
    assert bma["valuation_trace"]["price"] == 10870.0
    assert bma["valuation_trace"]["currency"] == "ARS"
    assert bma["valuation_trace"]["status"] == "OK"
    assert bma["valuation_trace"]["valuation_status"] == "OK"
    assert bma["valuation_trace"]["timestamp"] == now.isoformat()
    assert bma["valuation_trace"]["fetched_at"] == now.isoformat()


def test_consolidate_infers_dynamic_quote_for_known_byma_equity(monkeypatch, db_session):
    src_balanz = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", src_balanz)
    asset_bma = make_asset(db_session, "BMA")
    assert asset_bma.asset_type == "unknown"
    make_position(
        db_session,
        portfolio,
        asset_bma,
        "BMA",
        quantity=65,
        valuation=613403.05,
        currency="ARS",
    )
    db_session.commit()

    def fake_get_quote(ticker, exchange=None, instrument_type=None):
        assert ticker == "BMA"
        assert exchange == "BYMA"
        assert instrument_type == "EQUITY"
        now = datetime(2026, 4, 30, tzinfo=timezone.utc)
        return PriceResult(
            input_ticker="BMA",
            resolved_symbol="BMA.BA",
            source="test",
            price=Decimal("10890.00"),
            currency="ARS",
            timestamp=now,
            fetched_at=now,
            instrument_type="EQUITY",
            exchange="BYMA",
            quote_unit="PRICE",
            status="OK",
            is_stale=False,
            error=None,
        )

    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", fake_get_quote)

    result = consolidate(db_session)
    bma = result["by_asset"][0]

    assert bma["market_value"] == pytest.approx(707850.0)
    assert bma["valuation_status"] == "OK"
    assert bma["valuation_trace"]["resolved_symbol"] == "BMA.BA"


def test_consolidate_uses_dynamic_quote_for_balanz_ypfd(monkeypatch, db_session):
    src_balanz = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", src_balanz)
    asset_ypfd = make_asset(db_session, "YPFD")
    asset_ypfd.asset_type = "EQUITY"
    make_position(
        db_session,
        portfolio,
        asset_ypfd,
        "YPFD",
        quantity=15,
        valuation=631346.85,
        currency="ARS",
    )
    db_session.commit()

    now = datetime(2026, 4, 30, tzinfo=timezone.utc)

    def fake_get_quote(ticker, exchange=None, instrument_type=None):
        assert ticker == "YPFD"
        assert exchange == "BYMA"
        assert instrument_type == "EQUITY"
        return PriceResult(
            input_ticker="YPFD",
            resolved_symbol="YPFD.BA",
            source="test",
            price=Decimal("66425.00"),
            currency="ARS",
            timestamp=now,
            fetched_at=now,
            instrument_type="EQUITY",
            exchange="BYMA",
            quote_unit="PRICE",
            status="OK",
            is_stale=False,
            error=None,
        )

    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", fake_get_quote)

    result = consolidate(db_session)
    ypfd = result["by_asset"][0]

    assert result["total_valuation"] == pytest.approx(996375.00)
    assert ypfd["ticker"] == "YPFD"
    assert ypfd["valuation"] == pytest.approx(996375.00)
    assert ypfd["market_value"] == pytest.approx(996375.00)
    assert ypfd["cost_basis"] == pytest.approx(631346.85)
    assert ypfd["pnl_absolute"] == pytest.approx(365028.15)
    assert ypfd["pnl_percentage"] == pytest.approx(57.82)
    assert ypfd["portfolio_weight"] == pytest.approx(100.0)
    assert isinstance(ypfd["valuation_traces"], list)
    assert len(ypfd["valuation_traces"]) == 1
    assert ypfd["valuation_trace"] == ypfd["valuation_traces"][0]
    assert ypfd["valuation_status"] == "OK"
    assert ypfd["valuation_trace"]["quantity"] == 15.0
    assert ypfd["valuation_trace"]["avg_cost"] == pytest.approx(42089.79)
    assert ypfd["valuation_trace"]["resolved_symbol"] == "YPFD.BA"
    assert ypfd["valuation_trace"]["price"] == 66425.0
    assert ypfd["valuation_trace"]["currency"] == "ARS"
    assert ypfd["valuation_trace"]["status"] == "OK"
    assert ypfd["valuation_trace"]["valuation_status"] == "OK"
    assert ypfd["valuation_trace"]["timestamp"] == now.isoformat()
    assert ypfd["valuation_trace"]["fetched_at"] == now.isoformat()


def test_consolidate_ars_non_equity_uses_stored_valuation_without_quote(monkeypatch, db_session):
    src_balanz = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", src_balanz)
    asset_al30 = make_asset(db_session, "AL30")
    asset_al30.asset_type = "bond"
    make_position(
        db_session,
        portfolio,
        asset_al30,
        "AL30",
        quantity=10,
        valuation=12345.67,
        currency="ARS",
    )
    db_session.commit()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("AL30 must not use dynamic BYMA equity quote")

    monkeypatch.setattr("src.services.portfolio_engine.MarketDataService.get_quote", fail_if_called)

    result = consolidate(db_session)
    al30 = result["by_asset"][0]

    assert result["total_valuation"] == pytest.approx(12345.67)
    assert al30["ticker"] == "AL30"
    assert al30["market_value"] == pytest.approx(12345.67)
    assert al30["cost_basis"] == pytest.approx(12345.67)
    assert al30["pnl_absolute"] == 0.0
    assert al30["pnl_percentage"] == 0.0
    assert al30["portfolio_weight"] == pytest.approx(100.0)
    assert isinstance(al30["valuation_traces"], list)
    assert al30["valuation_trace"]["resolved_symbol"] == "AL30"
    assert al30["valuation_trace"]["exchange"] is None
    assert al30["valuation_trace"]["instrument_type"] is None
    assert al30["valuation_trace"]["price"] is None
    assert al30["valuation_trace"]["status"] == "NO_DYNAMIC_QUOTE"
    assert al30["valuation_trace"]["valuation_status"] == "NO_DYNAMIC_QUOTE"
