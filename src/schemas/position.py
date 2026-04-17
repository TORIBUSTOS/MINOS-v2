from datetime import date
from typing import Literal
from pydantic import BaseModel, field_validator


LoadType = Literal["file", "manual", "api", "visual"]


class PositionCreate(BaseModel):
    portfolio_id: int
    asset_id: int
    ticker: str
    quantity: float
    currency: str
    valuation: float
    valuation_date: date
    load_type: LoadType

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class PositionManualCreate(BaseModel):
    """Schema para carga manual: el cliente provee source/portfolio por nombre."""
    source_name: str
    portfolio_name: str
    ticker: str
    quantity: float
    currency: str = "ARS"
    valuation: float
    valuation_date: date

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v

    @field_validator("ticker")
    @classmethod
    def ticker_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("ticker cannot be empty")
        return v.strip().upper()


class PositionRead(BaseModel):
    id: int
    portfolio_id: int
    asset_id: int
    ticker: str
    quantity: float
    currency: str
    valuation: float
    valuation_date: date
    load_type: str
    validation_status: str

    model_config = {"from_attributes": True}
