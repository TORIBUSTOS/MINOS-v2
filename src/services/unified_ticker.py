"""
Unified Ticker Layer: vista unificada de tickers entre carteras.
Regla: NO suma nominales entre carteras — rastrea presencia por cartera.
"""
from collections import defaultdict
from sqlalchemy.orm import Session

from src.models.portfolio import Portfolio
from src.models.position import Position
from src.services.normalization import cedear_underlying, infer_asset_type


def unify(db: Session) -> list[dict]:
    """
    Retorna lista de tickers únicos con su presencia inter-cartera.

    Cada entrada:
    {
        "ticker": str,
        "presence": int,          # cuántas carteras distintas lo tienen
        "entries": [              # una entrada por cartera (sin sumar)
            {"portfolio": str, "quantity": float, "valuation": float}
        ]
    }
    """
    rows = (
        db.query(Position, Portfolio)
        .join(Portfolio, Position.portfolio_id == Portfolio.id)
        .all()
    )

    if not rows:
        return []

    # Agrupa por ticker manteniendo entradas individuales por cartera
    ticker_entries: dict[str, list[dict]] = defaultdict(list)
    ticker_types: dict[str, str] = {}
    ticker_underlyings: dict[str, str | None] = {}
    for pos, port in rows:
        asset_type = infer_asset_type(pos.ticker, pos.asset.asset_type if pos.asset else None)
        ticker_entries[pos.ticker].append({
            "portfolio": port.name,
            "quantity": pos.quantity,
            "valuation": pos.valuation,
        })
        ticker_types[pos.ticker] = asset_type
        ticker_underlyings[pos.ticker] = cedear_underlying(pos.ticker) if asset_type == "CEDEAR" else None

    return [
        {
            "ticker": ticker,
            "asset_type": ticker_types.get(ticker, "unknown"),
            "underlying": ticker_underlyings.get(ticker),
            "presence": len({e["portfolio"] for e in entries}),
            "entries": entries,
        }
        for ticker, entries in sorted(ticker_entries.items())
    ]
