"""
BN-005: Tests del Portfolio Engine — consolidación multi-cartera.
Correr con: pytest tests/test_portfolio_engine.py -v
"""
import pytest
from sqlalchemy.orm import Session

from src.services.portfolio_engine import consolidate
from tests.conftest import make_asset, make_portfolio, make_position, make_source


# ── Helpers locales ───────────────────────────────────────────────────────────

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


def test_consolidate_total_valuation_sums_all_positions(db_session):
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    assert result["total_valuation"] == 10000.0  # 3000 + 2000 + 1000 + 4000


def test_consolidate_by_asset_groups_same_ticker(db_session):
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_asset = {item["ticker"]: item for item in result["by_asset"]}

    # GGAL aparece en dos carteras → valuación sumada
    assert by_asset["GGAL"]["valuation"] == 4000.0  # 3000 + 1000
    assert by_asset["AAPL"]["valuation"] == 2000.0
    assert by_asset["PAMP"]["valuation"] == 4000.0


def test_consolidate_by_asset_percentage_correct(db_session):
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_asset = {item["ticker"]: item for item in result["by_asset"]}

    assert by_asset["GGAL"]["pct"] == pytest.approx(40.0)   # 4000/10000
    assert by_asset["AAPL"]["pct"] == pytest.approx(20.0)   # 2000/10000
    assert by_asset["PAMP"]["pct"] == pytest.approx(40.0)   # 4000/10000


def test_consolidate_by_asset_tracks_portfolios(db_session):
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_asset = {item["ticker"]: item for item in result["by_asset"]}

    assert set(by_asset["GGAL"]["portfolios"]) == {"Principal", "Conservadora"}
    assert by_asset["AAPL"]["portfolios"] == ["Principal"]


def test_consolidate_by_source(db_session):
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_source = {item["source"]: item for item in result["by_source"]}

    assert by_source["Balanz"]["valuation"] == 5000.0  # 3000 + 2000
    assert by_source["IOL"]["valuation"] == 5000.0     # 1000 + 4000
    assert by_source["Balanz"]["pct"] == pytest.approx(50.0)


def test_consolidate_by_currency(db_session):
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)
    by_currency = {item["currency"]: item for item in result["by_currency"]}

    assert by_currency["ARS"]["valuation"] == 8000.0   # 3000 + 1000 + 4000
    assert by_currency["USD"]["valuation"] == 2000.0
    assert by_currency["ARS"]["pct"] == pytest.approx(80.0)
    assert by_currency["USD"]["pct"] == pytest.approx(20.0)


def test_consolidate_percentages_sum_to_100(db_session):
    _seed_two_portfolios(db_session)
    result = consolidate(db_session)

    asset_pcts = sum(item["pct"] for item in result["by_asset"])
    source_pcts = sum(item["pct"] for item in result["by_source"])
    currency_pcts = sum(item["pct"] for item in result["by_currency"])

    assert asset_pcts == pytest.approx(100.0)
    assert source_pcts == pytest.approx(100.0)
    assert currency_pcts == pytest.approx(100.0)
