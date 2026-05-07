# AGENTS.md — MINOS PRIME

Sistema de inteligencia patrimonial de TORO.
Documentación de referencia: https://github.com/TORIBUSTOS/Trinity → `projects/minos-prime/`

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12+ / FastAPI |
| ORM | SQLAlchemy 2.x (async-ready) |
| Validación | Pydantic v2 |
| DB (MVP) | SQLite |
| DB (prod) | PostgreSQL |
| Migraciones | Alembic |
| Frontend | React / Next.js / TailwindCSS |
| Testing | pytest + pytest-asyncio + httpx |

---

## Comandos

```bash
# Instalar dependencias
pip install -r requirements.txt

# Levantar API (dev)
uvicorn src.main:app --reload --port 8800

# Levantar stack completo (Windows)
start_minos.bat

# Frontend (dev)
cd frontend/client && npm run dev   # puerto 4400

# Tests — usar py -3.12 explícitamente (las deps están en Python 3.12)
py -3.12 -m pytest tests/ -v

# Tests con coverage
py -3.12 -m pytest tests/ --cov=src --cov-report=term-missing

# Migraciones
alembic upgrade head
alembic revision --autogenerate -m "descripción"
```

---

## Estructura

```
minos-v2/
├── src/
│   ├── api/
│   │   └── routes/          # Endpoints FastAPI
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas (input/output)
│   ├── services/            # Lógica de negocio
│   ├── core/                # Config, DB session, settings
│   └── main.py              # App entrypoint
├── tests/
│   └── fixtures/            # CSV/XLSX de prueba
├── docs/                    # Docs técnicos internos
├── scripts/                 # Scripts de utilidad
├── minos-prime/             # Especificación (no código)
├── alembic/                 # Migraciones
├── requirements.txt
├── .gitignore
└── AGENTS.md
```

---

## Convenciones

- Archivos: `snake_case.py`
- Clases: `PascalCase`
- Endpoints: `/api/v1/<recurso>` en plural
- Modelos SQLAlchemy en `src/models/` — un archivo por entidad
- Schemas Pydantic en `src/schemas/` — separar `XCreate`, `XRead`, `XUpdate`
- Servicios en `src/services/` — sin dependencias directas de FastAPI
- Tests: espejo de `src/` en `tests/` — `test_<módulo>.py`
- Cada endpoint tiene al menos 1 test de integración con `httpx`
- Validación siempre en Pydantic antes de tocar la DB

---

## Testing — Gotchas

- SQLite in-memory: usar `poolclass=StaticPool` en el engine de test — FastAPI corre en threadpool y cada thread abriría conexión nueva (DB vacía)
- Importar TODOS los modelos antes de `Base.metadata.create_all()` aunque no se usen directamente — si falta uno, la tabla no existe
- Fixture chain: `db_engine (StaticPool)` → `client` + `db_session` — ambos deben compartir el mismo engine
- FastAPI lifespan: usar `@asynccontextmanager` + `lifespan=` en `FastAPI(...)` — `@app.on_event` está deprecado
- `datetime.utcnow()` deprecado en Python 3.12 — usar `datetime.now(timezone.utc)` siempre
- Fixtures compartidos en `tests/conftest.py` con helpers: `make_source`, `make_portfolio`, `make_asset`, `make_position`
- `py -3.12 -m pytest` — NO usar `python -m pytest`, las deps están en Python 3.12 específicamente
- Mock yfinance: patchear `src.services.market_data.yf.Ticker` + `MarketDataService._cache.clear()` en fixture autouse

---

## Git / PR Workflow

- Cada BN → rama propia (`Codex/minos-bn<NNN>`) + PR → merge directo via `gh pr merge --merge --delete-branch`
- No commitear directo a main — siempre PR
- Si remote diverge: `git pull --rebase && git push`

---

## Frontend

