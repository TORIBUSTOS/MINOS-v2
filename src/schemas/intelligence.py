from pydantic import BaseModel


class TickerSignal(BaseModel):
    ticker: str
    signal: str
    reason: str
    pct: float


class PortfolioStatus(BaseModel):
    status: str
    insights: list[str]
    suggested_action: str
    sell_count: int
    buy_count: int
    hold_count: int


class ReallocationOpportunity(BaseModel):
    ticker: str
    current_pct: float
    suggested_action: str


class Rotation(BaseModel):
    from_ticker: str  # alias del campo "from" (reservada en Python)
    to: str
    amount: float
    reason: str

    model_config = {"populate_by_name": True}


class ReallocationSuggestion(BaseModel):
    releasable_capital: float
    liquidity_level: str
    opportunities: list[ReallocationOpportunity]
    rotations: list[Rotation]
    suggested_action: str
