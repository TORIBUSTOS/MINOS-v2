"""
Portfolio Engine: consolida posiciones de múltiples carteras/fuentes.
Retorna patrimonio total, distribución por activo, fuente y moneda.
"""
from collections import defaultdict
from dataclasses import asdict
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from sqlalchemy.orm import Session

from src.models.portfolio import Portfolio
from src.models.position import Position
from src.models.source import Source
from src.services.market_data import MarketDataService, PriceResult
from src.services.normalization import cedear_underlying, infer_asset_type


MONEY_QUANT = Decimal("0.01")
PCT_QUANT = Decimal("0.0001")
TRACE_PCT_QUANT = Decimal("0.01")
SUPPORTED_DYNAMIC_ASSET_TYPES = {"EQUITY", "CEDEAR"}
VALUATION_STATUS_NO_DYNAMIC_QUOTE = "NO_DYNAMIC_QUOTE"
FRESHNESS_UNAVAILABLE = "UNAVAILABLE"
MONEY_MARKET_KEYWORDS = ("MONEY", "MARKET", "LIQ", "LIQUIDEZ", "MM")
CASH_KEYWORDS = ("CASH", "CAJA", "EFECTIVO", "DISPONIBLE", "SALDO")


def _empty_live_market() -> dict:
    return {
        "daily_pnl_total": 0.0,
        "daily_pnl_pct": 0.0,
        "positive_count": 0,
        "negative_count": 0,
        "unchanged_count": 0,
        "unavailable_count": 0,
        "freshness_summary": {},
        "last_market_time": None,
    }


def _empty_liquidity_summary() -> dict:
    return {
        "is_informed": False,
        "total": 0.0,
        "pct": 0.0,
        "by_currency": [],
        "items": [],
        "available_after_reallocation": None,
        "status": "NOT_INFORMED",
    }


def _decimal(value) -> Decimal:
    return Decimal(str(value))


def _to_float(value: Decimal, quant: Decimal = MONEY_QUANT) -> float:
    return float(value.quantize(quant, rounding=ROUND_HALF_UP))


def _pct(part: Decimal, total: Decimal) -> float:
    if total == 0:
        return 0.0
    return _to_float(part / total * Decimal("100"), PCT_QUANT)


def _quote_context(pos: Position) -> tuple[str | None, str | None]:
    asset_type = infer_asset_type(
        pos.ticker,
        pos.asset.asset_type if pos.asset else None,
    )
    if asset_type not in SUPPORTED_DYNAMIC_ASSET_TYPES:
        return None, None
    if pos.currency == "ARS":
        return "BYMA", asset_type
    return None, asset_type


def _quote_trace(quote: PriceResult, quantity: Decimal, market_value: Decimal, cost_basis: Decimal) -> dict:
    avg_cost = cost_basis / quantity if quantity else Decimal("0")
    pnl_absolute = market_value - cost_basis
    pnl_percentage = (pnl_absolute / cost_basis * Decimal("100")) if cost_basis else Decimal("0")

    day_change: float | None = None
    day_change_pct: float | None = None
    day_impact: float | None = None
    if (
        quote.price is not None
        and quote.previous_close is not None
        and quote.previous_close > Decimal("0")
        and quantity > Decimal("0")
    ):
        dc = quote.price - quote.previous_close
        day_change = _to_float(dc)
        day_change_pct = _to_float(dc / quote.previous_close * Decimal("100"), TRACE_PCT_QUANT)
        day_impact = _to_float(dc * quantity)

    trace = asdict(quote)
    trace.update(
        {
            "price": _to_float(quote.price) if quote.price is not None else None,
            "previous_close": _to_float(quote.previous_close) if quote.previous_close is not None else None,
            "quantity": _to_float(quantity),
            "avg_cost": _to_float(avg_cost),
            "market_value": _to_float(market_value),
            "cost_basis": _to_float(cost_basis),
            "pnl_absolute": _to_float(pnl_absolute),
            "pnl_percentage": _to_float(pnl_percentage, TRACE_PCT_QUANT),
            "day_change": day_change,
            "day_change_pct": day_change_pct,
            "day_impact": day_impact,
            "daily_impact_status": "OK" if day_impact is not None else FRESHNESS_UNAVAILABLE,
            "valuation_status": quote.status,
            "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
            "fetched_at": quote.fetched_at.isoformat(),
            "last_market_time": quote.last_market_time.isoformat() if quote.last_market_time else None,
        }
    )
    return trace