- Path canónico: `frontend/client/` — toda UI nueva va ahí (reorganizado desde `v0-financial-toro-dashboard-2-main/` en PR#5, que ya no se usa)
- Puerto: 4400 (`next dev --port 4400`)
- API client centralizado: `frontend/client/lib/minos-api.ts` — clase `MinosAPI` con todos los métodos
- Hooks en `frontend/client/hooks/use-minos.ts` — factory `useMinosQuery<T>` para estado loading/error/data
- Tipos en `frontend/client/types/minos.ts`

## API — Gotchas

- Upload endpoint: `POST /api/v1/ingest/file` (no `/upload`, no `/ingest/upload`)
- Upload soporta CSV/XLSX/XLS/PDF/imagenes (`.png`, `.jpg`, `.jpeg`, `.webp`). PDF Balanz funciona por texto embebido; imagenes requieren OCR con binario `tesseract` instalado y en PATH.
- Reset seguro de datos cargados: `POST /api/v1/admin/reset-uploaded-data` con body `{"confirm": true}`. Borra solo `positions` y `load_records` con `load_type in ("file", "manual")`; preserva datos API/conectores (`api`, `visual`) y catálogos (`sources`, `portfolios`, `assets`).
- CORS habilitado para frontend local `http://localhost:4400` y `http://127.0.0.1:4400`.
- `/api/v1/intelligence/signals` retorna lista directa — no `{signals: [], signal_summary: {}}`
- `/api/v1/market/refresh` debe refrescar con contexto de instrumento (`ticker`, `exchange`, `instrument_type`), no con tickers pelados. Para acciones BYMA conocidas debe resolver `BMA -> BMA.BA`, `YPFD -> YPFD.BA`.
- Antes de crear rama nueva: verificar que `main` local esté al día — si hay PRs recientes, hacer `git fetch origin && git reset --hard origin/main` para evitar diffs inflados por divergencia

## Market Data

- yfinance aprobado (`yfinance>=0.2.54`) — acciones argentinas usan sufijo `.BA` (ej: `GGAL.BA`, `YPFD.BA`)
- yfinance ya esta conectado al portfolio engine para acciones BYMA conocidas aunque el `Asset.asset_type` viejo sea `unknown`; la inferencia vive en `src/services/normalization.py::infer_asset_type`.
- `SUPPORTED_DYNAMIC_ASSET_TYPES` incluye `EQUITY` y `CEDEAR`; bonos/fondos/ON siguen usando valuacion almacenada salvo implementacion explicita de proveedor.
- Verificacion real hecha contra backend local: `POST /api/v1/market/refresh` devolvio `YPFD: 67650.0` y `BMA: 10890.0`; `portfolio/summary` mostro `valuation_status: OK`, `resolved_symbol: YPFD.BA/BMA.BA`.
- Mock en tests: patchear `src.services.market_data.yf.Ticker` (no `yfinance.Ticker`)
- `MarketDataService._cache.clear()` en fixture `autouse=True` antes/después de cada test

## Ingestion / OCR

- Parser de resumen Balanz PDF agregado en `src/services/ingestion.py`: detecta secciones `Acciones`, `Bonos`, `Cedears`, `Corporativos`, `Fondos` y persiste `asset_type` inferido.
- El PDF `ResumenDeCuenta_20260501.pdf` fue probado localmente: extrae 23 posiciones (6 `EQUITY`, 4 `BOND`, 9 `CEDEAR`, 1 `CORPORATE_BOND`, 3 `FUND`).
- OCR de imagenes esta cableado via `pytesseract`, pero en esta maquina falta el ejecutable `tesseract`; si se sube imagen, el backend devuelve error claro hasta instalarlo.
- Tests relevantes: `tests/test_statement_ingestion.py`, `tests/test_api_market.py`, `tests/test_admin_reset.py`, `tests/test_cors.py`.

## Frontend — Gotchas recientes

- `frontend/client/app/tickers/page.tsx`: todos los hooks deben ejecutarse antes de returns tempranos. Hubo error por `useMemo` condicional; no reintroducir hooks despues de `if (loading/error/null) return`.
- `frontend/client/app/manual-entry/page.tsx`: drop masivo acepta CSV/Excel/PDF/imagenes y refresca vistas mediante `triggerMinosRefresh()` despues de importar.
- `frontend/client/app/settings/page.tsx`: seccion Datos incluye reset destructivo con confirmacion visual; no llamar endpoint sin confirmacion.
- `next build` modifica automaticamente `frontend/client/next-env.d.ts` entre `.next/dev/types/routes.d.ts` y `.next/types/routes.d.ts`; evitar commitear ese cambio si solo es ruido de build.

---

## Boundaries (NO hacer sin aprobación de Tori)

- Cambiar la estructura de carpetas raíz
- Agregar dependencias nuevas al `requirements.txt`
- Modificar modelos de datos ya migrados (requiere discusión)
- Cambiar el scope de un BN aprobado
- Deployar a producción

## Autonomía (SÍ hacer con libertad)

- Decisiones técnicas dentro de un BN (documentar en `trinity/decisions.md`)
- Refactor interno de un módulo sin cambiar su contrato
- Agregar tests
- Pausar si se detecta riesgo o violación de specs

---

## BN Activo

Ver `minos-prime/MINOS_BN_BREAKDOWN.md` para el estado completo.

**Sprint 1 — TRACK A: Data Layer** ✅
- [x] BN-001: Scaffold
- [x] BN-002: Modelo de datos + Schemas
- [x] BN-003: Ingestion CSV/Excel
- [x] BN-004: Carga manual

**Sprint 1 — TRACK B: Portfolio Engine** ✅
- [x] BN-005: Portfolio Engine — consolidación multi-cartera
- [x] BN-006: Unified Ticker Layer
- [x] BN-007: Normalization (tickers, monedas, duplicados)
- [x] BN-007b: Market Data Service (yfinance, cache TTL, fallback MERVAL .BA)
- [x] BN-008: API patrimonial — 6 endpoints REST (http://localhost:8001)

**Sprint 1 — TRACK C: Frontend Base** ✅
- [x] BN-009: Scaffold frontend + Layout
- [x] BN-010: Vista Dashboard
- [x] BN-011: Vista Carteras
- [x] BN-012: Vista Tickers + Carga manual
- [x] Frontend Local: http://localhost:4400
- [x] Branding: MINOS Prime

**Sprint 1 — TRACK D: Intelligence Layer** ✅
- [x] BN-013: IntelligenceEngine — señales BUY/HOLD/SELL por ticker
- [x] BN-014: DecisionEngine — estado cartera (EXPANSIÓN/NEUTRAL/RIESGO)
- [x] BN-015: ReallocationEngine — sugerencias de reasignación
- [x] BN-016: API Intelligence — 3 endpoints REST (/api/v1/intelligence/)

**Sprint 1 — TRACK E: Integración + Polish** ✅
- [x] BN-017: Integrar frontend con API real (hooks, minos-api, types)
- [x] BN-018: ReallocationPanel en dashboard + signal badges en instruments
- [x] BN-019: Drag & drop real en upload + 10 E2E pipeline tests

**Sprint 1 CERRADO** ✅ — 19/19 BNs, 71 tests, 9 PRs mergeados (2026-04-27)

Branch activo: `main` — próximo: Sprint 2 (por definir)
