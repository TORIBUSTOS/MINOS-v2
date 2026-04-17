"""
BN-003: Tests de ingestion CSV/Excel.
Correr con: pytest tests/test_ingestion.py -v
"""
import pytest
from pathlib import Path
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
import src.models.asset  # noqa: F401 — needed for Base.metadata
import src.models.load_record  # noqa: F401 — needed for Base.metadata

FIXTURES = Path(__file__).parent / "fixtures"


# ── Test DB override ──────────────────────────────────────────────────────────

@pytest.fixture
def db_engine():
    # StaticPool: mismo connection en todos los threads — requerido para SQLite in-memory con FastAPI
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


# ── Tests de ingestion CSV ────────────────────────────────────────────────────

def test_ingest_csv_returns_processed_count(client):
    csv_content = (FIXTURES / "sample_portfolio.csv").read_bytes()
    response = client.post(
        "/api/v1/ingest/file",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["processed"] == 8
    assert body["rejected"] == 0


def test_ingest_csv_creates_source_and_portfolio(client, db_session):
    csv_content = (FIXTURES / "sample_portfolio.csv").read_bytes()
    client.post(
        "/api/v1/ingest/file",
        data={"source_name": "IOL", "portfolio_name": "Conservadora"},
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    source = db_session.query(Source).filter_by(name="IOL").first()
    assert source is not None

    portfolio = db_session.query(Portfolio).filter_by(name="Conservadora").first()
    assert portfolio is not None
    assert portfolio.source_id == source.id


def test_ingest_csv_persists_positions(client, db_session):
    csv_content = (FIXTURES / "sample_portfolio.csv").read_bytes()
    client.post(
        "/api/v1/ingest/file",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    positions = db_session.query(Position).all()
    assert len(positions) == 8
    tickers = {p.ticker for p in positions}
    assert "GGAL" in tickers
    assert "AAPL" in tickers


def test_ingest_rejects_invalid_rows_without_persisting_them(client, db_session):
    csv_content = (FIXTURES / "sample_invalid_rows.csv").read_bytes()
    response = client.post(
        "/api/v1/ingest/file",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("invalid.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    # 5 rows: 2 valid (GGAL + PAMP), 3 invalid (no ticker, negative qty, non-numeric qty)
    assert body["processed"] == 2
    assert body["rejected"] == 3
    assert len(body["warnings"]) == 3

    positions = db_session.query(Position).all()
    assert len(positions) == 2


def test_ingest_never_persists_without_validation(client, db_session):
    """Si todos los rows son inválidos, la DB no cambia."""
    bad_csv = b"ticker,cantidad,moneda,valuacion,fecha\n,abc,,xyz,bad-date\n"
    response = client.post(
        "/api/v1/ingest/file",
        data={"source_name": "Test", "portfolio_name": "Test"},
        files={"file": ("bad.csv", bad_csv, "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["processed"] == 0
    assert db_session.query(Position).count() == 0


def test_ingest_reuses_existing_source_and_portfolio(client, db_session):
    """Dos cargas al mismo source/portfolio acumulan posiciones."""
    csv_content = (FIXTURES / "sample_portfolio.csv").read_bytes()
    client.post(
        "/api/v1/ingest/file",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("s1.csv", csv_content, "text/csv")},
    )
    client.post(
        "/api/v1/ingest/file",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("s2.csv", csv_content, "text/csv")},
    )
    # Source y Portfolio no se duplican
    assert db_session.query(Source).filter_by(name="Balanz").count() == 1
    assert db_session.query(Portfolio).filter_by(name="Principal").count() == 1


def test_ingest_unsupported_format_returns_400(client):
    response = client.post(
        "/api/v1/ingest/file",
        data={"source_name": "X", "portfolio_name": "Y"},
        files={"file": ("data.txt", b"not,a,spreadsheet", "text/plain")},
    )
    assert response.status_code == 400
