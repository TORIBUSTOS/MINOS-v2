from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.position import PositionManualCreate, PositionRead
from src.services.positions import create_manual_position, list_positions

router = APIRouter(prefix="/api/v1/positions", tags=["positions"])


@router.post("", response_model=PositionRead, status_code=status.HTTP_201_CREATED)
def create_position(
    data: PositionManualCreate,
    db: Session = Depends(get_db),
):
    return create_manual_position(db, data)


@router.get("", response_model=list[PositionRead])
def get_positions(
    portfolio_name: str | None = None,
    source_name: str | None = None,
    db: Session = Depends(get_db),
):
    return list_positions(db, portfolio_name=portfolio_name, source_name=source_name)
