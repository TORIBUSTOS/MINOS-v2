from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from src.models.portfolio_snapshot import PortfolioSnapshot
from src.services.portfolio_snapshots import get_portfolio_snapshot, list_portfolio_snapshots, snapshot_to_dict


Severity = str


@dataclass(frozen=True)
class AssetState:
    ticker: str
    quantity: float | None
    valuation: float
    signal: str | None
    data_freshness: str | None
    market_state: str | None
    raw: dict[str, Any]


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _asset_quantity(asset: dict[str, Any]) -> float | None:
    direct = _as_float(asset.get("quantity"))
    if direct is not None:
        return direct

    traces = asset.get("valuation_traces")
    if isinstance(traces, list):
        quantities = [_as_float(trace.get("quantity")) for trace in traces if isinstance(trace, dict)]
        valid = [quantity for quantity in quantities if quantity is not None]
        if valid:
            return sum(valid)

    trace = asset.get("valuation_trace")
    if isinstance(trace, dict):
        return _as_float(trace.get("quantity"))

    return None


def _asset_valuation(asset: dict[str, Any]) -> float:
    return _as_float(asset.get("market_value")) or _as_float(asset.get("valuation")) or 0.0


def _asset_map(snapshot: PortfolioSnapshot) -> dict[str, AssetState]:
    assets: dict[str, AssetState] = {}
    for asset in snapshot.by_asset or []:
        ticker = str(asset.get("ticker", "")).strip().upper()
        if not ticker:
            continue
        assets[ticker] = AssetState(
            ticker=ticker,
            quantity=_asset_quantity(asset),
            valuation=_asset_valuation(asset),
            signal=asset.get("signal"),
            data_freshness=asset.get("data_freshness"),
            market_state=asset.get("market_state"),
            raw=asset,
        )
    return assets


def _pct_change(before: float, after: float) -> float | None:
    if before == 0:
        return None
    return (after - before) / before * 100


def _change_item(
    ticker: str,
    change_type: str,
    severity: Severity,
    before: Any,
    after: Any,
    reason: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item = {
        "ticker": ticker,
        "change_type": change_type,
        "severity": severity,
        "before": before,
        "after": after,
        "reason": reason,
    }
    if extra:
        item.update(extra)
    return item


def compare_snapshots(
    previous: PortfolioSnapshot,
    current: PortfolioSnapshot,
    large_move_pct_threshold: float = 5.0,
) -> dict[str, Any]:
    previous_assets = _asset_map(previous)
    current_assets = _asset_map(current)
    previous_tickers = set(previous_assets)
    current_tickers = set(current_assets)
    shared_tickers = sorted(previous_tickers & current_tickers)

    new_positions = [
        _change_item(
            ticker,
            "NEW_POSITION",
            "INFO",
            None,
            current_assets[ticker].raw,
            "Posicion nueva contra el snapshot anterior",
        )
        for ticker in sorted(current_tickers - previous_tickers)
    ]
    removed_positions = [
        _change_item(
            ticker,
            "REMOVED_POSITION",
            "ACTION",
            previous_assets[ticker].raw,
            None,
            "Posicion presente antes y ausente en el snapshot actual",
        )
        for ticker in sorted(previous_tickers - current_tickers)
    ]

    quantity_changes = []
    valuation_changes = []
    signal_changes = []
    freshness_changes = []
    large_moves = []

    for ticker in shared_tickers:
        before = previous_assets[ticker]
        after = current_assets[ticker]

        if before.quantity is not None and after.quantity is not None:
            quantity_delta = after.quantity - before.quantity
            if abs(quantity_delta) > 0.000001:
                quantity_changes.append(
                    _change_item(
                        ticker,
                        "QUANTITY_CHANGE",
                        "ACTION",
                        before.quantity,
                        after.quantity,
                        "Cambio de nominales detectado",
                        {"delta": quantity_delta},
                    )
                )

        valuation_delta = after.valuation - before.valuation
        if abs(valuation_delta) >= 0.01:
            pct = _pct_change(before.valuation, after.valuation)
            severity = "WARN" if pct is None or abs(pct) < large_move_pct_threshold else "ACTION"
            item = _change_item(
                ticker,
                "VALUATION_CHANGE",
                severity,
                before.valuation,
                after.valuation,
                "Cambio de valuacion detectado",
                {"delta": valuation_delta, "pct_change": pct},
            )
            valuation_changes.append(item)
            if pct is None or abs(pct) >= large_move_pct_threshold:
                large_moves.append({**item, "change_type": "LARGE_MOVE"})

        if before.signal and after.signal and before.signal != after.signal:
            signal_changes.append(
                _change_item(
                    ticker,
                    "SIGNAL_CHANGE",
                    "ACTION",
                    before.signal,
                    after.signal,
                    "Cambio de senal detectado",
                )
            )

        if before.data_freshness != after.data_freshness or before.market_state != after.market_state:
            freshness_changes.append(
                _change_item(
                    ticker,
                    "FRESHNESS_CHANGE",
                    "WARN",
                    {"data_freshness": before.data_freshness, "market_state": before.market_state},
                    {"data_freshness": after.data_freshness, "market_state": after.market_state},
                    "Cambio de frescura de mercado detectado",
                )
            )

    all_changes = (
        new_positions
        + removed_positions
        + quantity_changes
        + valuation_changes
        + signal_changes
        + freshness_changes
    )
    severity_counts = {"INFO": 0, "WARN": 0, "ACTION": 0}
    for item in all_changes:
        severity_counts[item["severity"]] += 1

    total_delta = current.total_valuation - previous.total_valuation
    summary = {
        "from_snapshot_id": previous.snapshot_id,
        "to_snapshot_id": current.snapshot_id,
        "from_created_at": previous.created_at.isoformat(),
        "to_created_at": current.created_at.isoformat(),
        "total_valuation_before": previous.total_valuation,
        "total_valuation_after": current.total_valuation,
        "total_valuation_delta": total_delta,
        "total_valuation_pct_change": _pct_change(previous.total_valuation, current.total_valuation),
        "change_count": len(all_changes),
        "severity_counts": severity_counts,
        "has_changes": bool(all_changes),
    }

    return {
        "from_snapshot": snapshot_to_dict(previous),
        "to_snapshot": snapshot_to_dict(current),
        "new_positions": new_positions,
        "removed_positions": removed_positions,
        "quantity_changes": quantity_changes,
        "valuation_changes": valuation_changes,
        "signal_changes": signal_changes,
        "freshness_changes": freshness_changes,
        "large_moves": large_moves,
        "summary": summary,
    }


def compare_latest_snapshots(db: Session) -> dict[str, Any] | None:
    snapshots = list_portfolio_snapshots(db, limit=2)
    if len(snapshots) < 2:
        return None
    current, previous = snapshots[0], snapshots[1]
    return compare_snapshots(previous, current)


def compare_snapshot_ids(db: Session, from_snapshot_id: str, to_snapshot_id: str) -> dict[str, Any] | None:
    previous = get_portfolio_snapshot(db, from_snapshot_id)
    current = get_portfolio_snapshot(db, to_snapshot_id)
    if previous is None or current is None:
        return None
    return compare_snapshots(previous, current)
