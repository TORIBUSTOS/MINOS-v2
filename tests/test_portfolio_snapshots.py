import pytest

from src.models.portfolio_snapshot import PortfolioSnapshot
from src.services.portfolio_snapshots import (
    create_portfolio_snapshot,
    get_latest_portfolio_snapshot,
    snapshot_to_dict,
)
from tests.conftest import make_asset, make_portfolio, make_position, make_source


def test_create_portfolio_snapshot_from_consolidated_summary(db_session):
    source = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", source)
    asset = make_asset(db_session, "XYZTEST")
    make_position(db_session, portfolio, asset, "XYZTEST", quantity=10, valuation=1500)
    db_session.commit()

    snapshot = create_portfolio_snapshot(
        db_session,
        trigger="MANUAL_SNAPSHOT",
        notes=["baseline"],
    )

    assert snapshot.snapshot_id
    assert snapshot.trigger == "MANUAL_SNAPSHOT"
    assert snapshot.total_valuation == 1500.0
    assert snapshot.by_asset[0]["ticker"] == "XYZTEST"
    assert snapshot.by_source[0]["source"] == "Balanz"
    assert snapshot.by_currency[0]["currency"] == "ARS"
    assert snapshot.notes == ["baseline"]
    assert db_session.query(PortfolioSnapshot).count() == 1


def test_create_portfolio_snapshot_with_empty_portfolio(db_session):
    snapshot = create_portfolio_snapshot(db_session, trigger="MANUAL_SNAPSHOT")
    body = snapshot_to_dict(snapshot)

    assert body["total_valuation"] == 0.0
    assert body["by_asset"] == []
    assert body["by_source"] == []
    assert body["by_currency"] == []
    assert body["live_market"]["daily_pnl_total"] == 0.0


def test_create_portfolio_snapshot_rejects_invalid_trigger(db_session):
    with pytest.raises(ValueError):
        create_portfolio_snapshot(db_session, trigger="BROKER_MAGIC")


def test_latest_portfolio_snapshot_returns_newest(db_session):
    first = create_portfolio_snapshot(db_session, trigger="MANUAL_SNAPSHOT", notes=["first"])
    second = create_portfolio_snapshot(db_session, trigger="MARKET_REFRESH", notes=["second"])

    latest = get_latest_portfolio_snapshot(db_session)

    assert first.id != second.id
    assert latest is not None
    assert latest.snapshot_id == second.snapshot_id


def test_api_create_and_read_portfolio_snapshot(client, db_session):
    source = make_source(db_session, "Balanz")
    portfolio = make_portfolio(db_session, "Principal", source)
    asset = make_asset(db_session, "ZZZTEST")
    make_position(db_session, portfolio, asset, "ZZZTEST", quantity=5, valuation=2500)
    db_session.commit()

    create_response = client.post(
        "/api/v1/portfolio/snapshots",
        json={"trigger": "UPLOAD_CONFIRMED", "notes": ["after import"]},
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["snapshot_id"]
    assert created["trigger"] == "UPLOAD_CONFIRMED"
    assert created["total_valuation"] == 2500.0
    assert created["notes"] == ["after import"]

    latest_response = client.get("/api/v1/portfolio/snapshots/latest")
    assert latest_response.status_code == 200
    assert latest_response.json()["snapshot_id"] == created["snapshot_id"]

    detail_response = client.get(f"/api/v1/portfolio/snapshots/{created['snapshot_id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["by_asset"][0]["ticker"] == "ZZZTEST"

    list_response = client.get("/api/v1/portfolio/snapshots")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_api_latest_snapshot_returns_404_when_empty(client):
    response = client.get("/api/v1/portfolio/snapshots/latest")

    assert response.status_code == 404
