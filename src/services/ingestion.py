"""
Ingestion service: parsea CSV/XLSX, valida rows, persiste posiciones.
Nunca persiste sin validación.
"""
from datetime import date
from io import BytesIO
import os
from pathlib import Path
import re
from typing import Any

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.asset import Asset
from src.models.load_record import LoadRecord
from src.models.portfolio import Portfolio
from src.models.position import Position
from src.models.source import Source
from src.services.normalization import infer_asset_type

# Mapeo flexible de columnas — cubre variaciones comunes de Balanz/IOL
COLUMN_MAP = {
    "ticker": ["ticker", "symbol", "simbolo", "activo", "especie"],
    "cantidad": ["cantidad", "quantity", "qty", "shares", "cuotas"],
    "moneda": ["moneda", "currency", "divisa"],
    "valuacion": ["valuacion", "valuation", "valor", "precio", "value", "monto"],
    "fecha": ["fecha", "date", "fecha_operacion", "fecha_valuacion"],
}

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg", ".webp"}

SECTION_ASSET_TYPES = {
    "Acciones": "EQUITY",
    "Bonos": "BOND",
    "Cedears": "CEDEAR",
    "Corporativos": "CORPORATE_BOND",
    "Fondos": "FUND",
}

BALANZ_LAYOUT_COLUMNS = {
    "ticker": "Ticker",
    "cantidad": "Nominales",
    "precio": "Precio",
    "ppc": "PPC",
    "valuacion": "V. Actual",
    "valor_inicial": "V. Inicial",
    "rendimiento": "Rendimiento",
    "variacion": "Variación (%)",
    "pct_rendimiento": "% de R.",
    "dpt": "DPT",
}

BALANZ_OPTIONAL_LAYOUT_COLUMNS = {
    "fecha": "Fecha",
}

STATEMENT_HEADER_WORDS = {
    "Especie",
    "Descripción",
    "Descripcion",
    "Cantidad",
    "Garantía",
    "Garantia",
    "Precio",
    "Valor Actual",
}


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


