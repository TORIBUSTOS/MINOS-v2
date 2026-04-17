"""
Unified Ticker Layer: vista unificada de tickers entre carteras.
Regla: NO suma nominales entre carteras — rastrea presencia por cartera.
"""
from collections import defaultdict
from sqlalchemy.orm import Session

from src.models.portfolio import Portfolio
from src.models.position import Position


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
    for pos, port in rows:
        ticker_entries[pos.ticker].append({
            "portfolio": port.name,
            "quantity": pos.quantity,
            "valuation": pos.valuation,
        })

    return [
        {
            "ticker": ticker,
            "presence": len({e["portfolio"] for e in entries}),
            "entries": entries,
        }
        for ticker, entries in sorted(ticker_entries.items())
    ]
