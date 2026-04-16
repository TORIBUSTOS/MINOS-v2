"""
Ingestion service: parsea CSV/XLSX, valida rows, persiste posiciones.
Nunca persiste sin validación.
"""
from datetime import date
from io import BytesIO
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from src.models.asset import Asset
from src.models.load_record import LoadRecord
from src.models.portfolio import Portfolio
from src.models.position import Position
from src.models.source import Source

# Mapeo flexible de columnas — cubre variaciones comunes de Balanz/IOL
COLUMN_MAP = {
    "ticker": ["ticker", "symbol", "simbolo", "activo", "especie"],
    "cantidad": ["cantidad", "quantity", "qty", "shares", "cuotas"],
    "moneda": ["moneda", "currency", "divisa"],
    "valuacion": ["valuacion", "valuation", "valor", "precio", "value", "monto"],
    "fecha": ["fecha", "date", "fecha_operacion", "fecha_valuacion"],
}

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas del archivo al nombre canónico del sistema."""
    rename = {}
    lower_cols = {c.lower().strip(): c for c in df.columns}
    for canonical, variants in COLUMN_MAP.items():
        for variant in variants:
            if variant in lower_cols:
                rename[lower_cols[variant]] = canonical
                break
    return df.rename(columns=rename)


def _parse_file(content: bytes, filename: str) -> pd.DataFrame:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato no soportado: {ext}")
    if ext == ".csv":
        return pd.read_csv(BytesIO(content))
    return pd.read_excel(BytesIO(content))


def _validate_row(row: dict) -> tuple[bool, str]:
    """Retorna (is_valid, reason). Nunca lanza excepción."""
    ticker = str(row.get("ticker", "")).strip()
    if not ticker or ticker.lower() == "nan":
        return False, "ticker vacío"
    try:
        qty = float(row.get("cantidad", 0))
    except (ValueError, TypeError):
        return False, f"cantidad inválida: {row.get('cantidad')}"
    if qty <= 0:
        return False, f"cantidad debe ser positiva (got {qty})"
    try:
        float(row.get("valuacion", 0))
    except (ValueError, TypeError):
        return False, f"valuacion inválida: {row.get('valuacion')}"
    return True, ""


def _get_or_create_source(db: Session, name: str) -> Source:
    source = db.query(Source).filter_by(name=name).first()
    if not source:
        source = Source(name=name, type="file")
        db.add(source)
        db.flush()
    return source


def _get_or_create_portfolio(db: Session, name: str, source_id: int) -> Portfolio:
    portfolio = db.query(Portfolio).filter_by(name=name, source_id=source_id).first()
    if not portfolio:
        portfolio = Portfolio(name=name, source_id=source_id)
        db.add(portfolio)
        db.flush()
    return portfolio


def _get_or_create_asset(db: Session, ticker: str) -> Asset:
    asset = db.query(Asset).filter_by(ticker=ticker).first()
    if not asset:
        asset = Asset(ticker=ticker, name=ticker, asset_type="unknown")
        db.add(asset)
        db.flush()
    return asset


def ingest_file(
    db: Session,
    content: bytes,
    filename: str,
    source_name: str,
    portfolio_name: str,
) -> dict[str, Any]:
    df = _parse_file(content, filename)
    df = _normalize_columns(df)

    source = _get_or_create_source(db, source_name)
    portfolio = _get_or_create_portfolio(db, portfolio_name, source.id)

    processed = 0
    rejected = 0
    warnings: list[str] = []

    for i, row in df.iterrows():
        row_dict = row.to_dict()
        valid, reason = _validate_row(row_dict)
        if not valid:
            rejected += 1
            warnings.append(f"Fila {i + 2}: {reason}")
            continue

        ticker = str(row_dict["ticker"]).strip().upper()
        asset = _get_or_create_asset(db, ticker)

        try:
            val_date = pd.to_datetime(row_dict.get("fecha", date.today())).date()
        except Exception:
            val_date = date.today()

        position = Position(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            ticker=ticker,
            quantity=float(row_dict["cantidad"]),
            currency=str(row_dict.get("moneda", "ARS")).strip().upper(),
            valuation=float(row_dict["valuacion"]),
            valuation_date=val_date,
            load_type="file",
            validation_status="valid",
        )
        db.add(position)
        processed += 1

    db.add(LoadRecord(
        source_id=source.id,
        load_type="file",
        status="success" if rejected == 0 else "partial",
        records_processed=processed,
        records_rejected=rejected,
    ))
    db.commit()

    return {"processed": processed, "rejected": rejected, "warnings": warnings}
