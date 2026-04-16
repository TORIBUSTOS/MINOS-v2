from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.ingestion import SUPPORTED_EXTENSIONS, ingest_file

router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])


@router.post("/file")
async def ingest_file_endpoint(
    file: UploadFile = File(...),
    source_name: str = Form(...),
    portfolio_name: str = Form(...),
    db: Session = Depends(get_db),
):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Formato no soportado: '{ext}'. Use CSV o XLSX.")

    content = await file.read()
    result = ingest_file(
        db=db,
        content=content,
        filename=file.filename,
        source_name=source_name,
        portfolio_name=portfolio_name,
    )
    return result
