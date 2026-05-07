from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.admin import reset_uploaded_data

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


class ResetUploadedDataRequest(BaseModel):
    confirm: bool = False


@router.post("/reset-uploaded-data")
def reset_uploaded_data_endpoint(
    payload: ResetUploadedDataRequest,
    db: Session = Depends(get_db),
):
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="Reset requires confirm=true")
    return reset_uploaded_data(db)
