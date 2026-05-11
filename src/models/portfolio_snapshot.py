from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    trigger: Mapped[str] = mapped_column(String(40), nullable=False)
    total_valuation: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    by_asset: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    by_source: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    by_currency: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    live_market: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    source_load_record_id: Mapped[int | None] = mapped_column(ForeignKey("load_records.id"), nullable=True)
    notes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    warnings: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
