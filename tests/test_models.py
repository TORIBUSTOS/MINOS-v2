"""
BN-002: Tests de modelos SQLAlchemy y schemas Pydantic.
Correr con: pytest tests/test_models.py -v
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.models.base import Base
from src.models.source import Source
from src.models.portfolio import Portfolio
from src.models.asset import Asset
from src.models.position import Position
from src.models.load_record import LoadRecord
from src.schemas.source import SourceCreate, SourceRead
from src.schemas.portfolio import PortfolioCreate, PortfolioRead
from src.schemas.asset import AssetCreate, AssetRead
from src.schemas.position import PositionCreate, PositionRead


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def db():
    """DB en memoria para tests — se destruye al finalizar."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


# ── Source ────────────────────────────────────────────────────────────────────

def test_source_creation(db):
    source = Source(name="Balanz", type="broker")
    db.add(source)
    db.commit()
    db.refresh(source)

    assert source.id is not None
    assert source.name == "Balanz"
    assert source.type == "broker"


def test_source_requires_name(db):
    with pytest.raises(Exception):
        source = Source(type="broker")
        db.add(source)
        db.flush()


# ── Portfolio ─────────────────────────────────────────────────────────────────

def test_portfolio_belongs_to_source(db):
    source = Source(name="IOL", type="broker")
    db.add(source)
    db.flush()

    portfolio = Portfolio(name="Cartera Principal", source_id=source.id)
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    assert portfolio.id is not None
    assert portfolio.source_id == source.id
    assert portfolio.source.name == "IOL"


def test_source_has_multiple_portfolios(db):
    source = Source(name="Balanz", type="broker")
    db.add(source)
    db.flush()

    p1 = Portfolio(name="ARS", source_id=source.id)
    p2 = Portfolio(name="USD", source_id=source.id)
    db.add_all([p1, p2])
    db.commit()
    db.refresh(source)

    assert len(source.portfolios) == 2


# ── Asset ─────────────────────────────────────────────────────────────────────

def test_asset_creation_with_unified_ticker(db):
    asset = Asset(ticker="AAPL", name="Apple Inc.", asset_type="equity")
    db.add(asset)
    db.commit()
    db.refresh(asset)

    assert asset.id is not None
    assert asset.ticker == "AAPL"


def test_asset_ticker_is_unique(db):
    a1 = Asset(ticker="AAPL", name="Apple Inc.", asset_type="equity")
    a2 = Asset(ticker="AAPL", name="Apple Duplicate", asset_type="equity")
    db.add(a1)
    db.flush()

    with pytest.raises(Exception):
        db.add(a2)
        db.flush()


# ── Position ──────────────────────────────────────────────────────────────────

def test_position_creation_with_all_fields(db):
    source = Source(name="Balanz", type="broker")
    db.add(source)
    db.flush()

    portfolio = Portfolio(name="Principal", source_id=source.id)
    db.add(portfolio)
    db.flush()

    asset = Asset(ticker="GGAL", name="Grupo Galicia", asset_type="equity")
    db.add(asset)
    db.flush()

    position = Position(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        ticker="GGAL",
        quantity=100.0,
        currency="ARS",
        valuation=50000.0,
        valuation_date=date(2026, 4, 16),
        load_type="file",
        validation_status="valid",
    )
    db.add(position)
    db.commit()
    db.refresh(position)

    assert position.id is not None
    assert position.ticker == "GGAL"
    assert position.quantity == 100.0
    assert position.portfolio.source.name == "Balanz"


def test_position_linked_to_portfolio_and_asset(db):
    source = Source(name="IOL", type="broker")
    db.add(source)
    db.flush()

    portfolio = Portfolio(name="Conservadora", source_id=source.id)
    db.add(portfolio)
    db.flush()

    asset = Asset(ticker="BMA", name="Banco Macro", asset_type="equity")
    db.add(asset)
    db.flush()

    position = Position(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        ticker="BMA",
        quantity=50.0,
        currency="ARS",
        valuation=25000.0,
        valuation_date=date(2026, 4, 16),
        load_type="manual",
        validation_status="valid",
    )
    db.add(position)
    db.commit()
    db.refresh(position)

    assert position.portfolio_id == portfolio.id
    assert position.asset_id == asset.id


# ── LoadRecord ────────────────────────────────────────────────────────────────

def test_load_record_tracks_ingestion(db):
    source = Source(name="Manual", type="manual")
    db.add(source)
    db.flush()

    record = LoadRecord(
        source_id=source.id,
        load_type="manual",
        status="success",
        records_processed=10,
        records_rejected=1,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    assert record.id is not None
    assert record.records_processed == 10
    assert record.records_rejected == 1
    assert record.status == "success"


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

def test_source_create_schema_validates():
    schema = SourceCreate(name="Balanz", type="broker")
    assert schema.name == "Balanz"


def test_source_create_schema_rejects_empty_name():
    with pytest.raises(Exception):
        SourceCreate(name="", type="broker")


def test_portfolio_create_schema_validates():
    schema = PortfolioCreate(name="Principal", source_id=1)
    assert schema.source_id == 1


def test_asset_create_schema_validates():
    schema = AssetCreate(ticker="AAPL", name="Apple Inc.", asset_type="equity")
    assert schema.ticker == "AAPL"


def test_position_create_schema_validates():
    schema = PositionCreate(
        portfolio_id=1,
        asset_id=1,
        ticker="GGAL",
        quantity=100.0,
        currency="ARS",
        valuation=50000.0,
        valuation_date=date(2026, 4, 16),
        load_type="file",
    )
    assert schema.ticker == "GGAL"
    assert schema.load_type == "file"


def test_position_create_schema_rejects_negative_quantity():
    with pytest.raises(Exception):
        PositionCreate(
            portfolio_id=1,
            asset_id=1,
            ticker="GGAL",
            quantity=-10.0,
            currency="ARS",
            valuation=50000.0,
            valuation_date=date(2026, 4, 16),
            load_type="file",
        )
