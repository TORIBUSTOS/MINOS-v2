"""
Fixtures y helpers compartidos para todos los tests de MINOS PRIME.
"""
import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.main import app
from src.core.database import get_db
from src.models.base import Base
from src.models.source import Source
from src.models.portfolio import Portfolio
from src.models.asset import Asset
from src.models.position import Position
import src.models.load_record  # noqa: F401 — needed for Base.metadata


# ── Engine / Session fixtures ─────────────────────────────────────────────────

@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session


@pytest.fixture
def client(db_engine):
    def override_get_db():
        with Session(db_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Seed helpers ──────────────────────────────────────────────────────────────

def make_source(db: Session, name: str, type: str = "file") -> Source:
    s = Source(name=name, type=type)
    db.add(s)
    db.flush()
    return s


def make_portfolio(db: Session, name: str, source: Source) -> Portfolio:
    p = Portfolio(name=name, source_id=source.id)
    db.add(p)
    db.flush()
    return p


def make_asset(db: Session, ticker: str) -> Asset:
    a = Asset(ticker=ticker, name=ticker, asset_type="unknown")
    db.add(a)
    db.flush()
    return a


def make_position(
    db: Session,
    portfolio: Portfolio,
    asset: Asset,
    ticker: str,
    quantity: float = 100.0,
    currency: str = "ARS",
    valuation: float = 1000.0,
    valuation_date: date = date(2024, 1, 15),
    load_type: str = "file",
) -> Position:
    p = Position(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        ticker=ticker,
        quantity=quantity,
        currency=currency,
        valuation=valuation,
        valuation_date=valuation_date,
        load_type=load_type,
        validation_status="valid",
    )
    db.add(p)
    db.flush()
    return p