def _fallback_trace(
    pos: Position,
    exchange: str | None,
    instrument_type: str | None,
    error: str | None = None,
    status: str = "FALLBACK_STORED_VALUATION",
) -> dict:
    quantity = _decimal(pos.quantity)
    cost_basis = _decimal(pos.cost_basis if pos.cost_basis is not None else pos.valuation)
    market_value = _decimal(pos.valuation)
    avg_cost = cost_basis / quantity if quantity else Decimal("0")
    return {
        "input_ticker": pos.ticker,
        "resolved_symbol": pos.ticker,
        "source": "stored_position",
        "price": None,
        "previous_close": None,
        "day_change": None,
        "day_change_pct": None,
        "day_impact": None,
        "daily_impact_status": FRESHNESS_UNAVAILABLE,
        "data_freshness": FRESHNESS_UNAVAILABLE,
        "market_state": FRESHNESS_UNAVAILABLE,
        "last_market_time": None,
        "currency": pos.currency,
        "timestamp": None,
        "fetched_at": None,
        "instrument_type": instrument_type,
        "exchange": exchange,
        "quote_unit": "PRICE",
        "status": status,
        "valuation_status": status,
        "is_stale": True,
        "error": error,
        "quantity": _to_float(quantity),
        "avg_cost": _to_float(avg_cost),  # always cost_basis / quantity — broker ppc column is unreliable
        "market_value": _to_float(market_value),
        "cost_basis": _to_float(cost_basis),
        "pnl_absolute": _to_float(market_value - cost_basis),
        "pnl_percentage": _to_float((market_value - cost_basis) / cost_basis * Decimal("100"), TRACE_PCT_QUANT) if cost_basis else 0.0,
    }


def _first_trace_value(traces: list[dict], key: str):
    return traces[0].get(key) if traces else None


def _sum_trace_money(traces: list[dict], key: str) -> Decimal | None:
    values = [trace.get(key) for trace in traces if trace.get(key) is not None]
    if not values:
        return None
    return sum((_decimal(value) for value in values), Decimal("0"))


def _latest_iso(values: list[str | None]) -> str | None:
    latest: datetime | None = None
    latest_raw: str | None = None
    for value in values:
        if not value:
            continue
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            continue
        if latest is None or parsed > latest:
            latest = parsed
            latest_raw = value
    return latest_raw


def _liquidity_kind(pos: Position, asset_type: str) -> str | None:
    normalized_type = (asset_type or "unknown").strip().upper()
    ticker = (pos.ticker or "").strip().upper()
    asset_name = (pos.asset.name if pos.asset else "") or ""
    label = f"{ticker} {asset_name}".upper()

    if normalized_type in {"CASH", "LIQUIDITY"}:
        return "CASH"
    if normalized_type in {"MONEY_MARKET", "MONEYMARKET"}:
        return "MONEY_MARKET"
    if normalized_type == "FUND" and any(keyword in label for keyword in MONEY_MARKET_KEYWORDS):
        return "MONEY_MARKET"
    if normalized_type in {"UNKNOWN", ""} and (
        ticker in {"ARS", "USD", "USDC", "USDT"} or any(keyword in label for keyword in CASH_KEYWORDS)
    ):
        return "CASH"
    return None


def _position_valuation(pos: Position) -> dict:
    quantity = _decimal(pos.quantity)
    cost_basis = _decimal(pos.cost_basis if pos.cost_basis is not None else pos.valuation)
    exchange, instrument_type = _quote_context(pos)

    if instrument_type is None:
        quote = None
        error = "dynamic quote unsupported for instrument"
        fallback_status = VALUATION_STATUS_NO_DYNAMIC_QUOTE
    else:
        try:
            quote = MarketDataService.get_quote(pos.ticker, exchange=exchange, instrument_type=instrument_type)
        except Exception as exc:
            quote = None
            error = str(exc)
            fallback_status = "FALLBACK_STORED_VALUATION"
        else:
            error = quote.error
            fallback_status = "FALLBACK_STORED_VALUATION"

    if quote and quote.price is not None:
        market_value = quantity * quote.price
        trace = _quote_trace(quote, quantity, market_value, cost_basis)
    else:
        market_value = _decimal(pos.valuation)
        trace = _fallback_trace(pos, exchange, instrument_type, error, fallback_status)

    pnl_absolute = _decimal(pos.pnl_absolute) if pos.pnl_absolute is not None else market_value - cost_basis
    pnl_percentage = (
        _decimal(pos.pnl_percentage)
        if pos.pnl_percentage is not None
        else (pnl_absolute / cost_basis * Decimal("100")) if cost_basis else Decimal("0")
    )
    return {
        "market_value": market_value,
        "cost_basis": cost_basis,
        "pnl_absolute": pnl_absolute,
        "pnl_percentage": pnl_percentage,
        "trace": trace,
    }


