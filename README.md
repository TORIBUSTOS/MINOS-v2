# MINOS PRIME

> Sistema de inteligencia patrimonial de TORO

## Documentación

La especificación completa vive en el repo Trinity:
→ [github.com/TORIBUSTOS/Trinity](https://github.com/TORIBUSTOS/Trinity) — `projects/minos-prime/`

| Doc | Descripción |
|-----|-------------|
| VISION.md | Norte estratégico |
| MISSION.md | Alcance y propósito operativo |
| SPECS.md | Especificaciones funcionales del MVP |
| ARCHITECTURE.md | Arquitectura conceptual y técnica |
| MINOS_BN_BREAKDOWN.md | Bloques de ejecución |

## Setup

```bash
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8800

cd frontend/client
npm install
npm run dev
```

Backend local: `http://localhost:8800`
Frontend local: `http://localhost:4400`

## Estado Actual

**Fase:** MINOS Prime v2 — Sprint 2 integrado localmente
**Backend:** FastAPI + SQLite
**Frontend:** Next.js 16 + React 19

Capacidades activas:

- Dashboard patrimonial con API real.
- Carga manual de posiciones.
- Importación masiva por CSV, Excel, PDF y capturas/imagenes.
- Parser de resumen Balanz PDF con detección de acciones, bonos, CEDEARs, corporativos y fondos.
- Valuación broker-grade para acciones BYMA conocidas usando yfinance (`BMA.BA`, `YPFD.BA`, etc.).
- Cache de precios con TTL.
- Señales de inteligencia y sugerencias de reasignación.
- Reset seguro de datos cargados, preservando datos de API/conectores.

## Sprint 2 — Broker-Grade Valuation Core

Resumen:
- Resolución correcta de instrumentos BYMA (`.BA`)
- Pricing trazable con contexto (`PriceResult`)
- Valuación tipo broker (`market_value`, `pnl`, etc.)
- Bloqueo de señales sin valuación confiable
- UI tipo broker con tabla de instrumentos

Estado:
INTEGRADO LOCALMENTE

Verificación real reciente:

- `POST /api/v1/market/refresh` devolvió `YPFD: 67650.0` y `BMA: 10890.0`.
- `GET /api/v1/portfolio/summary` mostró `valuation_status: OK` y `resolved_symbol: YPFD.BA/BMA.BA`.

## Ingestión

Endpoint único:

```text
POST /api/v1/ingest/file
```

Formatos:

- `.csv`
- `.xlsx`
- `.xls`
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`
- `.webp`

Notas:

- PDF Balanz funciona por texto embebido.
- Capturas/imagenes intentan OCR con `pytesseract`.
- Para OCR de imagenes hace falta instalar el binario `tesseract` y dejarlo en `PATH`.

## Endpoints Principales

| Feature | Endpoint |
|---------|----------|
| Posiciones | `GET /api/v1/positions` |
| Crear posición manual | `POST /api/v1/positions` |
| Portfolio summary | `GET /api/v1/portfolio/summary` |
| Por fuente | `GET /api/v1/portfolio/by-source` |
| Por moneda | `GET /api/v1/portfolio/by-currency` |
| Portfolios | `GET /api/v1/portfolios` |
| Tickers unificados | `GET /api/v1/tickers/unified` |
| Refresh market data | `POST /api/v1/market/refresh` |
| Precios cacheados | `GET /api/v1/market/prices` |
| Upload archivo/resumen | `POST /api/v1/ingest/file` |
| Reset datos cargados | `POST /api/v1/admin/reset-uploaded-data` |
| Signals | `GET /api/v1/intelligence/signals` |
| Estado cartera | `GET /api/v1/intelligence/portfolio-status` |
| Reasignación | `GET /api/v1/intelligence/reallocation` |

Reset seguro:

```json
{ "confirm": true }
```

Borra solo posiciones y registros de carga `file/manual`; preserva datos `api/visual` y catálogos.

## Tests

```bash
py -3.12 -m pytest tests/ -v
```

Tests relevantes agregados:

- `tests/test_api_market.py`
- `tests/test_statement_ingestion.py`
- `tests/test_admin_reset.py`
- `tests/test_cors.py`

Ver [CODEX.md](CODEX.md) y [AGENTS.md](AGENTS.md) para contexto operativo, gotchas y handoff entre agentes.
