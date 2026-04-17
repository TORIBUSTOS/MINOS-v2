from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    portfolios: Mapped[list["Portfolio"]] = relationship(
        "Portfolio", back_populates="source", cascade="all, delete-orphan"
    )
    load_records: Mapped[list["LoadRecord"]] = relationship(
        "LoadRecord", back_populates="source", cascade="all, delete-orphan"
    )