def consolidate(db: Session) -> dict:
    """
    Consolida todas las posiciones en una vista patrimonial total.

    Returns:
        {
            "total_valuation": float,
            "by_asset": [{"ticker", "valuation", "pct", "portfolios"}],
            "by_source": [{"source", "valuation", "pct"}],
            "by_currency": [{"currency", "valuation", "pct"}],
        }
    """
    rows = (
        db.query(Position, Portfolio, Source)
        .join(Portfolio, Position.portfolio_id == Portfolio.id)
        .join(Source, Portfolio.source_id == Source.id)
        .all()
    )

    if not rows:
        return {
            "total_valuation": 0.0,
            "by_asset": [],
            "by_source": [],
            "by_currency": [],
            "live_market": _empty_live_market(),
            "liquidity_summary": _empty_liquidity_summary(),
        }

    valued_rows = [
        (pos, port, src, _position_valuation(pos))
        for pos, port, src in rows
    ]

    total = sum((item["market_value"] for _, _, _, item in valued_rows), Decimal("0"))

    # by_asset: suma valuaciones y rastrea portfolios
    asset_val: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    asset_cost: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    asset_pnl: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    asset_portfolios: dict[str, set] = defaultdict(set)
    asset_traces: dict[str, list[dict]] = defaultdict(list)
    asset_types: dict[str, str] = {}
    asset_underlyings: dict[str, str | None] = {}
    asset_liquidity_kinds: dict[str, str | None] = {}
    asset_currencies: dict[str, set] = defaultdict(set)
    asset_sources: dict[str, set] = defaultdict(set)
    for pos, port, src, valuation in valued_rows:
        asset_type = infer_asset_type(pos.ticker, pos.asset.asset_type if pos.asset else None)
        asset_val[pos.ticker] += valuation["market_value"]
        asset_cost[pos.ticker] += valuation["cost_basis"]
        asset_pnl[pos.ticker] += valuation["pnl_absolute"]
        asset_portfolios[pos.ticker].add(port.name)
        asset_traces[pos.ticker].append(valuation["trace"])
        asset_types[pos.ticker] = asset_type
        asset_underlyings[pos.ticker] = cedear_underlying(pos.ticker) if asset_type == "CEDEAR" else None
        asset_liquidity_kinds[pos.ticker] = _liquidity_kind(pos, asset_type)
        asset_currencies[pos.ticker].add(pos.currency)
        asset_sources[pos.ticker].add(src.name)

    by_asset = [
        {
            "ticker": ticker,
            "asset_type": asset_types.get(ticker, "unknown"),
            "underlying": asset_underlyings.get(ticker),
            "valuation": _to_float(val),
            "market_value": _to_float(val),
            "cost_basis": _to_float(asset_cost[ticker]),
            "pnl_absolute": _to_float(asset_pnl[ticker]),
            "pnl_percentage": _to_float(
                asset_pnl[ticker] / asset_cost[ticker] * Decimal("100"),
                TRACE_PCT_QUANT,
            ) if asset_cost[ticker] else 0.0,
            "pct": _pct(val, total),
            "portfolio_weight": _pct(val, total),
            "portfolios": sorted(asset_portfolios[ticker]),
            "valuation_status": asset_traces[ticker][0]["valuation_status"],
            "day_change": _first_trace_value(asset_traces[ticker], "day_change"),
            "day_change_pct": _first_trace_value(asset_traces[ticker], "day_change_pct"),
            "day_impact": _to_float(day_impact) if day_impact is not None else None,
            "data_freshness": _first_trace_value(asset_traces[ticker], "data_freshness") or FRESHNESS_UNAVAILABLE,
            "market_state": _first_trace_value(asset_traces[ticker], "market_state") or FRESHNESS_UNAVAILABLE,
            "last_market_time": _latest_iso([trace.get("last_market_time") or trace.get("timestamp") for trace in asset_traces[ticker]]),
            "is_liquidity": asset_liquidity_kinds.get(ticker) is not None,
            "liquidity_kind": asset_liquidity_kinds.get(ticker),
            "valuation_trace": asset_traces[ticker][0],
            "valuation_traces": asset_traces[ticker],
        }
        for ticker, val, day_impact in (
            (ticker, val, _sum_trace_money(asset_traces[ticker], "day_impact"))
            for ticker, val in sorted(asset_val.items(), key=lambda x: -x[1])
        )
    ]

    # by_source
    source_val: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for _, _, src, valuation in valued_rows:
        source_val[src.name] += valuation["market_value"]

    by_source = [
        {"source": src, "valuation": _to_float(val), "pct": _pct(val, total)}
        for src, val in sorted(source_val.items(), key=lambda x: -x[1])
    ]

    # by_currency
    currency_val: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for pos, _, _, valuation in valued_rows:
        currency_val[pos.currency] += valuation["market_value"]

    by_currency = [
        {"currency": cur, "valuation": _to_float(val), "pct": _pct(val, total)}
        for cur, val in sorted(currency_val.items(), key=lambda x: -x[1])
    ]

    live_traces = [trace for traces in asset_traces.values() for trace in traces]
    daily_pnl = sum(
        (_decimal(trace["day_impact"]) for trace in live_traces if trace.get("day_impact") is not None),
        Decimal("0"),
    )
    freshness_summary: dict[str, int] = defaultdict(int)
    for trace in live_traces:
        freshness_summary[trace.get("data_freshness") or FRESHNESS_UNAVAILABLE] += 1

    positive_count = 0
    negative_count = 0
    unchanged_count = 0
    unavailable_count = 0
    for asset in by_asset:
        day_change = asset.get("day_change")
        if day_change is None:
            unavailable_count += 1
        elif day_change > 0:
            positive_count += 1
        elif day_change < 0:
            negative_count += 1
        else:
            unchanged_count += 1

    live_market = {
        "daily_pnl_total": _to_float(daily_pnl),
        "daily_pnl_pct": _pct(daily_pnl, total),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "unchanged_count": unchanged_count,
        "unavailable_count": unavailable_count,
        "freshness_summary": dict(freshness_summary),
        "last_market_time": _latest_iso([
            trace.get("last_market_time") or trace.get("timestamp")
            for trace in live_traces
        ]),
    }

    liquidity_items = [
        {
            "ticker": ticker,
            "asset_type": asset_types.get(ticker, "unknown"),
            "liquidity_kind": asset_liquidity_kinds[ticker],
            "valuation": _to_float(asset_val[ticker]),
            "pct": _pct(asset_val[ticker], total),
            "currencies": sorted(asset_currencies[ticker]),
            "sources": sorted(asset_sources[ticker]),
        }
        for ticker in sorted(asset_val, key=lambda key: -asset_val[key])
        if asset_liquidity_kinds.get(ticker) is not None
    ]
    liquidity_total = sum(
        (_decimal(item["valuation"]) for item in liquidity_items),
        Decimal("0"),
    )
    liquidity_currency_val: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for pos, _, _, valuation in valued_rows:
        asset_type = infer_asset_type(pos.ticker, pos.asset.asset_type if pos.asset else None)
        if _liquidity_kind(pos, asset_type) is not None:
            liquidity_currency_val[pos.currency] += valuation["market_value"]
    liquidity_summary = (
        {
            "is_informed": True,
            "total": _to_float(liquidity_total),
            "pct": _pct(liquidity_total, total),
            "by_currency": [
                {"currency": cur, "valuation": _to_float(val), "pct": _pct(val, liquidity_total)}
                for cur, val in sorted(liquidity_currency_val.items(), key=lambda x: -x[1])
            ],
            "items": liquidity_items,
            "available_after_reallocation": None,
            "status": "INFORMED",
        }
        if liquidity_items
        else _empty_liquidity_summary()
    )

    return {
        "total_valuation": _to_float(total),
        "by_asset": by_asset,
        "by_source": by_source,
        "by_currency": by_currency,
        "live_market": live_market,
        "liquidity_summary": liquidity_summary,
    }
