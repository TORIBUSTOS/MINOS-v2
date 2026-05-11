from uuid import uuid4

from sqlalchemy.orm import Session

from src.models.portfolio_snapshot import PortfolioSnapshot
from src.services.portfolio_engine import consolidate


VALID_SNAPSHOT_TRIGGERS = {
    "UPLOAD_CONFIRMED",
    "MANUAL_ENTRY",
    "MARKET_REFRESH",
    "MANUAL_SNAPSHOT",
}


def _clean_strings(values: list[str] | None) -> list[str]:
    if not values:
        return []
    return [str(value) for value in values if str(value).strip()]


def snapshot_to_dict(snapshot: PortfolioSnapshot) -> dict:
    return {
        "id": snapshot.id,
        "snapshot_id": snapshot.snapshot_id,
        "created_at": snapshot.created_at.isoformat(),
        "trigger": snapshot.trigger,
        "total_valuation": snapshot.total_valuation,
        "by_asset": snapshot.by_asset,
        "by_source": snapshot.by_source,
        "by_currency": snapshot.by_currency,
        "live_market": snapshot.live_market,
        "source_load_record_id": snapshot.source_load_record_id,
        "notes": snapshot.notes,
        "warnings": snapshot.warnings,
    }


def create_portfolio_snapshot(
    db: Session,
    trigger: str = "MANUAL_SNAPSHOT",
    source_load_record_id: int | None = None,
    notes: list[str] | None = None,
    warnings: list[str] | None = None,
    summary: dict | None = None,
) -> PortfolioSnapshot:
    if trigger not in VALID_SNAPSHOT_TRIGGERS:
        raise ValueError(f"trigger must be one of {sorted(VALID_SNAPSHOT_TRIGGERS)}")

    portfolio_summary = summary if summary is not None else consolidate(db)
    snapshot = PortfolioSnapshot(
        snapshot_id=str(uuid4()),
        trigger=trigger,
        total_valuation=float(portfolio_summary.get("total_valuation", 0.0)),
        by_asset=portfolio_summary.get("by_asset", []),
        by_source=portfolio_summary.get("by_source", []),
        by_currency=portfolio_summary.get("by_currency", []),
        live_market=portfolio_summary.get("live_market"),
        source_load_record_id=source_load_record_id,
        notes=_clean_strings(notes),
        warnings=_clean_strings(warnings),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def list_portfolio_snapshots(db: Session, limit: int = 20) -> list[PortfolioSnapshot]:
    safe_limit = max(1, min(limit, 100))
    return (
        db.query(PortfolioSnapshot)
        .order_by(PortfolioSnapshot.created_at.desc(), PortfolioSnapshot.id.desc())
        .limit(safe_limit)
        .all()
    )


def get_portfolio_snapshot(db: Session, snapshot_id: str) -> PortfolioSnapshot | None:
    return db.query(PortfolioSnapshot).filter_by(snapshot_id=snapshot_id).first()


def get_latest_portfolio_snapshot(db: Session) -> PortfolioSnapshot | None:
    return (
        db.query(PortfolioSnapshot)
        .order_by(PortfolioSnapshot.created_at.desc(), PortfolioSnapshot.id.desc())
        .first()
    )
