# CLAUDE.md — MINOS PRIME

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
uvicorn src.main:app --reload --port 8001

# Tests
pytest tests/ -v

# Tests con coverage
pytest tests/ --cov=src --cov-report=term-missing

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
└── CLAUDE.md
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
- [x] BN-008: API patrimonial — 6 endpoints REST

**Total: 92 tests passing**

Branch activo: `claude/minos-bn001`
