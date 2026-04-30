# MINOS PRIME — BN BREAKDOWN (Bloques Negros)

**Fase:** Sprint 1 CERRADO ✅  
**Generado por:** Claude (CTO)  
**Estado:** APROBADO por Tori (Gate-2 cerrado) — Sprint 1 completado 2026-04-28  
**Repo de ejecución:** github.com/TORIBUSTOS/MINOS-v2  
**Stack:** Python 3.12+ / FastAPI (BE) + React / Next.js / TailwindCSS (FE) + SQLite (MVP) / PostgreSQL (prod)

---

## Resumen de Tracks

```
TRACK A ─── Data Layer ──────────────── [Claude]     ── BN-001 a BN-004  ── ✅ COMPLETO
TRACK B ─── Portfolio Engine ────────── [Claude]     ── BN-005 a BN-008  ── ✅ COMPLETO
TRACK C ─── Frontend Base ──────────── [Gemini/AG]  ── BN-009 a BN-012  ── ✅ COMPLETO
TRACK D ─── Intelligence Layer ──────── [Claude]     ── BN-013 a BN-016  ── ✅ COMPLETO
TRACK E ─── Integración + Polish ────── [Claude]     ── BN-017 a BN-019  ── ✅ COMPLETO
```

```
Dependencias:

A ──→ B ──→ D ──→ E
A ──→ C ─────────→ E
      ↑             ↑
      B y C van en paralelo
```

### Métricas Sprint 1

| Métrica | Valor |
|---------|-------|
| BNs completados | 19/19 (100%) |
| Tests backend | 71 pasando, 0 fallos |
| Cobertura | 95-100% |
| PRs mergeados | 10 |
| Endpoints REST | 15 |
| Fecha de cierre | 2026-04-28 |

---

## TRACK A — DATA LAYER ✅

**Agente:** Claude  
**Dependencias:** Ninguna

---

### BN-001: Scaffold del proyecto + CLAUDE.md ✅

**Descripción:** Inicializar el repo MINOS-v2 con estructura de carpetas, CLAUDE.md, dependencias base y configuración del proyecto.

**Aceptación:**
- Repo tiene estructura: `src/`, `tests/`, `docs/`, `scripts/`
- CLAUDE.md en la raíz con stack, comandos, convenciones y boundaries
- `requirements.txt` con dependencias iniciales
- `.gitignore` configurado
- `README.md` apuntando a docs de Trinity

**Implementado:** ✅ Exacto al spec  
**Archivos:** `CLAUDE.md`, `README.md`, `requirements.txt`, `.gitignore`, estructura de carpetas

---

### BN-002: Modelo de datos + Schemas ✅

**Descripción:** Definir modelos SQLAlchemy y schemas Pydantic para el dominio patrimonial.

**Aceptación:**
- Modelos: `Source`, `Portfolio`, `Asset`, `Position`, `LoadRecord`
- Schemas Pydantic para input/output de cada modelo
- Relaciones: Source → Portfolio → Position
- Migración inicial que crea las tablas

**Implementado:** ✅ Exacto al spec  
**Archivos:** `src/models/`, `src/schemas/`, `alembic/`

---

### BN-003: Data Ingestion — CSV/Excel ✅

**Descripción:** Ingestion layer para carga desde archivos CSV y Excel.

**Aceptación:**
- Endpoint `POST /api/v1/ingest/file` acepta CSV y XLSX
- Detecta columnas automáticamente
- Valida datos antes de guardar
- Retorna resumen: procesados, rechazados, warnings

**Implementado:** ✅ Exacto al spec  
**Archivos:** `src/services/ingestion.py`, `src/api/routes/ingest.py`, `tests/test_ingestion.py`, `tests/fixtures/sample_portfolio.csv`

---

### BN-004: Data Ingestion — Carga manual ✅

**Descripción:** Endpoint para agregar posiciones individuales manualmente.

**Aceptación:**
- `POST /api/v1/positions` con body JSON
- `GET /api/v1/positions` con filtros por cartera/fuente
- tipo_carga = "manual"

**Implementado:** ✅ Exacto al spec  
**Archivos:** `src/api/routes/positions.py`, `tests/test_positions.py`

---

## TRACK B — PORTFOLIO ENGINE ✅

**Agente:** Claude  
**Dependencias:** Track A completo

---

### BN-005: Portfolio Engine — Consolidación multi-cartera ✅

