"""
BN-008: Tests de la API de consulta patrimonial.
Correr con: pytest tests/test_api_portfolio.py -v
"""
from tests.conftest import make_asset, make_portfolio, make_position, make_source


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
