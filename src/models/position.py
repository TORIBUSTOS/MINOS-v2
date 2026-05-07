from datetime import date, datetime
from sqlalchemy import String, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)

    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    valuation: Mapped[float] = mapped_column(Float, nullable=False)
    valuation_date: Mapped[date] = mapped_column(Date, nullable=False)
    unit_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    cost_basis: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl_absolute: Mapped[float | None] = mapped_column(Float, nullable=True)
    pnl_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    dpt: Mapped[float | None] = mapped_column(Float, nullable=True)

    load_type: Mapped[str] = mapped_column(String(20), nullable=False)
    validation_status: Mapped[str] = mapped_column(String(20), default="pending")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="positions")
    asset: Mapped["Asset"] = relationship("Asset", back_populates="positions")