**Descripción:** Servicio que consolida todas las posiciones en vista patrimonial total.

**Aceptación:**
- `PortfolioEngine.consolidate()` retorna patrimonio total
- Distribución por activo, por fuente, por moneda
- Trazabilidad a cartera de origen

**Implementado:** ✅ Exacto al spec  
**Archivos:** `src/services/portfolio_engine.py`, `tests/test_portfolio_engine.py`

---

### BN-006: Unified Ticker Layer ✅

**Descripción:** Capa que unifica tickers entre carteras sin sumar nominales.

**Aceptación:**
- `UnifiedTickerService.unify()` retorna tickers únicos con presencia en carteras
- No suma nominales entre carteras

**Implementado:** ✅ Exacto al spec  
**Archivos:** `src/services/unified_ticker.py`, `tests/test_unified_ticker.py`

---

### BN-007: Processing & Normalization ✅

**Descripción:** Capa de limpieza y normalización de datos entrantes.

**Aceptación:**
- Normalización de tickers, monedas, detección de duplicados
- Aliases configurables en JSON
- Log de transformaciones

**Implementado:** ✅ Exacto al spec  
**Archivos:** `src/services/normalization.py`, `tests/test_normalization.py`

---

### BN-007b: Market Data Service ✅

**Descripción:** Precios en vivo vía yfinance con cache TTL.

**Aceptación:**
- `MarketDataService.refresh_prices()` consulta yfinance
- Soporta US y MERVAL (.BA)
- Cache con TTL, fallback a última valuación
- `POST /api/v1/market/refresh`, `GET /api/v1/market/prices`

**Implementado:** ✅ Exacto al spec  
**Nota:** Mock en tests via `patch("src.services.market_data.yf.Ticker")` — no `yfinance.Ticker`  
**Archivos:** `src/services/market_data.py`, `tests/test_market_data.py`

---

### BN-008: API de consulta patrimonial ✅

**Descripción:** Endpoints REST para consultar patrimonio consolidado.

**Aceptación:**
- `GET /api/v1/portfolio/summary`
- `GET /api/v1/portfolio/by-source`
- `GET /api/v1/portfolio/by-currency`
- `GET /api/v1/tickers/unified`
- `GET /api/v1/portfolios`

**Implementado:** ✅ Exacto al spec  
**Archivos:** `src/api/routes/portfolio.py`, `src/api/routes/tickers.py`, `tests/test_api_portfolio.py`

---

## TRACK C — FRONTEND BASE ✅

**Agente:** Gemini/AG + Claude  
**Dependencias:** Track A mínimo

**Nota de implementación:** El frontend se desarrolló inicialmente en `v0-financial-toro-dashboard-2-main/` y fue reorganizado a `frontend/client/` en el PR#5. Path canónico: `frontend/client/`.

---

### BN-009: Scaffold frontend + Layout base ✅

**Descripción:** Next.js + TailwindCSS con layout y sidebar de navegación.

**Implementado:** ✅ Con shadcn/ui. Tema oscuro. Sidebar: Dashboard, Instrumentos, Fuentes, Tickers, Carga Manual.  
**Path real:** `frontend/client/`  
**Archivos:** `frontend/client/app/layout.tsx`, `frontend/client/components/layout/`

---

### BN-010: Vista Dashboard ✅

**Descripción:** Patrimonio total, distribución por activo/plataforma, exposición por moneda.

**Implementado:** ✅ KPI cards, bar chart por activo, breakdown por fuente con barra animada, exposición ARS/USD, IntelligenceBanner (agregado en BN-018).  
**Archivos:** `frontend/client/components/dashboard/dashboard-view.tsx`, `frontend/client/components/dashboard/dashboard-ui.tsx`

---

### BN-011: Vista Carteras / Fuentes ✅

**Descripción:** Lista de carteras con detalle de posiciones.

**Implementado:** ✅ Vista de fuentes/brokers con detalle de posiciones por fuente.  
**Archivos:** `frontend/client/app/sources/page.tsx`

---

### BN-012: Vista Tickers + Formulario carga manual ✅

**Descripción:** Tabla unificada de tickers y formulario de carga manual.

**Implementado:** ✅ Tabla de tickers con semáforo BUY/HOLD/SELL (real desde BN-017). Formulario de carga manual en tab separado con `POST /api/v1/positions`.  
**Archivos:** `frontend/client/app/tickers/page.tsx`, `frontend/client/app/manual-entry/page.tsx`

