from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.portfolio import Portfolio
from src.models.position import Position
from src.services.portfolio_engine import consolidate

router = APIRouter(prefix="/api/v1", tags=["portfolio"])


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
            "position_count": db.query(Position).filter_by(portfolio_id=p.id).count(),
        }
        for p in portfolios
    ]
