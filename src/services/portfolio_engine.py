"""
Portfolio Engine: consolida posiciones de múltiples carteras/fuentes.
Retorna patrimonio total, distribución por activo, fuente y moneda.
"""
from collections import defaultdict
from dataclasses import asdict
from decimal import Decimal, ROUND_HALF_UP
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
    trace = asdict(quote)
    trace.update(
        {
            "price": _to_float(quote.price) if quote.price is not None else None,
            "quantity": _to_float(quantity),
            "avg_cost": _to_float(avg_cost),
            "market_value": _to_float(market_value),
            "cost_basis": _to_float(cost_basis),
            "pnl_absolute": _to_float(pnl_absolute),
            "pnl_percentage": _to_float(pnl_percentage, TRACE_PCT_QUANT),
            "valuation_status": quote.status,
            "timestamp": quote.timestamp.isoformat() if quote.timestamp else None,
            "fetched_at": quote.fetched_at.isoformat(),
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
        "avg_cost": _to_float(_decimal(pos.avg_cost) if pos.avg_cost is not None else avg_cost),
        "market_value": _to_float(market_value),
        "cost_basis": _to_float(cost_basis),
        "pnl_absolute": _to_float(_decimal(pos.pnl_absolute) if pos.pnl_absolute is not None else market_value - cost_basis),
        "pnl_percentage": _to_float(_decimal(pos.pnl_percentage), TRACE_PCT_QUANT) if pos.pnl_percentage is not None else _to_float((market_value - cost_basis) / cost_basis * Decimal("100"), TRACE_PCT_QUANT) if cost_basis else 0.0,
    }


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
    for pos, port, _, valuation in valued_rows:
        asset_type = infer_asset_type(pos.ticker, pos.asset.asset_type if pos.asset else None)
        asset_val[pos.ticker] += valuation["market_value"]
        asset_cost[pos.ticker] += valuation["cost_basis"]
        asset_pnl[pos.ticker] += valuation["pnl_absolute"]
        asset_portfolios[pos.ticker].add(port.name)
        asset_traces[pos.ticker].append(valuation["trace"])
        asset_types[pos.ticker] = asset_type
        asset_underlyings[pos.ticker] = cedear_underlying(pos.ticker) if asset_type == "CEDEAR" else None

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
            "valuation_trace": asset_traces[ticker][0],
            "valuation_traces": asset_traces[ticker],
        }
        for ticker, val in sorted(asset_val.items(), key=lambda x: -x[1])
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

    return {
        "total_valuation": _to_float(total),
        "by_asset": by_asset,
        "by_source": by_source,
        "by_currency": by_currency,
    }
