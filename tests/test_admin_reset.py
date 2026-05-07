from datetime import date

from src.models.asset import Asset
from src.models.load_record import LoadRecord
from src.models.portfolio import Portfolio
from src.models.position import Position
from src.models.source import Source


def _seed_position(db_session, load_type: str) -> None:
    source = Source(name=f"{load_type}-source", type=load_type)
    db_session.add(source)
    db_session.flush()

    portfolio = Portfolio(name=f"{load_type}-portfolio", source_id=source.id)
    asset = Asset(ticker=f"{load_type.upper()}1", name=load_type, asset_type="unknown")
    db_session.add_all([portfolio, asset])
    db_session.flush()

    db_session.add(Position(
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        ticker=asset.ticker,
        quantity=1.0,
        currency="ARS",
        valuation=100.0,
        valuation_date=date(2024, 1, 1),
        load_type=load_type,
        validation_status="valid",
    ))
    db_session.add(LoadRecord(
        source_id=source.id,
        load_type=load_type,
        status="success",
        records_processed=1,
        records_rejected=0,
    ))
    db_session.commit()


def test_reset_uploaded_data_deletes_file_and_manual_only(client, db_session):
    for load_type in ("file", "manual", "api", "visual"):
        _seed_position(db_session, load_type)

    response = client.post("/api/v1/admin/reset-uploaded-data", json={"confirm": True})

    assert response.status_code == 200
    body = response.json()
    assert body["positions_deleted"] == 2
    assert body["load_records_deleted"] == 2

    remaining_positions = {
        p.load_type for p in db_session.query(Position).order_by(Position.load_type).all()
    }
    remaining_load_records = {
        r.load_type for r in db_session.query(LoadRecord).order_by(LoadRecord.load_type).all()
    }
    assert remaining_positions == {"api", "visual"}
    assert remaining_load_records == {"api", "visual"}


def test_reset_uploaded_data_preserves_catalog_entities(client, db_session):
    _seed_position(db_session, "file")

    response = client.post("/api/v1/admin/reset-uploaded-data", json={"confirm": True})

    assert response.status_code == 200
    assert db_session.query(Position).count() == 0
    assert db_session.query(Source).count() == 1
    assert db_session.query(Portfolio).count() == 1
    assert db_session.query(Asset).count() == 1


def test_reset_uploaded_data_requires_explicit_confirmation(client, db_session):
    _seed_position(db_session, "file")

    response = client.post("/api/v1/admin/reset-uploaded-data", json={"confirm": False})

    assert response.status_code == 400
    assert db_session.query(Position).count() == 1
