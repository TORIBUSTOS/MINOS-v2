from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.position import Position
from src.services.portfolio_engine import _quote_context
from src.services.market_data import MarketDataService

router = APIRouter(prefix="/api/v1/market", tags=["market"])


@router.post("/refresh")
def refresh_market_prices(db: Session = Depends(get_db)):
    """Fuerza refresh de precios para todos los tickers en cartera."""
    contexts_by_ticker: dict[str, tuple[str, str | None, str | None]] = {}
    for position in db.query(Position).all():
        exchange, instrument_type = _quote_context(position)
        if instrument_type is not None:
            contexts_by_ticker[position.ticker] = (position.ticker, exchange, instrument_type)

    quotes = MarketDataService.refresh_quote_contexts(list(contexts_by_ticker.values()))
    prices = {
        ticker: float(quote.price) if quote.price is not None else None
        for ticker, quote in quotes.items()
    }
    return {"refreshed": len(prices), "prices": prices}


@router.get("/prices")
def get_market_prices():
    """Retorna precios en cache con timestamp de última actualización."""
    return MarketDataService.get_all_cached()