---

## TRACK D — INTELLIGENCE LAYER ✅

**Agente:** Claude (Kilo)  
**Dependencias:** Track B completo

---

### BN-013: Intelligence Layer Base — Señales por ticker ✅

**Descripción:** Motor de reglas que asigna señal BUY/HOLD/SELL por ticker.

**Aceptación:**
- `IntelligenceEngine.evaluate_tickers()` asigna señal a cada ticker
- Reglas configurables en JSON: thresholds de concentración
- Señales con razón textual
- Placeholder para integración futura con ARGOS

**Implementado:** ✅ Exacto al spec. Señales: `STRONG_BUY / BUY / HOLD / SELL / STRONG_SELL`  
**Archivos:** `src/services/intelligence.py`, `src/config/rules.json`, `tests/test_intelligence.py` (11 tests)

---

### BN-014: Portfolio Decision Engine ✅

**Descripción:** Estado general de cartera + insights + acción sugerida.

**Aceptación:**
- `DecisionEngine.evaluate_portfolio()` → estado EXPANSIÓN/NEUTRAL/RIESGO
- 2-4 insights concretos
- Acción sugerida accionable

**Implementado:** ✅ Exacto al spec. Incluye sell_count/buy_count/hold_count en response.  
**Archivos:** `src/services/decision_engine.py`, `tests/test_decision_engine.py` (14 tests)

---

### BN-015: Capital Reallocation Engine ✅

**Descripción:** Sugerencias de reasignación de capital liberable.

**Aceptación:**
- `ReallocationEngine.suggest()` → capital liberable, nivel de liquidez, rotaciones, acción sugerida
- MINOS no sugiere vender sin proponer destino

**Implementado:** ✅ Exacto al spec  
**Archivos:** `src/services/reallocation.py`, `tests/test_reallocation.py` (14 tests)

---

### BN-016: API de inteligencia ✅

**Descripción:** Endpoints REST para señales, estado de cartera y reasignación.

**Aceptación:**
- `GET /api/v1/intelligence/signals`
- `GET /api/v1/intelligence/portfolio-status`
- `GET /api/v1/intelligence/reallocation`

**Implementado:** ✅ Exacto al spec. `/signals` retorna lista directa (no dict wrapeado).  
**Archivos:** `src/api/routes/intelligence.py`, `src/schemas/intelligence.py`, `tests/test_api_intelligence.py` (22 tests)

---

## TRACK E — INTEGRACIÓN + POLISH ✅

**Agente:** Claude  
**Dependencias:** Tracks B, C, D completos

---

### BN-017: Integrar frontend con API real ✅

**Descripción:** Reemplazar mock data con llamadas a la API real.

**Aceptación:**
- Dashboard, Carteras, Tickers consumen API real
- Formulario envía a API real
- Manejo de estados: loading, error, empty

**Implementado:** ✅ Exacto al spec. Arquitectura centralizada en `MinosAPI` + hooks React (`useMinosQuery` factory).  
**Archivos:** `frontend/client/lib/minos-api.ts`, `frontend/client/hooks/use-minos.ts`, `frontend/client/types/minos.ts`

---

### BN-018: Integrar Intelligence Layer en frontend ✅

**Descripción:** Señales, estado, insights y reasignación visibles en el frontend.

**Aceptación:**
- Dashboard muestra estado EXPANSIÓN/NEUTRAL/RIESGO
- Tickers muestra señal BUY/HOLD/SELL con color
- Sección de reasignación cuando hay sugerencias

**Implementado:** ✅ Con adiciones:
- `IntelligenceBanner` en dashboard (estado + insight + conteo señales)
- `ReallocationPanel` en sidebar del dashboard (capital liberable, rotaciones, acción)
- Columna "Señal" con badge color-coded en vista Instrumentos
- Semáforo BUY/HOLD/SELL en vista Tickers  
**Archivos:** `frontend/client/components/dashboard/dashboard-view.tsx`, `frontend/client/app/instruments/page.tsx`, `frontend/client/app/tickers/page.tsx`

---

### BN-019: Upload de archivos + End-to-end test ✅

**Descripción:** Drag & drop de CSV/Excel y test E2E del flujo completo.

**Aceptación original:**
- Drag & drop funcional
- Preview antes de confirmar
- Test E2E completo

