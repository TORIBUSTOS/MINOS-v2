from src.models.asset import Asset
from src.models.position import Position
from src.models.source import Source
from src.services.ingestion import _parse_statement_text, ingest_file, preview_file


BALANZ_TEXT = """
Acciones
Especie
Descripción
Cantidad
Garantía
Precio
Valor Actual
BMA
BANCO MACRO S.A."B" 1 V. ESCRIT
65,00
0.00
$ 10.890,00
$ 707.850
YPFD
YPF S.A. ESCRIT. "D" 1 VOTO
15,00
0.00
$ 67.650,00
$ 1.014.750
Bonos
Especie
Descripción
Cantidad
Garantía
Precio
Valor Actual
AL30
BONO REP. ARGENTINA USD STEP UP 2030
1.700,00
0.00
$ 913,20
$ 1.552.440
Cedears
Especie
Descripción
Cantidad
Garantía
Precio
Valor Actual
MELI
CEDEAR MERCADOLIBRE INC.
13,00
0.00
$ 22.450,00
$ 291.850
"""

BALANZ_SCREENSHOT_TEXT = """
Acciones (6)
Ticker
Nominales
Precio
Fecha
PPC
V. Actual
V. Inicial
Rendimiento
Variación (%)
% de R.
DPT
Pesos
BMA
65
$ 10.890,00
30/04/2026
9.436,97
$ 707.850
$ 613.403
$ 94.447
0.00 (0.00%)
15,40%
317
SUPV
80
$ 2.476,00
30/04/2026
3.423,13
$ 198.080
$ 273.850
$ -75.770
0.00 (0.00%)
-27,67%
184
Totales
"""

BALANZ_INCOMPLETE_SCREENSHOT_TEXT = """
Acciones (6)
Ticker
Nominales
Precio
PPC
V. Actual
Pesos
BMA
65
$ 10.890,00
30/04/2026
9.436,97
$ 707.850
"""


def test_parse_balanz_statement_text_extracts_positions():
    df = _parse_statement_text(BALANZ_TEXT, "ResumenDeCuenta_20260501.pdf")

    rows = {row["ticker"]: row for row in df.to_dict("records")}
    assert rows["BMA"]["cantidad"] == 65.0
    assert rows["BMA"]["valuacion"] == 707850.0
    assert rows["BMA"]["asset_type"] == "EQUITY"
    assert rows["AL30"]["cantidad"] == 1700.0
    assert rows["AL30"]["asset_type"] == "BOND"
    assert rows["MELI"]["asset_type"] == "CEDEAR"


def test_parse_balanz_layout_extracts_full_columns():
    df = _parse_statement_text(BALANZ_SCREENSHOT_TEXT, "screenshot.png")

    rows = {row["ticker"]: row for row in df.to_dict("records")}
    assert rows["BMA"]["cantidad"] == 65.0
    assert rows["BMA"]["precio"] == 10890.0
    assert rows["BMA"]["ppc"] == 9436.97
    assert rows["BMA"]["valuacion"] == 707850.0
    assert rows["BMA"]["valor_inicial"] == 613403.0
    assert rows["BMA"]["rendimiento"] == 94447.0
    assert rows["BMA"]["pct_rendimiento"] == 15.40
    assert rows["BMA"]["dpt"] == 317.0
    assert rows["SUPV"]["rendimiento"] == -75770.0
    assert rows["SUPV"]["pct_rendimiento"] == -27.67
    assert df.attrs["warnings"] == []


def test_parse_balanz_layout_warns_missing_columns():
    df = _parse_statement_text(BALANZ_INCOMPLETE_SCREENSHOT_TEXT, "screenshot.png")

    assert df.to_dict("records")[0]["ticker"] == "BMA"
    assert any("faltan columnas" in warning for warning in df.attrs["warnings"])
    assert any("V. Inicial" in warning for warning in df.attrs["warnings"])
    assert not any("Fecha" in warning for warning in df.attrs["warnings"])


