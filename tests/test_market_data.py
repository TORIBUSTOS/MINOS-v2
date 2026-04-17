"""
BN-007b: Tests del Market Data Service.
yfinance se mockea — nunca pega a Yahoo en tests.
Correr con: pytest tests/test_market_data.py -v
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.services.market_data import MarketDataService, PriceCache


@pytest.fixture(autouse=True)
def fresh_cache():
    """Limpia el cache singleton antes de cada test."""
    MarketDataService._cache.clear()
    yield
    MarketDataService._cache.clear()


def _mock_yfinance(prices: dict[str, float]):
    """Helper: mockea yf.Ticker para retornar precios dados."""
    def fake_ticker(symbol):
        mock = MagicMock()
        mock.fast_info.last_price = prices.get(symbol, 0.0)
        return mock
    return fake_ticker


# ── Consulta de precios ───────────────────────────────────────────────────────

def test_get_price_returns_value_from_yfinance():
    with patch("src.services.market_data.yf.Ticker", _mock_yfinance({"GGAL.BA": 450.0})):
        price = MarketDataService.get_price("GGAL.BA")
    assert price == 450.0


def test_get_price_caches_result():
    call_count = 0

    def counting_ticker(symbol):
        nonlocal call_count
        call_count += 1
        mock = MagicMock()
        mock.fast_info.last_price = 100.0
        return mock

    with patch("src.services.market_data.yf.Ticker", counting_ticker):
        MarketDataService.get_price("GGAL.BA")
        MarketDataService.get_price("GGAL.BA")  # segunda llamada — usa cache

    assert call_count == 1


def test_get_price_refreshes_after_ttl_expired():
    call_count = 0

    def counting_ticker(symbol):
        nonlocal call_count
        call_count += 1
        mock = MagicMock()
        mock.fast_info.last_price = 100.0
        return mock

    with patch("src.services.market_data.yf.Ticker", counting_ticker):
        MarketDataService.get_price("GGAL.BA")
        # Expirar cache manualmente
        MarketDataService._cache["GGAL.BA"] = PriceCache(
            price=100.0,
            fetched_at=datetime.now(timezone.utc) - timedelta(minutes=20),
        )
        MarketDataService.get_price("GGAL.BA")  # expirado → nuevo fetch

    assert call_count == 2


def test_get_price_fallback_when_yfinance_fails():
    """Si yfinance lanza excepción, retorna último precio conocido."""
    MarketDataService._cache["GGAL.BA"] = PriceCache(
        price=300.0,
        fetched_at=datetime.now(timezone.utc) - timedelta(minutes=20),  # expirado
    )

    def broken_ticker(symbol):
        raise ConnectionError("Yahoo no responde")

    with patch("src.services.market_data.yf.Ticker", broken_ticker):
        price = MarketDataService.get_price("GGAL.BA")

    assert price == 300.0  # fallback al último conocido


def test_get_price_returns_none_when_no_cache_and_yfinance_fails():
    def broken_ticker(symbol):
        raise ConnectionError("Yahoo no responde")

    with patch("src.services.market_data.yf.Ticker", broken_ticker):
        price = MarketDataService.get_price("GGAL.BA")

    assert price is None


def test_get_price_merval_ticker_with_ba_suffix():
    """Tickers MERVAL con .BA funcionan igual que US."""
    with patch("src.services.market_data.yf.Ticker", _mock_yfinance({"YPFD.BA": 35000.0})):
        price = MarketDataService.get_price("YPFD.BA")
    assert price == 35000.0


# ── Refresh batch ─────────────────────────────────────────────────────────────

def test_refresh_prices_updates_multiple_tickers():
    prices = {"GGAL.BA": 450.0, "AAPL": 180.0, "YPFD.BA": 35000.0}
    with patch("src.services.market_data.yf.Ticker", _mock_yfinance(prices)):
        result = MarketDataService.refresh_prices(["GGAL.BA", "AAPL", "YPFD.BA"])

    assert result["GGAL.BA"] == 450.0
    assert result["AAPL"] == 180.0
    assert result["YPFD.BA"] == 35000.0


def test_refresh_prices_returns_none_for_failed_tickers():
    def broken_ticker(symbol):
        raise ConnectionError()

    with patch("src.services.market_data.yf.Ticker", broken_ticker):
        result = MarketDataService.refresh_prices(["GGAL.BA"])

    assert result["GGAL.BA"] is None


def test_refresh_prices_bypasses_cache():
    """refresh_prices ignora el cache vigente y fuerza fetch."""
    MarketDataService._cache["GGAL.BA"] = PriceCache(
        price=100.0,
        fetched_at=datetime.now(timezone.utc),  # vigente
    )
    with patch("src.services.market_data.yf.Ticker", _mock_yfinance({"GGAL.BA": 999.0})):
        result = MarketDataService.refresh_prices(["GGAL.BA"])

    assert result["GGAL.BA"] == 999.0


# ── Cache snapshot ────────────────────────────────────────────────────────────

def test_get_all_cached_returns_current_cache():
    MarketDataService._cache["GGAL.BA"] = PriceCache(
        price=500.0,
        fetched_at=datetime.now(timezone.utc),
    )
    cached = MarketDataService.get_all_cached()
    assert "GGAL.BA" in cached
    assert cached["GGAL.BA"]["price"] == 500.0
    assert "fetched_at" in cached["GGAL.BA"]
    assert cached["GGAL.BA"]["expired"] is False


def test_get_all_cached_marks_expired_entries():
    MarketDataService._cache["GGAL.BA"] = PriceCache(
        price=500.0,
        fetched_at=datetime.now(timezone.utc) - timedelta(minutes=20),
    )
    cached = MarketDataService.get_all_cached()
    assert cached["GGAL.BA"]["expired"] is True
