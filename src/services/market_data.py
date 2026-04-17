"""
Market Data Service: precios en vivo via yfinance con cache TTL.
- Soporta tickers US (AAPL, MELI) y MERVAL con sufijo .BA (GGAL.BA, YPFD.BA)
- Cache in-memory singleton con TTL configurable (default 15 min)
- Fallback: si Yahoo falla, retorna último precio conocido
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import yfinance as yf

DEFAULT_TTL_MINUTES = 15


@dataclass
class PriceCache:
    price: float
    fetched_at: datetime


class MarketDataService:
    _cache: dict[str, PriceCache] = {}
    _ttl_minutes: int = DEFAULT_TTL_MINUTES

    @classmethod
    def _is_expired(cls, entry: PriceCache) -> bool:
        return datetime.now(timezone.utc) - entry.fetched_at > timedelta(minutes=cls._ttl_minutes)

    @classmethod
    def get_price(cls, ticker: str) -> Optional[float]:
        """
        Retorna precio del ticker. Usa cache si vigente.
        Fallback: último precio conocido si yfinance falla.
        Retorna None si no hay cache y yfinance falla.
        """
        cached = cls._cache.get(ticker)
        if cached and not cls._is_expired(cached):
            return cached.price

        try:
            price = float(yf.Ticker(ticker).fast_info.last_price)
            cls._cache[ticker] = PriceCache(price=price, fetched_at=datetime.now(timezone.utc))
            return price
        except Exception:
            return cached.price if cached else None

    @classmethod
    def refresh_prices(cls, tickers: list[str]) -> dict[str, Optional[float]]:
        """Fuerza refresh de una lista de tickers ignorando el cache."""
        results: dict[str, Optional[float]] = {}
        for ticker in tickers:
            try:
                price = float(yf.Ticker(ticker).fast_info.last_price)
                cls._cache[ticker] = PriceCache(price=price, fetched_at=datetime.now(timezone.utc))
                results[ticker] = price
            except Exception:
                results[ticker] = None
        return results

    @classmethod
    def get_all_cached(cls) -> dict[str, dict]:
        """Retorna snapshot del cache actual con precios y timestamps."""
        return {
            ticker: {
                "price": entry.price,
                "fetched_at": entry.fetched_at.isoformat(),
                "expired": cls._is_expired(entry),
            }
            for ticker, entry in cls._cache.items()
        }
