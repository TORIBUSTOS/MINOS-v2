"""
BN-004: Tests de carga manual de posiciones.
Correr con: pytest tests/test_positions.py -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.main import app
from src.core.database import get_db
from src.models.base import Base
from src.models.source import Source
from src.models.portfolio import Portfolio
from src.models.position import Position
import src.models.asset       # noqa: F401 — needed for Base.metadata
import src.models.load_record  # noqa: F401 — needed for Base.metadata

# ── Fixtures ─────────────────────────────────────────────────────────────────

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
def client(db_engine):
    def override_get_db():
        with Session(db_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session


VALID_PAYLOAD = {
    "source_name": "Balanz",
    "portfolio_name": "Principal",
    "ticker": "GGAL",
    "quantity": 100.0,
    "currency": "ARS",
    "valuation": 1500.0,
    "valuation_date": "2024-01-15",
}

# ── POST /api/v1/positions ────────────────────────────────────────────────────

def test_create_position_returns_201(client):
    response = client.post("/api/v1/positions", json=VALID_PAYLOAD)
    assert response.status_code == 201


def test_create_position_response_contains_id_and_ticker(client):
    response = client.post("/api/v1/positions", json=VALID_PAYLOAD)
    body = response.json()
    assert "id" in body
    assert body["ticker"] == "GGAL"
    assert body["load_type"] == "manual"


def test_create_position_persists_to_db(client, db_session):
    client.post("/api/v1/positions", json=VALID_PAYLOAD)
    position = db_session.query(Position).first()
    assert position is not None
    assert position.ticker == "GGAL"
    assert position.quantity == 100.0


def test_create_position_load_type_is_always_manual(client, db_session):
    """load_type debe ser 'manual' independientemente de lo que envíe el cliente."""
    client.post("/api/v1/positions", json=VALID_PAYLOAD)
    position = db_session.query(Position).first()
    assert position.load_type == "manual"


def test_create_position_creates_source_and_portfolio(client, db_session):
    client.post("/api/v1/positions", json=VALID_PAYLOAD)
    source = db_session.query(Source).filter_by(name="Balanz").first()
    assert source is not None
    portfolio = db_session.query(Portfolio).filter_by(name="Principal").first()
    assert portfolio is not None
    assert portfolio.source_id == source.id


def test_create_position_reuses_existing_source_and_portfolio(client, db_session):
    """Dos cargas al mismo source/portfolio no duplican entidades."""
    client.post("/api/v1/positions", json=VALID_PAYLOAD)
    client.post("/api/v1/positions", json={**VALID_PAYLOAD, "ticker": "PAMP"})
    assert db_session.query(Source).filter_by(name="Balanz").count() == 1
    assert db_session.query(Portfolio).filter_by(name="Principal").count() == 1


def test_create_position_invalid_quantity_returns_422(client):
    response = client.post("/api/v1/positions", json={**VALID_PAYLOAD, "quantity": -10})
    assert response.status_code == 422


def test_create_position_zero_quantity_returns_422(client):
    response = client.post("/api/v1/positions", json={**VALID_PAYLOAD, "quantity": 0})
    assert response.status_code == 422


def test_create_position_empty_ticker_returns_422(client):
    response = client.post("/api/v1/positions", json={**VALID_PAYLOAD, "ticker": ""})
    assert response.status_code == 422


def test_create_position_missing_required_field_returns_422(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "ticker"}
    response = client.post("/api/v1/positions", json=payload)
    assert response.status_code == 422


# ── GET /api/v1/positions ─────────────────────────────────────────────────────

def test_list_positions_returns_empty_list_initially(client):
    response = client.get("/api/v1/positions")
    assert response.status_code == 200
    assert response.json() == []


def test_list_positions_returns_all_positions(client):
    client.post("/api/v1/positions", json=VALID_PAYLOAD)
    client.post("/api/v1/positions", json={**VALID_PAYLOAD, "ticker": "PAMP"})
    response = client.get("/api/v1/positions")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_positions_filter_by_portfolio(client):
    client.post("/api/v1/positions", json=VALID_PAYLOAD)
    client.post("/api/v1/positions", json={
        **VALID_PAYLOAD,
        "portfolio_name": "Conservadora",
        "ticker": "PAMP",
    })
    response = client.get("/api/v1/positions?portfolio_name=Principal")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ticker"] == "GGAL"


def test_list_positions_filter_by_source(client):
    client.post("/api/v1/positions", json=VALID_PAYLOAD)
    client.post("/api/v1/positions", json={
        **VALID_PAYLOAD,
        "source_name": "IOL",
        "ticker": "MSFT",
    })
    response = client.get("/api/v1/positions?source_name=IOL")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ticker"] == "MSFT"


def test_list_positions_each_item_has_expected_fields(client):
    client.post("/api/v1/positions", json=VALID_PAYLOAD)
    data = client.get("/api/v1/positions").json()
    item = data[0]
    for field in ("id", "ticker", "quantity", "currency", "valuation", "load_type"):
        assert field in item