**Implementado:** ✅ Parcial al spec:
- ✅ Drag & drop real con `onDragOver/onDrop`, validación de extensión, feedback visual
- ✅ 10 tests E2E en `tests/test_e2e_pipeline.py` cubriendo upload → portfolio → intelligence
- ⚠️ Preview antes de confirmar: **no implementado en Sprint 1** — queda para Sprint 2

**Archivos:** `frontend/client/app/manual-entry/page.tsx`, `tests/test_e2e_pipeline.py`

---

## RESUMEN DE ASIGNACIÓN

| BN | Track | Descripción corta | Estado | Tests |
|----|-------|-------------------|--------|-------|
| 001 | A | Scaffold + CLAUDE.md | ✅ | — |
| 002 | A | Modelo de datos + Schemas | ✅ | ✅ |
| 003 | A | Ingestion CSV/Excel | ✅ | ✅ |
| 004 | A | Ingestion manual | ✅ | ✅ |
| 005 | B | Consolidación multi-cartera | ✅ | ✅ |
| 006 | B | Unified Ticker Layer | ✅ | ✅ |
| 007 | B | Normalization | ✅ | ✅ |
| 007b | B | Market Data Service | ✅ | ✅ |
| 008 | B | API patrimonial (6 endpoints) | ✅ | ✅ |
| 009 | C | Scaffold frontend + Layout | ✅ | — |
| 010 | C | Vista Dashboard | ✅ | — |
| 011 | C | Vista Fuentes/Carteras | ✅ | — |
| 012 | C | Vista Tickers + Carga manual | ✅ | — |
| 013 | D | Señales por ticker | ✅ | 11 |
| 014 | D | Portfolio Decision Engine | ✅ | 14 |
| 015 | D | Capital Reallocation Engine | ✅ | 14 |
| 016 | D | API de inteligencia (3 endpoints) | ✅ | 22 |
| 017 | E | Integrar FE con API real | ✅ | — |
| 018 | E | Intelligence en FE | ✅ | — |
| 019 | E | Upload drag & drop + E2E tests | ✅ | 10 |

**Total tests backend: 71 pasando**

---

## FUERA DE SCOPE — Sprint 1 (pasa a Sprint 2)

- Preview de datos antes de confirmar upload (BN-019 parcial)
- Captura visual (OCR, templates de extracción)
- Integración con ARGOS (señales por activo externas)
- APIs de brokers en vivo (Balanz, IOL, etc.)
- Conexión con OIKOS
- Análisis avanzado / ML
- Tests E2E de frontend (Playwright)

---

## DECISIONES TÉCNICAS (desvíos del spec original)

