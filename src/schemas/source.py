from pydantic import BaseModel, field_validator


class SourceCreate(BaseModel):
    name: str
    type: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be empty")
        return v


class SourceRead(BaseModel):
    id: int
    name: str
    type: str

    model_config = {"from_attributes": True}
