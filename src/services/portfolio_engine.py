"""
Portfolio Engine: consolida posiciones de múltiples carteras/fuentes.
Retorna patrimonio total, distribución por activo, fuente y moneda.
"""
from collections import defaultdict
from sqlalchemy.orm import Session

from src.models.portfolio import Portfolio
from src.models.position import Position
from src.models.source import Source


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

    total = sum(pos.valuation for pos, _, _ in rows)

    # by_asset: suma valuaciones y rastrea portfolios
    asset_val: dict[str, float] = defaultdict(float)
    asset_portfolios: dict[str, set] = defaultdict(set)
    for pos, port, _ in rows:
        asset_val[pos.ticker] += pos.valuation
        asset_portfolios[pos.ticker].add(port.name)

    by_asset = [
        {
            "ticker": ticker,
            "valuation": val,
            "pct": round(val / total * 100, 4),
            "portfolios": sorted(asset_portfolios[ticker]),
        }
        for ticker, val in sorted(asset_val.items(), key=lambda x: -x[1])
    ]

    # by_source
    source_val: dict[str, float] = defaultdict(float)
    for pos, _, src in rows:
        source_val[src.name] += pos.valuation

    by_source = [
        {"source": src, "valuation": val, "pct": round(val / total * 100, 4)}
        for src, val in sorted(source_val.items(), key=lambda x: -x[1])
    ]

    # by_currency
    currency_val: dict[str, float] = defaultdict(float)
    for pos, _, _ in rows:
        currency_val[pos.currency] += pos.valuation

    by_currency = [
        {"currency": cur, "valuation": val, "pct": round(val / total * 100, 4)}
        for cur, val in sorted(currency_val.items(), key=lambda x: -x[1])
    ]

    return {
        "total_valuation": total,
        "by_asset": by_asset,
        "by_source": by_source,
        "by_currency": by_currency,
    }
