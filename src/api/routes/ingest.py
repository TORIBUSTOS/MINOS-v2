from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.services.ingestion import SUPPORTED_EXTENSIONS, ingest_file, preview_file

router = APIRouter(prefix="/api/v1/ingest", tags=["ingestion"])


@router.post("/file")
async def ingest_file_endpoint(
    file: UploadFile = File(...),
    source_name: str = Form(...),
    portfolio_name: str = Form(...),
    force_confirm: bool = Form(False),
    db: Session = Depends(get_db),
):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Formato no soportado: '{ext}'. Use CSV, XLSX, PDF o imagen.")

    content = await file.read()
    try:
        result = ingest_file(
            db=db,
            content=content,
            filename=file.filename,
            source_name=source_name,
            portfolio_name=portfolio_name,
            force_confirm=force_confirm,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


@router.post("/preview")
async def ingest_preview_endpoint(
    file: UploadFile = File(...),
    source_name: str = Form(""),
    portfolio_name: str = Form(""),
    db: Session = Depends(get_db),
):
    ext = "." + file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Formato no soportado: '{ext}'. Use CSV, XLSX, PDF o imagen.")

    content = await file.read()
    try:
        return preview_file(
            content=content,
            filename=file.filename,
            source_name=source_name or None,
            portfolio_name=portfolio_name or None,
            db=db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
