from pydantic import BaseModel


class TickerSignal(BaseModel):
    ticker: str
    signal: str
    signal_status: str = "ACTIONABLE"
    is_actionable: bool = True
    valuation_status: str | None = None
    block_reason: str | None = None
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
    informed_liquidity: float | None = None
    available_capital: float = 0.0
    liquidity_level: str
    opportunities: list[ReallocationOpportunity]
    rotations: list[Rotation]
    suggested_action: str
