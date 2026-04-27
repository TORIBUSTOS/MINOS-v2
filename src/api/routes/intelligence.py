from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.intelligence import PortfolioStatus, ReallocationSuggestion, TickerSignal
from src.services.decision_engine import DecisionEngine
from src.services.intelligence import IntelligenceEngine
from src.services.portfolio_engine import consolidate
from src.services.reallocation import ReallocationEngine

router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence"])


@router.get("/signals", response_model=list[TickerSignal])
def get_signals(db: Session = Depends(get_db)):
    portfolio_data = consolidate(db)
    return IntelligenceEngine().evaluate_tickers(portfolio_data)


@router.get("/portfolio-status", response_model=PortfolioStatus)
def get_portfolio_status(db: Session = Depends(get_db)):
    portfolio_data = consolidate(db)
    return DecisionEngine().evaluate_portfolio(portfolio_data)


@router.get("/reallocation", response_model=ReallocationSuggestion)
def get_reallocation(db: Session = Depends(get_db)):
    portfolio_data = consolidate(db)
    raw = ReallocationEngine().suggest(portfolio_data)
    # Renombrar "from" → "from_ticker" para el schema Pydantic
    for rot in raw["rotations"]:
        rot["from_ticker"] = rot.pop("from")
    return raw
