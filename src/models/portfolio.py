from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    source: Mapped["Source"] = relationship("Source", back_populates="portfolios")
    positions: Mapped[list["Position"]] = relationship(
        "Position", back_populates="portfolio", cascade="all, delete-orphan"
    )
