from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.position import Position
from src.services.market_data import MarketDataService

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.post("/refresh")
def refresh_market_prices(db: Session = Depends(get_db)):
    """Fuerza refresh de precios para todos los tickers en cartera."""
    tickers = [row[0] for row in db.query(Position.ticker).distinct().all()]
    result = MarketDataService.refresh_prices(tickers)
    return {"refreshed": len(result), "prices": result}


@router.get("/prices")
def get_market_prices():
    """Retorna precios en cache con timestamp de última actualización."""
    return MarketDataService.get_all_cached()