def _parse_number(value: str) -> float:
    cleaned = (
        str(value)
        .replace("$", "")
        .replace("%", "")
        .replace(" ", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )
    return float(cleaned)


def _looks_like_number(value: str) -> bool:
    try:
        _parse_number(value)
        return True
    except (TypeError, ValueError):
        return False


def _looks_like_date(value: str) -> bool:
    return bool(re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", str(value).strip()))


def _normalise_ocr_text(value: str) -> str:
    return (
        value.lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )


def _section_asset_type_from_line(line: str) -> str | None:
    match = re.search(r"\b(Acciones|Bonos|Cedears|Corporativos|Fondos)(?:\s*\(\d+\))?", line)
    if not match:
        return None
    return SECTION_ASSET_TYPES[match.group(1)]


def _detect_balanz_layout_missing_columns(text: str) -> list[str]:
    normalised = _normalise_ocr_text(text)
    checks = {
        "ticker": ["ticker"],
        "cantidad": ["nominales"],
        "precio": ["precio"],
        "ppc": ["ppc"],
        "valuacion": ["v. actual", "v actual", "y actual", "actual"],
        "valor_inicial": ["v. inicial", "v inicial", "inicial"],
        "rendimiento": ["rendimiento"],
        "variacion": ["variacion", "varacion"],
        "pct_rendimiento": ["% de r", "de r"],
        "dpt": ["dpt"],
    }
    return [
        BALANZ_LAYOUT_COLUMNS[key]
        for key, variants in checks.items()
        if not any(variant in normalised for variant in variants)
    ]


def _number_tokens(value: str) -> list[str]:
    return re.findall(r"-?\$?\s*\d+(?:[.,]\d{3})*(?:[.,]\d+)?%?", value)


def _parse_balanz_ocr_row_line(line: str, asset_type: str, valuation_date: date) -> dict[str, Any] | None:
    match = re.match(r"^([A-Z]{2,8})\s+(.+)$", line.strip())
    if not match:
        return None

    ticker = match.group(1)
    if ticker in {"TICKER", "PESOS", "TOTALES"}:
        return None

    rest = match.group(2)
    row_date = None
    date_match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", rest)
    if date_match:
        row_date = pd.to_datetime(date_match.group(0), dayfirst=True).date()
        rest = rest.replace(date_match.group(0), " ")

    values = _number_tokens(rest)
    if len(values) < 6:
        return None

    # Layout completo Balanz sin fecha obligatoria:
    # cantidad, precio, ppc, v_actual, v_inicial, rendimiento, variacion..., pct_r, dpt
    #
    # OCR puede intercalar tokens de tiempo (HH:MM) entre precio y PPC.
    # Tokens típicos tras ticker para una línea completa:
    #   [0] cantidad
    #   [1] precio  (puede venir con "$ ")
    #   [2] hora-parte1  (ej. "16" de "16:19") — NO es ppc
    #   [3] hora-parte2  (ej. "19" de "16:19") — NO es v_actual
    #   [4] ppc
    #   [5] v_actual     (con "$")
    #   [6] v_inicial    (con "$")
    #   [7] rendimiento  (con "$")
    #
    # Identificación de tokens de tiempo: dos enteros de 1-2 dígitos adyacentes
    # en el string original (separados por ":") sugieren hora HH:MM.
    # Ejemplo: "$ 19.840,00 16:19 13.671,87" → tokens [2]="16" [3]="19"
    time_pair_match = re.search(r"(\d{1,2}):(\d{1,2})", rest)
    has_time_tokens = bool(time_pair_match)
    qty = _parse_number(values[0])
    precio_raw = values[1] if len(values) > 1 else "0"
    precio = _parse_number(precio_raw.replace("$", "").replace(",", "."))
    if has_time_tokens:
        ppc = _parse_number(values[4]) if len(values) > 4 else None
        v_actual = _parse_number(values[5].replace("$", "").replace(",", "")) if len(values) > 5 else None
        v_inicial = _parse_number(values[6].replace("$", "").replace(",", "")) if len(values) > 6 else None
        rendimiento = _parse_number(values[7].replace("$", "").replace(",", "")) if len(values) > 7 else None
    else:
        ppc = _parse_number(values[2]) if len(values) > 2 else None
        v_actual = _parse_number(values[3].replace("$", "").replace(",", "")) if len(values) > 3 else None
        v_inicial = _parse_number(values[4].replace("$", "").replace(",", "")) if len(values) > 4 else None
        rendimiento = _parse_number(values[5].replace("$", "").replace(",", "")) if len(values) > 5 else None

    pct_index = len(values) - 2 if len(values) >= 8 else None
    dpt_index = len(values) - 1 if len(values) >= 7 else None
    try:
        return {
            "ticker": ticker,
            "cantidad": qty,
            "moneda": "ARS",
            "precio": precio,
            "ppc": ppc,
            "valuacion": v_actual,
            "valor_inicial": v_inicial,
            "rendimiento": rendimiento,
            "pct_rendimiento": _parse_number(values[pct_index]) if pct_index is not None else None,
            "dpt": _parse_number(values[dpt_index]) if dpt_index is not None else None,
            "fecha": row_date or valuation_date,
            "asset_type": asset_type,
        }
    except (ValueError, TypeError):
        return None


def _is_complete_balanz_row(row: dict[str, Any]) -> bool:
    required = ["precio", "ppc", "valuacion", "valor_inicial", "rendimiento", "pct_rendimiento"]
    return all(pd.notna(row.get(field)) for field in required)


def _statement_date_from_filename(filename: str) -> date:
    match = re.search(r"(20\d{6})", filename)
    if not match:
        return date.today()
    try:
        return pd.to_datetime(match.group(1), format="%Y%m%d").date()
    except Exception:
        return date.today()


def _extract_pdf_text(content: bytes) -> str:
    try:
        import fitz
    except ImportError as exc:
        raise ValueError("PDF no soportado: falta PyMuPDF/fitz en el entorno") from exc

    with fitz.open(stream=content, filetype="pdf") as doc:
        text = "\n".join(page.get_text("text") for page in doc)

    # Si el texto extraído es casi vacío, el PDF probablemente es una imagen escaneada.
    # Intentamos OCR del rendered page como respaldo.
    if len(text.strip()) < 50:
        from PIL import Image
        import pytesseract

        try:
            tesseract_exe = Path("C:/Program Files/Tesseract-OCR/tesseract.exe")
            if tesseract_exe.exists():
                pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)
            user_tessdata = Path(os.environ.get("LOCALAPPDATA", "")) / "Tesseract-OCR" / "tessdata"
            if user_tessdata.exists():
                os.environ["TESSDATA_PREFIX"] = str(user_tessdata)

            ocr_lines: list[str] = []
            for page in doc:
                mat = fitz.Matrix(4, 4)  # 4x zoom for sharp OCR
                pix = page.get_pixmap(matrix=mat)
                img = Image.open(BytesIO(pix.tobytes("png"))).convert("L")
                if img.width < 1800:
                    ratio = 1800 / img.width
                    img = img.resize((1800, int(img.height * ratio)))
                ocr_lines.append(pytesseract.image_to_string(img, lang="spa+eng", config="--psm 6"))
            text = "\n".join(ocr_lines)
        except Exception:
            pass  # Mantenemos el texto original (vacío o casi vacío)

    return text


def _extract_image_text(content: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract
    except ImportError as exc:
        raise ValueError("Imagen no soportada: faltan PIL/pytesseract en el entorno") from exc

    try:
        tesseract_exe = Path("C:/Program Files/Tesseract-OCR/tesseract.exe")
        if tesseract_exe.exists():
            pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)

        user_tessdata = Path(os.environ.get("LOCALAPPDATA", "")) / "Tesseract-OCR" / "tessdata"
        if user_tessdata.exists():
            os.environ["TESSDATA_PREFIX"] = str(user_tessdata)

        image = Image.open(BytesIO(content)).convert("L")
        if image.width < 1800:
            ratio = 1800 / image.width
            image = image.resize((1800, int(image.height * ratio)))
        return pytesseract.image_to_string(image, lang="spa+eng", config="--psm 6")
    except Exception as exc:
        raise ValueError(
            "No se pudo leer la imagen por OCR. Verificá que Tesseract esté instalado y en PATH."
        ) from exc


def _parse_statement_text(text: str, filename: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    active_asset_type: str | None = None
    valuation_date = _statement_date_from_filename(filename)
    missing_columns = _detect_balanz_layout_missing_columns(text)
    has_balanz_layout = (
        "ticker" in _normalise_ocr_text(text)
        and "ppc" in _normalise_ocr_text(text)
        and ("v. actual" in _normalise_ocr_text(text) or "v actual" in _normalise_ocr_text(text))
    )
    if has_balanz_layout and missing_columns:
        warnings.append(
            "Layout Balanz incompleto: faltan columnas "
            + ", ".join(missing_columns)
            + ". Revisar preview antes de consolidar."
        )
    elif not has_balanz_layout:
        warnings.append(
            "Resumen incompleto: no se detectó layout Balanz de 10 columnas. "
            "Usá captura de la tabla completa para no inventar PPC, V.Inicial ni rendimiento."
        )
    i = 0

    while i < len(lines):
        line = lines[i]
        section_asset_type = _section_asset_type_from_line(line)
        if section_asset_type:
            active_asset_type = section_asset_type
            i += 1
            continue

        if (
            line in STATEMENT_HEADER_WORDS
            or line in BALANZ_LAYOUT_COLUMNS.values()
            or line in BALANZ_OPTIONAL_LAYOUT_COLUMNS.values()
            or line in {"Pesos", "Totales"}
            or active_asset_type is None
        ):
            i += 1
            continue

        if not re.fullmatch(r"[A-Z0-9]{2,15}", line):
            row = _parse_balanz_ocr_row_line(line, active_asset_type, valuation_date)
            if row:
                rows.append(row)
            i += 1
            continue

        ticker = line
        numeric_values: list[str] = []
        row_date: date | None = None
        j = i + 1
        while j < len(lines) and len(numeric_values) < 9:
            candidate = lines[j]
            if _section_asset_type_from_line(candidate):
                break
            if candidate in {"Pesos", "Totales"}:
                j += 1
                continue
            if (
                numeric_values
                and re.fullmatch(r"[A-Z0-9]{2,15}", candidate)
                and re.search(r"[A-Z]", candidate)
            ):
                break
            if row_date is None and _looks_like_date(candidate):
                row_date = pd.to_datetime(candidate, dayfirst=True).date()
                j += 1
                continue
            if _looks_like_number(candidate):
                numeric_values.append(candidate)
            j += 1

        if len(numeric_values) >= 4:
            has_layout_values = len(numeric_values) >= 6 and row_date is not None
            price_index = 1 if has_layout_values else 2
            ppc_index = 2 if has_layout_values else None
            valuation_index = 3
            initial_value_index = 4 if has_layout_values else None
            performance_index = 5 if has_layout_values else None
            pct_performance_index = 6 if len(numeric_values) > 6 else None
            dpt_index = 7 if len(numeric_values) > 7 else None
            rows.append(
                {
                    "ticker": ticker,
                    "cantidad": _parse_number(numeric_values[0]),
                    "moneda": "ARS",
                    "precio": _parse_number(numeric_values[price_index]) if len(numeric_values) > price_index else None,
                    "ppc": _parse_number(numeric_values[ppc_index]) if ppc_index is not None else None,
                    "valuacion": _parse_number(numeric_values[valuation_index]),
                    "valor_inicial": _parse_number(numeric_values[initial_value_index]) if initial_value_index is not None else None,
                    "rendimiento": _parse_number(numeric_values[performance_index]) if performance_index is not None else None,
                    "pct_rendimiento": _parse_number(numeric_values[pct_performance_index]) if pct_performance_index is not None else None,
                    "dpt": _parse_number(numeric_values[dpt_index]) if dpt_index is not None else None,
                    "fecha": row_date or valuation_date,
                    "asset_type": active_asset_type,
                }
            )
            i = j
            continue

        i += 1

    if not rows:
        sample = " | ".join(lines[:8])
        raise ValueError(
            "No se detectaron posiciones en el resumen. "
            f"Texto OCR inicial: {sample[:500]}"
        )

    df = pd.DataFrame(rows)
    complete_rows = [_is_complete_balanz_row(row) for row in rows]
    can_confirm = bool(rows) and all(complete_rows)
    if can_confirm:
        warnings = [
            warning for warning in warnings
            if not warning.startswith("Resumen incompleto:")
            and not warning.startswith("Layout Balanz incompleto:")
        ]
        missing_columns = []
    if has_balanz_layout and not all(complete_rows):
        warnings.append("Hay filas con datos incompletos. Revisar preview antes de consolidar.")
    df.attrs["can_confirm"] = can_confirm
    df.attrs["missing_columns"] = missing_columns
    df.attrs["detected_layout"] = "balanz_10_columns" if can_confirm else "statement_partial"
    df.attrs["warnings"] = warnings
    return df


def _parse_file(content: bytes, filename: str) -> pd.DataFrame:
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato no soportado: {ext}")
    if ext == ".csv":
        return pd.read_csv(BytesIO(content))
    if ext in {".xlsx", ".xls"}:
        return pd.read_excel(BytesIO(content))
    if ext == ".pdf":
        return _parse_statement_text(_extract_pdf_text(content), filename)
    return _parse_statement_text(_extract_image_text(content), filename)


def _normalise_asset_type(value: Any) -> str:
    asset_type = str(value or "unknown").strip().upper()
    return asset_type if asset_type and asset_type != "NAN" else "unknown"


def _canonical_source_name(name: str) -> str:
    cleaned = name.strip()
    known = {
        "balanz": "BALANZ",
        "iol": "IOL",
    }
    return known.get(cleaned.lower(), cleaned)


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
    canonical_name = _canonical_source_name(name)
    source = db.query(Source).filter(Source.name == canonical_name).first()
    if not source:
        source = (
            db.query(Source)
            .filter(func.lower(Source.name) == canonical_name.lower())
            .first()
        )
        if source:
            source.name = canonical_name
            db.flush()
    if not source:
        source = Source(name=canonical_name, type="file")
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


def _get_or_create_asset(db: Session, ticker: str, asset_type: str = "unknown") -> Asset:
    inferred_asset_type = infer_asset_type(ticker, asset_type)
    asset = db.query(Asset).filter_by(ticker=ticker).first()
    if not asset:
        asset = Asset(ticker=ticker, name=ticker, asset_type=inferred_asset_type)
        db.add(asset)
        db.flush()
    elif asset.asset_type == "unknown" and inferred_asset_type != "unknown":
        asset.asset_type = inferred_asset_type
        db.flush()
    return asset


def ingest_file(
    db: Session,
    content: bytes,
    filename: str,
    source_name: str,
    portfolio_name: str,
    force_confirm: bool = False,
) -> dict[str, Any]:
    df = _parse_file(content, filename)
    parser_warnings = list(df.attrs.get("warnings", []))
    df = _normalize_columns(df)
    is_statement_snapshot = "asset_type" in df.columns
    if is_statement_snapshot and not df.attrs.get("can_confirm", False) and not force_confirm:
        raise ValueError(
            "No se consolidó: el resumen no tiene las 10 columnas Balanz completas. "
            "Subí una captura completa y confirmala desde la preview."
        )

    source = _get_or_create_source(db, source_name)
    portfolio = _get_or_create_portfolio(db, portfolio_name, source.id)

    if is_statement_snapshot:
        db.query(Position).filter(
            Position.portfolio_id == portfolio.id,
            Position.load_type == "file",
        ).delete(synchronize_session=False)
        db.flush()

    processed = 0
    rejected = 0
    warnings: list[str] = []
    warnings.extend(parser_warnings)
    if is_statement_snapshot:
        if df.attrs.get("can_confirm", False):
            warnings.append(
                "Resumen detectado como snapshot completo: se reemplazaron posiciones previas "
                "del archivo para evitar duplicados."
            )
        else:
            warnings.append(
                "Resumen detectado como snapshot parcial: se reemplazaron posiciones previas "
                "del archivo para evitar duplicados. El rendimiento real requiere PPC/V.Inicial "
                "del origen o confirmación manual."
            )
    if force_confirm:
        warnings.append("Carga confirmada por usuario desde preview aunque el parser marcó advertencias.")

    for i, row in df.iterrows():
        row_dict = row.to_dict()
        valid, reason = _validate_row(row_dict)
        if not valid:
            rejected += 1
            warnings.append(f"Fila {i + 2}: {reason}")
            continue

        ticker = str(row_dict["ticker"]).strip().upper()
        asset = _get_or_create_asset(db, ticker, _normalise_asset_type(row_dict.get("asset_type")))

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
            unit_price=float(row_dict["precio"]) if pd.notna(row_dict.get("precio")) else None,
            avg_cost=(
                float(row_dict["valor_inicial"]) / float(row_dict["cantidad"])
                if pd.notna(row_dict.get("valor_inicial")) and float(row_dict.get("cantidad") or 0) > 0
                else None
            ),
            cost_basis=float(row_dict["valor_inicial"]) if pd.notna(row_dict.get("valor_inicial")) else None,
            pnl_absolute=float(row_dict["rendimiento"]) if pd.notna(row_dict.get("rendimiento")) else None,
            pnl_percentage=float(row_dict["pct_rendimiento"]) if pd.notna(row_dict.get("pct_rendimiento")) else None,
            dpt=float(row_dict["dpt"]) if pd.notna(row_dict.get("dpt")) else None,
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


def preview_file(content: bytes, filename: str) -> dict[str, Any]:
    df = _parse_file(content, filename)
    parser_warnings = list(df.attrs.get("warnings", []))
    missing_columns = list(df.attrs.get("missing_columns", []))
    detected_layout = df.attrs.get("detected_layout", "tabular_file")
    can_confirm = bool(df.attrs.get("can_confirm", True))
    df = _normalize_columns(df)

    rows: list[dict[str, Any]] = []
    rejected = 0
    warnings = list(parser_warnings)
    for i, row in df.iterrows():
        row_dict = row.to_dict()
        valid, reason = _validate_row(row_dict)
        if not valid:
            rejected += 1
            warnings.append(f"Fila {i + 2}: {reason}")
            continue
        rows.append(
            {
                "ticker": str(row_dict["ticker"]).strip().upper(),
                "cantidad": float(row_dict["cantidad"]),
                "moneda": str(row_dict.get("moneda", "ARS")).strip().upper(),
                "precio": float(row_dict["precio"]) if pd.notna(row_dict.get("precio")) else None,
                "fecha": str(pd.to_datetime(row_dict.get("fecha", date.today())).date()),
                "ppc": float(row_dict["ppc"]) if pd.notna(row_dict.get("ppc")) else None,
                "valuacion": float(row_dict["valuacion"]),
                "valor_inicial": float(row_dict["valor_inicial"]) if pd.notna(row_dict.get("valor_inicial")) else None,
                "rendimiento": float(row_dict["rendimiento"]) if pd.notna(row_dict.get("rendimiento")) else None,
                "pct_rendimiento": float(row_dict["pct_rendimiento"]) if pd.notna(row_dict.get("pct_rendimiento")) else None,
                "dpt": float(row_dict["dpt"]) if pd.notna(row_dict.get("dpt")) else None,
                "asset_type": _normalise_asset_type(row_dict.get("asset_type")),
                "complete": _is_complete_balanz_row(row_dict) if "asset_type" in df.columns else True,
            }
        )

    if rejected:
        can_confirm = False
    return {
        "filename": filename,
        "detected_layout": detected_layout,
        "can_confirm": can_confirm and rejected == 0,
        "missing_columns": missing_columns,
        "rows": rows,
        "processed": len(rows),
        "rejected": rejected,
        "warnings": warnings,
    }
