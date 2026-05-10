from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import yfinance as yf

DEFAULT_TTL_MINUTES = 15
SOURCE_YFINANCE = "yfinance"
STATUS_OK = "OK"
STATUS_CACHED = "CACHED"
STATUS_STALE = "STALE"
STATUS_FETCH_ERROR = "FETCH_ERROR"
FRESHNESS_LIVE = "LIVE"
FRESHNESS_CACHE = "CACHE"
FRESHNESS_STALE = "STALE"
FRESHNESS_UNAVAILABLE = "UNAVAILABLE"


def resolve_symbol(ticker: str, exchange: str | None = None, instrument_type: str | None = None) -> str:
    normalized = ticker.upper()
    if exchange == "BYMA" and instrument_type in {"EQUITY", "CEDEAR"}:
        return normalized if normalized.endswith(".BA") else f"{normalized}.BA"
    return normalized


@dataclass
class PriceCache:
    price: Decimal | float
    fetched_at: datetime
    currency: str = "USD"
    timestamp: datetime | None = None
    source: str = SOURCE_YFINANCE
    previous_close: Decimal | None = None


@dataclass
class PriceResult:
    input_ticker: str
    resolved_symbol: str
    source: str
    price: Decimal | None
    currency: str
    timestamp: datetime | None
    fetched_at: datetime
    instrument_type: str | None
    exchange: str | None
    quote_unit: str
    status: str
    is_stale: bool
    error: str | None
    previous_close: Decimal | None = None
    data_freshness: str = FRESHNESS_UNAVAILABLE
    market_state: str = FRESHNESS_UNAVAILABLE
    last_market_time: datetime | None = None


def _freshness_for_status(status: str, has_price: bool) -> str:
    if status == STATUS_OK and has_price:
        return FRESHNESS_LIVE
    if status == STATUS_CACHED and has_price:
        return FRESHNESS_CACHE
    if status == STATUS_STALE and has_price:
        return FRESHNESS_STALE
    return FRESHNESS_UNAVAILABLE


