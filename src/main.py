from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.admin import router as admin_router
from src.api.routes.ingest import router as ingest_router
from src.api.routes.intelligence import router as intelligence_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4400",
        "http://127.0.0.1:4400",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router)
app.include_router(positions_router)
app.include_router(market_router)
app.include_router(portfolio_router)
app.include_router(tickers_router)
app.include_router(intelligence_router)
app.include_router(admin_router)
