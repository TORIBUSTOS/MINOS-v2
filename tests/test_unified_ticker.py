"""
BN-006: Tests del Unified Ticker Layer.
Regla clave: NO suma nominales entre carteras — solo rastrea presencia.
Correr con: pytest tests/test_unified_ticker.py -v
"""
from src.services.unified_ticker import unify
from tests.conftest import make_asset, make_portfolio, make_position, make_source


def _seed(db_session):
    """3 carteras, GGAL en 2, AAPL solo en 1, PAMP solo en 1."""
    src_balanz = make_source(db_session, "Balanz")
    src_iol = make_source(db_session, "IOL")

    port1 = make_portfolio(db_session, "Principal", src_balanz)
    port2 = make_portfolio(db_session, "Conservadora", src_balanz)
    port3 = make_portfolio(db_session, "Agresiva", src_iol)

    a_ggal = make_asset(db_session, "GGAL")
    a_aapl = make_asset(db_session, "AAPL")
    a_pamp = make_asset(db_session, "PAMP")

    make_position(db_session, port1, a_ggal, "GGAL", quantity=100, valuation=1000)
    make_position(db_session, port2, a_ggal, "GGAL", quantity=200, valuation=2000)  # GGAL en 2 carteras
    make_position(db_session, port1, a_aapl, "AAPL", quantity=10, valuation=5000)
    make_position(db_session, port3, a_pamp, "PAMP", quantity=50, valuation=500)

    db_session.commit()


def test_unify_returns_distinct_tickers(db_session):
    _seed(db_session)
    result = unify(db_session)
    tickers = [item["ticker"] for item in result]
    assert len(tickers) == len(set(tickers))  # sin duplicados
    assert set(tickers) == {"GGAL", "AAPL", "PAMP"}


def test_unify_presence_counts_portfolios_not_sum(db_session):
    """GGAL en 2 carteras → presence=2, NO suma nominales."""
    _seed(db_session)
    result = unify(db_session)
    by_ticker = {item["ticker"]: item for item in result}

    assert by_ticker["GGAL"]["presence"] == 2
    assert by_ticker["AAPL"]["presence"] == 1
    assert by_ticker["PAMP"]["presence"] == 1


def test_unify_does_not_sum_quantities_across_portfolios(db_session):
    """GGAL: 100 en port1 + 200 en port2 — no se suman."""
    _seed(db_session)
    result = unify(db_session)
    by_ticker = {item["ticker"]: item for item in result}

    # Cada entrada de cartera se conserva por separado
    ggal_entries = by_ticker["GGAL"]["entries"]
    assert len(ggal_entries) == 2
    quantities = {e["quantity"] for e in ggal_entries}
    assert quantities == {100.0, 200.0}


def test_unify_tracks_portfolio_names(db_session):
    _seed(db_session)
    result = unify(db_session)
    by_ticker = {item["ticker"]: item for item in result}

    portfolios = {e["portfolio"] for e in by_ticker["GGAL"]["entries"]}
    assert portfolios == {"Principal", "Conservadora"}


def test_unify_empty_db_returns_empty_list(db_session):
    assert unify(db_session) == []


def test_unify_single_ticker_single_portfolio(db_session):
    src = make_source(db_session, "Test")
    port = make_portfolio(db_session, "Solo", src)
    asset = make_asset(db_session, "MSFT")
    make_position(db_session, port, asset, "MSFT", quantity=5, valuation=2000)
    db_session.commit()

    result = unify(db_session)
    assert len(result) == 1
    assert result[0]["ticker"] == "MSFT"
    assert result[0]["presence"] == 1
