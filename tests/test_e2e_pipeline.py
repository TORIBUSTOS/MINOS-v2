"""
E2E: flujo completo CSV → portfolio → intelligence.
Cubre el path crítico de MINOS de punta a punta sin mocks de negocio.
"""
import io
import pytest
from unittest.mock import patch, MagicMock


CSV_CONTENT = b"""ticker,cantidad,moneda,valuacion,fecha
GGAL,100,ARS,52000.00,2026-04-16
BMA,50,ARS,31500.00,2026-04-16
AAPL,10,USD,1750.00,2026-04-16
MSFT,5,USD,2100.50,2026-04-16
MELI,8,USD,14000.00,2026-04-16
"""


@pytest.fixture
def _mock_yf():
    """Silencia yfinance en todos los tests E2E."""
    mock_ticker = MagicMock()
    mock_ticker.fast_info = MagicMock()
    mock_ticker.fast_info.last_price = 100.0
    with patch("src.services.market_data.yf.Ticker", return_value=mock_ticker):
        yield


@pytest.fixture
def _loaded_client(client, _mock_yf):
    """Retorna un client con datos ya ingresados via CSV."""
    data = io.BytesIO(CSV_CONTENT)
    resp = client.post(
        "/api/v1/ingest/file",
        files={"file": ("test.csv", data, "text/csv")},
        data={"source_name": "TestBróker", "portfolio_name": "TestCartera"},
    )
    assert resp.status_code == 200, f"Upload falló: {resp.text}"
    return client


# ── Upload ─────────────────────────────────────────────────────────────────────

def test_upload_csv_creates_positions(_loaded_client):
    resp = _loaded_client.get("/api/v1/positions")
    assert resp.status_code == 200
    positions = resp.json()
    tickers = {p["ticker"] for p in positions}
    assert {"GGAL", "BMA", "AAPL", "MSFT", "MELI"} == tickers


def test_upload_returns_position_count(_loaded_client):
    resp = _loaded_client.get("/api/v1/positions")
    assert len(resp.json()) == 5


# ── Portfolio engine ───────────────────────────────────────────────────────────

def test_portfolio_summary_after_upload(_loaded_client):
    resp = _loaded_client.get("/api/v1/portfolio/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_valuation"] > 0
    assert len(data["by_asset"]) == 5
    assert len(data["by_source"]) == 1
    assert any(c["currency"] == "USD" for c in data["by_currency"])
    assert any(c["currency"] == "ARS" for c in data["by_currency"])


def test_portfolio_by_source_after_upload(_loaded_client):
    resp = _loaded_client.get("/api/v1/portfolio/by-source")
    assert resp.status_code == 200
    sources = resp.json()
    assert len(sources) == 1
    assert sources[0]["source"] == "TestBróker"


def test_unified_tickers_after_upload(_loaded_client):
    resp = _loaded_client.get("/api/v1/tickers/unified")
    assert resp.status_code == 200
    tickers = {t["ticker"] for t in resp.json()}
    assert "GGAL" in tickers
    assert "MELI" in tickers


# ── Intelligence layer ────────────────────────────────────────────────────────

def test_intelligence_signals_after_upload(_loaded_client):
    resp = _loaded_client.get("/api/v1/intelligence/signals")
    assert resp.status_code == 200
    data = resp.json()
    # API retorna lista de señales directamente
    assert isinstance(data, list)
    assert len(data) == 5
    for sig in data:
        assert sig["signal"] in ("STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL")
        assert "ticker" in sig
        assert "reason" in sig
        assert "pct" in sig


def test_portfolio_status_after_upload(_loaded_client):
    resp = _loaded_client.get("/api/v1/intelligence/portfolio-status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("EXPANSIÓN", "NEUTRAL", "RIESGO")
    assert isinstance(data["insights"], list)
    assert isinstance(data["suggested_action"], str)


def test_reallocation_after_upload(_loaded_client):
    resp = _loaded_client.get("/api/v1/intelligence/reallocation")
    assert resp.status_code == 200
    data = resp.json()
    assert "releasable_capital" in data
    assert "opportunities" in data
    assert "rotations" in data
    assert "suggested_action" in data
    assert data["releasable_capital"] >= 0


# ── Full pipeline integrity ───────────────────────────────────────────────────

def test_full_pipeline_consistency(_loaded_client):
    """Los conteos de señales en signals y portfolio-status deben coincidir."""
    signals_resp = _loaded_client.get("/api/v1/intelligence/signals")
    status_resp  = _loaded_client.get("/api/v1/intelligence/portfolio-status")

    signals = signals_resp.json()  # lista directa
    status  = status_resp.json()

    sell_count = sum(1 for s in signals if s["signal"] in ("SELL", "STRONG_SELL"))
    buy_count  = sum(1 for s in signals if s["signal"] in ("BUY",  "STRONG_BUY"))

    assert status["sell_count"] == sell_count
    assert status["buy_count"]  == buy_count


def test_pipeline_empty_db_returns_valid_structure(client, _mock_yf):
    """Con DB vacía, los endpoints de inteligencia devuelven estructura válida (no 500)."""
    for endpoint in [
        "/api/v1/intelligence/signals",
        "/api/v1/intelligence/portfolio-status",
        "/api/v1/intelligence/reallocation",
    ]:
        resp = client.get(endpoint)
        assert resp.status_code == 200, f"{endpoint} falló con {resp.status_code}"
