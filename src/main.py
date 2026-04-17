from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.routes.ingest import router as ingest_router
from src.api.routes.market import router as market_router
from src.api.routes.portfolio import router as portfolio_router
from src.api.routes.positions import router as positions_router
from src.api.routes.tickers import router as tickers_router
from src.core.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="MINOS PRIME", version="0.1.0", lifespan=lifespan)

app.include_router(ingest_router)
app.include_router(positions_router)
app.include_router(market_router)
app.include_router(portfolio_router)
app.include_router(tickers_router)