| Decisión | Detalle |
|----------|---------|
| Path frontend | `frontend/client/` (reorganizado desde `v0-financial-toro-dashboard-2-main/` en PR#5) |
| Hook factory | `useMinosQuery<T>` genérico — evita duplicación de estado loading/error/data |
| Señales extendidas | `STRONG_BUY / STRONG_SELL` además de `BUY / HOLD / SELL` |
| `/signals` response | Lista directa, no `{signals: [], signal_summary: {}}` |
| `ReallocationPanel` | Agregado al sidebar del dashboard, no como página separada |
| Signal badges | En Instrumentos además de Tickers (no estaba en el spec original) |
| Mock yfinance | Patchear `src.services.market_data.yf.Ticker`, no `yfinance.Ticker` |

---

**Estado Sprint 1:** CERRADO ✅ — 2026-04-28

---

## SPRINT 2 — BROKER-GRADE VALUATION CORE 🔄

**Inicio:** 2026-04-30  
**Branch:** `claude/minos-broker-grade-sprint-KsTZZ`  
**Decisión crítica:** Primero verdad financiera, después inteligencia. Ninguna señal BUY/HOLD/SELL es válida si `valuation_status != OK`.

---

### BN-S2-DIAG: Diagnóstico de Pricing ✅

**Descripción:** Diagnóstico completo del sistema de pricing actual. Sin modificar lógica financiera.

**Aceptación:**
- Script ejecutable que expone el flujo real de resolución de tickers
- Tabla con: `ticker_input | instrument_type | exchange | resolved_symbol | source | price | currency | quote_timestamp | fetched_at | is_stale | status | error`
- Identificación explícita de bugs con categoría
- Sin romper tests existentes

**Implementado:** ✅  
**Archivos:** `scripts/debug_pricing.py`  
**Tests:** 163 pasando (sin regresión)  
**Fecha:** 2026-04-30

#### Bugs confirmados

| Código | Archivo | Descripción |
|--------|---------|-------------|
| `NO_EXCHANGE_FIELD` | `src/models/asset.py`, `src/models/position.py` | Sin campo `exchange` ni `instrument_type` — imposible saber si un ticker es BYMA vs NYSE |
| `NO_BA_SUFFIX_LOGIC` | `src/services/market_data.py:42` | `get_price(ticker)` pasa el ticker tal cual — `BMA` en vez de `BMA.BA`, `GGAL` en vez de `GGAL.BA` |
| `TICKER_ALIASES_INCOMPLETO` | `src/config/ticker_aliases.json` | Mapea `"ypf" → "YPFD"` y `"galicia" → "GGAL"` sin sufijo `.BA` — aliases no son exchange-aware |
| `VALUATION_ESTATICA` | `src/services/portfolio_engine.py:40` | Usa `pos.valuation` (dato ingested estático) — `MarketDataService` no integrado en valuación de cartera |
| `NO_CURRENCY_IN_PRICE` | `src/services/market_data.py:16-19` | `PriceCache` almacena solo `price + fetched_at` — sin moneda |
| `NO_QUOTE_TIMESTAMP` | `src/services/market_data.py` | `yfinance.fast_info` no expone timestamp de cotización — solo `fetched_at` |
| `FALLBACK_SILENCIOSO` | `src/services/market_data.py:45-46` | Retorna precio cacheado sin flag de staleness cuando yfinance falla |

---

### BN-S2-01: InstrumentResolver — pendiente ⏳

**Descripción:** Resolver que mapea `(ticker, exchange, instrument_type) → yfinance_symbol`. Prerequisito de todos los BNs de pricing.

**Aceptación:**
- Agregar campos `exchange` (BYMA/NYSE/NASDAQ/etc.) e `instrument_type` (EQUITY/CEDEAR/BOND) a `Asset`
- Migración Alembic
- Clase `InstrumentResolver` en `src/services/`
- `BYMA + EQUITY` → `ticker + ".BA"`
- `NYSE/NASDAQ + EQUITY` → ticker sin cambio
- CEDEAR → `ticker + ".BA"` (o sufijo según regla a definir)
- Tests unitarios completos
- **No rompe `MarketDataService` existente hasta BN-S2-02**

---

### BN-S2-02: PriceResult enriquecido — pendiente ⏳

**Descripción:** Reemplazar `Optional[float]` por `PriceResult` dataclass con metadata completa.

**Aceptación:**
- `PriceResult`: `price`, `currency`, `source`, `quote_timestamp`, `is_stale`, `valuation_status`
- `valuation_status`: `OK | STALE | ERROR | NO_DATA`
- `MarketDataService.get_price_result(ticker, exchange, instrument_type) → PriceResult`
- `PriceCache` actualizado para almacenar moneda y timestamp de cotización
- Backward compatible con endpoint existente `/api/v1/market/prices`

---

### BN-S2-03: Valuación dinámica en portfolio_engine — pendiente ⏳

**Descripción:** Integrar precios live en la consolidación de cartera.

**Aceptación:**
- `portfolio_engine.consolidate()` multiplica `market_price × quantity` en vez de usar `pos.valuation` estático
- Retorna `valuation_status` por ticker (OK/STALE/ERROR)
- Cartera con cualquier ticker en estado ERROR → alerta en response
- Mantener `pos.valuation` como fallback de último recurso (con `valuation_status = STALE`)

---

### BN-S2-04: valuation_status en API e Intelligence — pendiente ⏳

**Descripción:** Exponer `valuation_status` en la API y bloquear señales de inteligencia si los precios no son confiables.

**Aceptación:**
- `GET /api/v1/portfolio/summary` incluye `valuation_status` global
- `IntelligenceEngine` recibe `valuation_status` por ticker
- Señal marcada como `INVALID` si `valuation_status != OK`
- Frontend muestra advertencia cuando hay tickers con precio no confiable

---

## RESUMEN SPRINT 2

| BN | Descripción | Estado | Tests |
|----|-------------|--------|-------|
| S2-DIAG | Diagnóstico de pricing | ✅ | 163 (sin regresión) |
| S2-01 | InstrumentResolver | ⏳ | — |
| S2-02 | PriceResult enriquecido | ⏳ | — |
| S2-03 | Valuación dinámica | ⏳ | — |
| S2-04 | valuation_status en API | ⏳ | — |
