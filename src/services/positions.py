"""
Positions service: carga manual de posiciones individuales.
"""
from sqlalchemy.orm import Session

from src.models.portfolio import Portfolio
from src.models.position import Position
from src.models.source import Source
from src.schemas.position import PositionManualCreate, PositionRead
from src.services.ingestion import (
    _get_or_create_asset,
    _get_or_create_portfolio,
    _get_or_create_source,
)


def create_manual_position(db: Session, data: PositionManualCreate) -> Position:
    source = _get_or_create_source(db, data.source_name)
    portfolio = _get_or_create_portfolio(db, data.portfolio_name, source.id)
    asset = _get_or_create_asset(db, data.ticker)

    position = Position(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        ticker=data.ticker,
        quantity=data.quantity,
        currency=data.currency.upper(),
        valuation=data.valuation,
        valuation_date=data.valuation_date,
        load_type="manual",
        validation_status="valid",
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


def list_positions(
    db: Session,
    portfolio_name: str | None = None,
    source_name: str | None = None,
) -> list[Position]:
    query = db.query(Position)

    if portfolio_name:
        query = query.join(Portfolio).filter(Portfolio.name == portfolio_name)

    if source_name:
        if portfolio_name:
            # Portfolio join ya está aplicado
            query = query.join(Source, Portfolio.source_id == Source.id).filter(Source.name == source_name)
        else:
            query = (
                query.join(Portfolio)
                .join(Source, Portfolio.source_id == Source.id)
                .filter(Source.name == source_name)
            )

    return query.all()
