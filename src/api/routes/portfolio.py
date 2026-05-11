from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.portfolio import Portfolio
from src.models.position import Position
from src.services.portfolio_engine import consolidate
from src.services.portfolio_snapshots import (
    create_portfolio_snapshot,
    get_latest_portfolio_snapshot,
    get_portfolio_snapshot,
    list_portfolio_snapshots,
    snapshot_to_dict,
)

router = APIRouter(prefix="/api/v1", tags=["portfolio"])


class PortfolioSnapshotCreateRequest(BaseModel):
    trigger: str = "MANUAL_SNAPSHOT"
    source_load_record_id: int | None = None
    notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


@router.get("/portfolio/summary")
def portfolio_summary(db: Session = Depends(get_db)):
    return consolidate(db)


@router.get("/portfolio/by-source")
def portfolio_by_source(db: Session = Depends(get_db)):
    return consolidate(db)["by_source"]


@router.get("/portfolio/by-currency")
def portfolio_by_currency(db: Session = Depends(get_db)):
    return consolidate(db)["by_currency"]


@router.get("/portfolios")
def list_portfolios(db: Session = Depends(get_db)):
    portfolios = db.query(Portfolio).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "source_id": p.source_id,
            "source_name": p.source.name if p.source else None,
            "position_count": db.query(Position).filter_by(portfolio_id=p.id).count(),
        }
        for p in portfolios
    ]


@router.post("/portfolio/snapshots")
def create_snapshot(payload: PortfolioSnapshotCreateRequest, db: Session = Depends(get_db)):
    try:
        snapshot = create_portfolio_snapshot(
            db,
            trigger=payload.trigger,
            source_load_record_id=payload.source_load_record_id,
            notes=payload.notes,
            warnings=payload.warnings,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return snapshot_to_dict(snapshot)


@router.get("/portfolio/snapshots")
def portfolio_snapshots(limit: int = 20, db: Session = Depends(get_db)):
    return [
        snapshot_to_dict(snapshot)
        for snapshot in list_portfolio_snapshots(db, limit=limit)
    ]


@router.get("/portfolio/snapshots/latest")
def latest_portfolio_snapshot(db: Session = Depends(get_db)):
    snapshot = get_latest_portfolio_snapshot(db)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="No portfolio snapshots found")
    return snapshot_to_dict(snapshot)


@router.get("/portfolio/snapshots/{snapshot_id}")
def portfolio_snapshot(snapshot_id: str, db: Session = Depends(get_db)):
    snapshot = get_portfolio_snapshot(db, snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Portfolio snapshot not found")
    return snapshot_to_dict(snapshot)
