"""
BN-016: Tests de la API de inteligencia patrimonial.
Endpoints: /intelligence/signals, /intelligence/portfolio-status, /intelligence/reallocation
"""
from tests.conftest import make_asset, make_portfolio, make_position, make_source


def _seed(db_session):
    """Cartera concentrada: MELI 60%, GGAL 30%, AL30 10% → señales mixtas."""
    src = make_source(db_session, "Balanz")
    port = make_portfolio(db_session, "Principal", src)
    a_meli = make_asset(db_session, "MELI")
    a_ggal = make_asset(db_session, "GGAL")
    a_al30 = make_asset(db_session, "AL30")
    make_position(db_session, port, a_meli, "MELI", valuation=6000.0, currency="ARS")
    make_position(db_session, port, a_ggal, "GGAL", valuation=3000.0, currency="ARS")
    make_position(db_session, port, a_al30, "AL30", valuation=1000.0, currency="ARS")
    db_session.commit()


def _seed_diversificada(db_session):
    """Cartera equilibrada: 5 activos a 20% cada uno → todos HOLD."""
    src = make_source(db_session, "IOL")
    port = make_portfolio(db_session, "Balanceada", src)
    for ticker in ["AL30", "GD30", "GGAL", "PAMP", "BBAR"]:
        asset = make_asset(db_session, ticker)
        make_position(db_session, port, asset, ticker, valuation=2000.0, currency="ARS")
    db_session.commit()


# ── GET /api/v1/intelligence/signals ─────────────────────────────────────────

def test_signals_returns_200(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/intelligence/signals").status_code == 200


def test_signals_retorna_lista(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/signals").json()
    assert isinstance(body, list)


def test_signals_cada_item_tiene_campos_requeridos(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/signals").json()
    for item in body:
        assert "ticker" in item
        assert "signal" in item
        assert "reason" in item
        assert "pct" in item


def test_signals_valores_validos(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/signals").json()
    for item in body:
        assert item["signal"] in ("BUY", "HOLD", "SELL", "NEUTRAL")
        assert isinstance(item["pct"], float)


def test_signals_cartera_concentrada_incluye_sell(client, db_session):
    """Con MELI al 60% → al menos un ticker con SELL."""
    _seed(db_session)
    body = client.get("/api/v1/intelligence/signals").json()
    signals = {item["ticker"]: item["signal"] for item in body}
    assert signals.get("MELI") == "SELL"


def test_signals_db_vacia_retorna_lista_vacia(client):
    body = client.get("/api/v1/intelligence/signals").json()
    assert body == []


def test_signals_contiene_todos_los_tickers(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/signals").json()
    tickers = {item["ticker"] for item in body}
    assert {"MELI", "GGAL", "AL30"} == tickers


# ── GET /api/v1/intelligence/portfolio-status ─────────────────────────────────

def test_portfolio_status_returns_200(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/intelligence/portfolio-status").status_code == 200


def test_portfolio_status_tiene_campos_requeridos(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/portfolio-status").json()
    assert "status" in body
    assert "insights" in body
    assert "suggested_action" in body
    assert "sell_count" in body
    assert "buy_count" in body
    assert "hold_count" in body


def test_portfolio_status_valor_valido(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/portfolio-status").json()
    assert body["status"] in ("EXPANSIÓN", "NEUTRAL", "RIESGO")


def test_portfolio_status_cartera_concentrada_es_riesgo(client, db_session):
    """Cartera con MELI 60% → RIESGO."""
    _seed(db_session)
    body = client.get("/api/v1/intelligence/portfolio-status").json()
    assert body["status"] == "RIESGO"


def test_portfolio_status_insights_es_lista(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/portfolio-status").json()
    assert isinstance(body["insights"], list)
    assert len(body["insights"]) > 0


def test_portfolio_status_suggested_action_no_vacia(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/portfolio-status").json()
    assert isinstance(body["suggested_action"], str)
    assert len(body["suggested_action"]) > 0


def test_portfolio_status_db_vacia_retorna_neutral(client):
    body = client.get("/api/v1/intelligence/portfolio-status").json()
    assert body["status"] == "NEUTRAL"


def test_portfolio_status_contadores_coherentes(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/portfolio-status").json()
    total = body["sell_count"] + body["buy_count"] + body["hold_count"]
    assert total == 3  # MELI, GGAL, AL30


# ── GET /api/v1/intelligence/reallocation ─────────────────────────────────────

def test_reallocation_returns_200(client, db_session):
    _seed(db_session)
    assert client.get("/api/v1/intelligence/reallocation").status_code == 200


def test_reallocation_tiene_campos_requeridos(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/reallocation").json()
    assert "releasable_capital" in body
    assert "liquidity_level" in body
    assert "opportunities" in body
    assert "rotations" in body
    assert "suggested_action" in body


def test_reallocation_cartera_concentrada_tiene_capital_liberable(client, db_session):
    """Con MELI 60% y GGAL 30% → capital liberable > 0."""
    _seed(db_session)
    body = client.get("/api/v1/intelligence/reallocation").json()
    assert body["releasable_capital"] > 0


def test_reallocation_liquidity_level_valido(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/reallocation").json()
    assert body["liquidity_level"] in ("ALTA", "MEDIA", "BAJA")


def test_reallocation_suggested_action_no_vacia(client, db_session):
    _seed(db_session)
    body = client.get("/api/v1/intelligence/reallocation").json()
    assert isinstance(body["suggested_action"], str)
    assert len(body["suggested_action"]) > 0


def test_reallocation_db_vacia_retorna_valores_neutros(client):
    body = client.get("/api/v1/intelligence/reallocation").json()
    assert body["releasable_capital"] == 0.0
    assert body["opportunities"] == []
    assert body["rotations"] == []


def test_reallocation_cartera_diversificada_sin_capital_liberable(client, db_session):
    """Cartera equilibrada → releasable_capital == 0."""
    _seed_diversificada(db_session)
    body = client.get("/api/v1/intelligence/reallocation").json()
    assert body["releasable_capital"] == 0.0
