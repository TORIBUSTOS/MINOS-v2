from pathlib import Path

from src.models.position import Position
from tests.conftest import make_asset, make_portfolio, make_position, make_source


FIXTURES = Path(__file__).parent / "fixtures"


def test_ingest_preview_contract_does_not_persist(client, db_session):
    csv_content = (FIXTURES / "sample_portfolio.csv").read_bytes()

    response = client.post(
        "/api/v1/ingest/preview",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["preview_id"]
    assert body["source_name"] == "Balanz"
    assert body["portfolio_name"] == "Principal"
    assert body["expires_at"]
    assert body["processed"] == 8
    assert body["rejected"] == 0
    assert body["can_confirm"] is True
    assert body["summary"]["detected"] == 8
    assert body["summary"]["actions"]["CREATE"] == 8
    assert body["detected_positions"][0]["action_hint"] == "CREATE"
    assert body["detected_positions"][0]["confidence"] == 1.0
    assert db_session.query(Position).count() == 0


def test_ingest_preview_marks_existing_file_positions_as_update(client, db_session):
    source = make_source(db_session, "BALANZ")
    portfolio = make_portfolio(db_session, "Principal", source)
    asset = make_asset(db_session, "GGAL")
    make_position(db_session, portfolio, asset, "GGAL")
    db_session.commit()
    csv_content = (FIXTURES / "sample_portfolio.csv").read_bytes()

    response = client.post(
        "/api/v1/ingest/preview",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    ggal = next(row for row in body["detected_positions"] if row["ticker"] == "GGAL")
    assert ggal["action_hint"] == "UPDATE"
    assert body["summary"]["actions"]["UPDATE"] == 1
    assert db_session.query(Position).count() == 1


def test_ingest_preview_returns_rejected_rows(client, db_session):
    csv_content = (FIXTURES / "sample_invalid_rows.csv").read_bytes()

    response = client.post(
        "/api/v1/ingest/preview",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("invalid.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["can_confirm"] is False
    assert body["processed"] == 2
    assert body["rejected"] == 3
    assert len(body["rejected_rows"]) == 3
    assert body["summary"]["actions"]["CREATE"] == 2
    assert db_session.query(Position).count() == 0
