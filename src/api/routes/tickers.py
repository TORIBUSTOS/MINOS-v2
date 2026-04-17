from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.unified_ticker import unify

router = APIRouter(prefix="/api/v1/tickers", tags=["tickers"])


@router.get("/unified")
def tickers_unified(db: Session = Depends(get_db)):
    return unify(db)
