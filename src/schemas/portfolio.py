from pydantic import BaseModel


class PortfolioCreate(BaseModel):
    name: str
    source_id: int


class PortfolioRead(BaseModel):
    id: int
    name: str
    source_id: int

    model_config = {"from_attributes": True}
