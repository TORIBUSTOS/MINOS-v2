from pydantic import BaseModel


class AssetCreate(BaseModel):
    ticker: str
    name: str
    asset_type: str


class AssetRead(BaseModel):
    id: int
    ticker: str
    name: str
    asset_type: str

    model_config = {"from_attributes": True}