class MarketDataService:
    _cache: dict[str, PriceCache] = {}
    _ttl_minutes: int = DEFAULT_TTL_MINUTES

    @classmethod
    def _is_expired(cls, entry: PriceCache) -> bool:
        return datetime.now(timezone.utc) - entry.fetched_at > timedelta(minutes=cls._ttl_minutes)

    @staticmethod
    def _read_fast_info(fast_info: Any, key: str) -> Any:
        if isinstance(fast_info, dict):
            return fast_info.get(key)
        value = getattr(fast_info, key, None)
        return value if not callable(value) else value()

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        price = Decimal(str(value))
        if price <= Decimal("0"):
            raise ValueError("Price must be greater than zero")
        return price

    @staticmethod
    def _to_timestamp(value: Any, fallback: datetime) -> datetime:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        return fallback

    @staticmethod
    def _currency_for(resolved_symbol: str, exchange: str | None, fast_info: Any = None) -> str:
        raw_currency = MarketDataService._read_fast_info(fast_info, "currency") if fast_info is not None else None
        if isinstance(raw_currency, str) and raw_currency:
            return raw_currency
        if exchange == "BYMA" or resolved_symbol.endswith(".BA"):
            return "ARS"
        return "USD"

    @staticmethod
    def _cache_result(
        input_ticker: str,
        resolved_symbol: str,
        exchange: str | None,
        instrument_type: str | None,
        cache: PriceCache,
        status: str,
        is_stale: bool,
        error: str | None = None,
    ) -> PriceResult:
        freshness = _freshness_for_status(status, cache.price is not None)
        last_market_time = cache.timestamp or cache.fetched_at
        return PriceResult(
            input_ticker=input_ticker,
            resolved_symbol=resolved_symbol,
            source=cache.source,
            price=Decimal(str(cache.price)),
            currency=cache.currency,
            timestamp=cache.timestamp or cache.fetched_at,
            fetched_at=cache.fetched_at,
            instrument_type=instrument_type,
            exchange=exchange,
            quote_unit="PRICE",
            status=status,
            is_stale=is_stale,
            error=error,
            previous_close=cache.previous_close,
            data_freshness=freshness,
            market_state=freshness,
            last_market_time=last_market_time,
        )

    @classmethod
    def get_quote(
        cls,
        ticker: str,
        exchange: str | None = None,
        instrument_type: str | None = None,
    ) -> PriceResult:
        resolved_symbol = resolve_symbol(ticker, exchange, instrument_type)
        cached = cls._cache.get(resolved_symbol)
        if cached and not cls._is_expired(cached):
            return cls._cache_result(
                ticker,
                resolved_symbol,
                exchange,
                instrument_type,
                cached,
                STATUS_CACHED,
                False,
            )

        fetched_at = datetime.now(timezone.utc)
        try:
            ticker_data = yf.Ticker(resolved_symbol)
            fast_info = ticker_data.fast_info
            price = cls._to_decimal(cls._read_fast_info(fast_info, "last_price"))
            currency = cls._currency_for(resolved_symbol, exchange, fast_info)
            timestamp = cls._to_timestamp(
                cls._read_fast_info(fast_info, "last_trade_time")
                or cls._read_fast_info(fast_info, "last_price_time"),
                fetched_at,
            )
            raw_prev = cls._read_fast_info(fast_info, "previous_close")
            try:
                previous_close = cls._to_decimal(raw_prev) if raw_prev is not None else None
            except (ValueError, InvalidOperation):
                previous_close = None
            cls._cache[resolved_symbol] = PriceCache(
                price=price,
                fetched_at=fetched_at,
                currency=currency,
                timestamp=timestamp,
                previous_close=previous_close,
            )
            freshness = _freshness_for_status(STATUS_OK, True)
            return PriceResult(
                input_ticker=ticker,
                resolved_symbol=resolved_symbol,
                source=SOURCE_YFINANCE,
                price=price,
                currency=currency,
                timestamp=timestamp,
                fetched_at=fetched_at,
                instrument_type=instrument_type,
                exchange=exchange,
                quote_unit="PRICE",
                status=STATUS_OK,
                is_stale=False,
                error=None,
                previous_close=previous_close,
                data_freshness=freshness,
                market_state=freshness,
                last_market_time=timestamp,
            )
        except (Exception, InvalidOperation) as exc:
            if cached:
                return cls._cache_result(
                    ticker,
                    resolved_symbol,
                    exchange,
                    instrument_type,
                    cached,
                    STATUS_STALE,
                    True,
                    str(exc),
                )
            return PriceResult(
                input_ticker=ticker,
                resolved_symbol=resolved_symbol,
                source=SOURCE_YFINANCE,
                price=None,
                currency=cls._currency_for(resolved_symbol, exchange),
                timestamp=None,
                fetched_at=fetched_at,
                instrument_type=instrument_type,
                exchange=exchange,
                quote_unit="PRICE",
                status=STATUS_FETCH_ERROR,
                is_stale=False,
                error=str(exc),
                data_freshness=FRESHNESS_UNAVAILABLE,
                market_state=FRESHNESS_UNAVAILABLE,
                last_market_time=None,
            )

    @classmethod
    def get_price(
        cls,
        ticker: str,
        exchange: str | None = None,
        instrument_type: str | None = None,
    ) -> Optional[float]:
        """
        Retorna precio del ticker. Usa cache si vigente.
        Fallback: último precio conocido si yfinance falla.
        Retorna None si no hay cache y yfinance falla.
        """
        quote = cls.get_quote(ticker, exchange, instrument_type)
        return float(quote.price) if quote.price is not None else None

    @classmethod
    def refresh_prices(cls, tickers: list[str]) -> dict[str, Optional[float]]:
        """Fuerza refresh de una lista de tickers ignorando el cache."""
        results: dict[str, Optional[float]] = {}
        for ticker in tickers:
            cls._cache.pop(ticker, None)
            quote = cls.get_quote(ticker)
            results[ticker] = float(quote.price) if quote.price is not None else None
        return results

    @classmethod
    def refresh_quotes(cls, tickers: list[str]) -> dict[str, PriceResult]:
        """Fuerza refresh trazable de una lista de tickers ignorando el cache."""
        results: dict[str, PriceResult] = {}
        for ticker in tickers:
            resolved_symbol = resolve_symbol(ticker)
            cls._cache.pop(resolved_symbol, None)
            results[ticker] = cls.get_quote(ticker)
        return results

    @classmethod
    def refresh_quote_contexts(
        cls,
        contexts: list[tuple[str, str | None, str | None]],
    ) -> dict[str, PriceResult]:
        """Fuerza refresh con exchange/tipo de instrumento, preservando ticker de entrada."""
        results: dict[str, PriceResult] = {}
        for ticker, exchange, instrument_type in contexts:
            resolved_symbol = resolve_symbol(ticker, exchange, instrument_type)
            cls._cache.pop(resolved_symbol, None)
            results[ticker] = cls.get_quote(ticker, exchange=exchange, instrument_type=instrument_type)
        return results

    @classmethod
    def get_all_cached(cls) -> dict[str, dict]:
        """Retorna snapshot del cache actual con precios y timestamps."""
        snapshot = {}
        for ticker, entry in cls._cache.items():
            status = STATUS_STALE if cls._is_expired(entry) else STATUS_CACHED
            freshness = _freshness_for_status(status, entry.price is not None)
            last_market_time = entry.timestamp or entry.fetched_at
            snapshot[ticker] = {
                "price": entry.price,
                "fetched_at": entry.fetched_at.isoformat(),
                "currency": entry.currency,
                "timestamp": last_market_time.isoformat(),
                "last_market_time": last_market_time.isoformat(),
                "previous_close": entry.previous_close,
                "status": status,
                "data_freshness": freshness,
                "market_state": freshness,
                "expired": cls._is_expired(entry),
            }
        return snapshot
