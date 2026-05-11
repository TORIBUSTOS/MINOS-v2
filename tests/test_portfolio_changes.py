from src.services.portfolio_changes import compare_snapshots
from src.services.portfolio_snapshots import create_portfolio_snapshot


def _asset(
    ticker,
    quantity,
    market_value,
    signal="HOLD",
    data_freshness="CACHE",
    market_state="CLOSED",
):
    return {
        "ticker": ticker,
        "quantity": quantity,
        "market_value": market_value,
        "signal": signal,
        "data_freshness": data_freshness,
        "market_state": market_state,
    }


def _summary(assets):
    return {
        "total_valuation": sum(asset["market_value"] for asset in assets),
        "by_asset": assets,
        "by_source": [],
        "by_currency": [],
        "live_market": {
            "daily_pnl_total": 0.0,
            "freshness_summary": {},
            "last_market_time": None,
        },
    }


def _tickers(items):
    return {item["ticker"] for item in items}


def test_compare_snapshots_detects_portfolio_changes(db_session):
    previous = create_portfolio_snapshot(
        db_session,
        trigger="UPLOAD_CONFIRMED",
        summary=_summary(
            [
                _asset("BMA", 65, 706550, data_freshness="CACHE"),
                _asset("GGAL", 80, 494800, signal="HOLD"),
                _asset("SUPV", 80, 191920),
            ]
        ),
    )
    current = create_portfolio_snapshot(
        db_session,
        trigger="UPLOAD_CONFIRMED",
        summary=_summary(
            [
                _asset("BMA", 70, 760000, data_freshness="LIVE", market_state="OPEN"),
                _asset("GGAL", 80, 600000, signal="SELL"),
                _asset("PAMP", 100, 470250),
            ]
        ),
    )

    diff = compare_snapshots(previous, current)

    assert _tickers(diff["new_positions"]) == {"PAMP"}
    assert _tickers(diff["removed_positions"]) == {"SUPV"}
    assert diff["quantity_changes"][0]["ticker"] == "BMA"
    assert diff["quantity_changes"][0]["delta"] == 5
    assert _tickers(diff["valuation_changes"]) == {"BMA", "GGAL"}
    assert _tickers(diff["large_moves"]) == {"BMA", "GGAL"}
    assert diff["signal_changes"][0]["ticker"] == "GGAL"
    assert diff["freshness_changes"][0]["ticker"] == "BMA"
    assert diff["summary"]["change_count"] == 7
    assert diff["summary"]["severity_counts"]["ACTION"] == 5
    assert diff["summary"]["severity_counts"]["INFO"] == 1
    assert diff["summary"]["severity_counts"]["WARN"] == 1


def test_compare_snapshots_returns_empty_diff_when_unchanged(db_session):
    summary = _summary([_asset("BMA", 65, 706550)])
    previous = create_portfolio_snapshot(db_session, trigger="MANUAL_SNAPSHOT", summary=summary)
    current = create_portfolio_snapshot(db_session, trigger="MANUAL_SNAPSHOT", summary=summary)

    diff = compare_snapshots(previous, current)

    assert diff["summary"]["has_changes"] is False
    assert diff["summary"]["change_count"] == 0
    assert diff["new_positions"] == []
    assert diff["removed_positions"] == []
    assert diff["quantity_changes"] == []
    assert diff["valuation_changes"] == []
    assert diff["signal_changes"] == []
    assert diff["freshness_changes"] == []
    assert diff["large_moves"] == []


def test_api_latest_snapshot_diff_requires_two_snapshots(client, db_session):
    create_portfolio_snapshot(
        db_session,
        trigger="MANUAL_SNAPSHOT",
        summary=_summary([_asset("BMA", 65, 706550)]),
    )

    response = client.get("/api/v1/portfolio/snapshots/diff/latest")

    assert response.status_code == 404
    assert response.json()["detail"] == "At least two portfolio snapshots are required"


def test_api_latest_snapshot_diff_returns_changes(client, db_session):
    create_portfolio_snapshot(
        db_session,
        trigger="UPLOAD_CONFIRMED",
        summary=_summary([_asset("BMA", 65, 706550)]),
    )
    create_portfolio_snapshot(
        db_session,
        trigger="UPLOAD_CONFIRMED",
        summary=_summary([_asset("BMA", 70, 760000), _asset("PAMP", 100, 470250)]),
    )

    response = client.get("/api/v1/portfolio/snapshots/diff/latest")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["has_changes"] is True
    assert _tickers(body["new_positions"]) == {"PAMP"}
    assert body["quantity_changes"][0]["ticker"] == "BMA"


def test_api_snapshot_diff_by_ids(client, db_session):
    previous = create_portfolio_snapshot(
        db_session,
        trigger="UPLOAD_CONFIRMED",
        summary=_summary([_asset("BMA", 65, 706550), _asset("SUPV", 80, 191920)]),
    )
    current = create_portfolio_snapshot(
        db_session,
        trigger="UPLOAD_CONFIRMED",
        summary=_summary([_asset("BMA", 65, 706550)]),
    )

    response = client.get(
        "/api/v1/portfolio/snapshots/diff",
        params={
            "from_snapshot_id": previous.snapshot_id,
            "to_snapshot_id": current.snapshot_id,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert _tickers(body["removed_positions"]) == {"SUPV"}
    assert body["summary"]["from_snapshot_id"] == previous.snapshot_id
    assert body["summary"]["to_snapshot_id"] == current.snapshot_id