def test_ingest_pdf_statement_persists_extracted_positions(monkeypatch, client, db_session):
    monkeypatch.setattr(
        "src.services.ingestion._extract_pdf_text",
        lambda content: BALANZ_TEXT,
    )

    response = client.post(
        "/api/v1/ingest/file",
        data={"source_name": "Balanz", "portfolio_name": "Principal"},
        files={"file": ("ResumenDeCuenta_20260501.pdf", b"%PDF", "application/pdf")},
    )

    assert response.status_code == 400
    assert "10 columnas Balanz completas" in response.json()["detail"]
    assert db_session.query(Position).count() == 0


def test_ingest_complete_balanz_screenshot_persists_financial_columns(monkeypatch, db_session):
    monkeypatch.setattr(
        "src.services.ingestion._extract_image_text",
        lambda content: BALANZ_SCREENSHOT_TEXT,
    )

    result = ingest_file(
        db=db_session,
        content=b"image",
        filename="screenshot.png",
        source_name="balanz",
        portfolio_name="Principal",
    )

    assert result["processed"] == 2
    bma = db_session.query(Position).filter_by(ticker="BMA").one()
    assert bma.valuation == 707850.0
    assert bma.unit_price == 10890.0
    assert bma.avg_cost == 9436.97
    assert bma.cost_basis == 613403.0
    assert bma.pnl_absolute == 94447.0
    assert bma.pnl_percentage == 15.40
    assert bma.dpt == 317.0
    assert db_session.query(Asset).filter_by(ticker="BMA").one().asset_type == "EQUITY"


def test_ingest_complete_balanz_screenshot_replaces_previous_snapshot(monkeypatch, db_session):
    monkeypatch.setattr(
        "src.services.ingestion._extract_image_text",
        lambda content: BALANZ_SCREENSHOT_TEXT,
    )

    for source_name in ("balanz", "BALANZ"):
        result = ingest_file(
            db=db_session,
            content=b"image",
            filename="screenshot.png",
            source_name=source_name,
            portfolio_name="Principal",
        )
        assert result["processed"] == 2

    assert db_session.query(Position).count() == 2
    assert db_session.query(Source).count() == 1
    assert db_session.query(Source).one().name == "BALANZ"


def test_preview_incomplete_pdf_cannot_confirm(monkeypatch):
    monkeypatch.setattr(
        "src.services.ingestion._extract_pdf_text",
        lambda content: BALANZ_TEXT,
    )

    result = preview_file(b"%PDF", "ResumenDeCuenta_20260501.pdf")

    assert result["can_confirm"] is False
    assert result["processed"] == 4
    assert any("Resumen incompleto" in warning for warning in result["warnings"])


def test_preview_complete_screenshot_can_confirm(monkeypatch):
    monkeypatch.setattr(
        "src.services.ingestion._extract_image_text",
        lambda content: BALANZ_SCREENSHOT_TEXT,
    )

    result = preview_file(b"image", "screenshot.png")

    assert result["can_confirm"] is True
    assert result["processed"] == 2
    assert result["rows"][0]["ppc"] == 9436.97
    assert result["rows"][0]["valor_inicial"] == 613403.0


def test_parse_balanz_ocr_single_line_rows():
    text = """
“> Acciones (6)
Ticker Nominales Precio PPC V. Actual V. Inicial Rendimiento Variación (%) % de R. DPT
BMA 65 $ 10.890,00 9.436,97 $ 707.850 $ 613.403 $ 94.447 0.00 (0.00%) 15,40% 317
SUPV 80 $ 2.476,00 3.423,13 $ 198.080 $ 273.850 $ -75.770 0.00 (0.00%) -27,67% 184
"""

    df = _parse_statement_text(text, "screenshot.png")
    rows = {row["ticker"]: row for row in df.to_dict("records")}

    assert rows["BMA"]["ppc"] == 9436.97
    assert rows["BMA"]["valor_inicial"] == 613403.0
    assert rows["BMA"]["pct_rendimiento"] == 15.40
    assert rows["BMA"]["dpt"] == 317.0
    assert rows["SUPV"]["rendimiento"] == -75770.0
    assert rows["SUPV"]["pct_rendimiento"] == -27.67
