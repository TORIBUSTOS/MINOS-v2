# MINOS PRIME — BN PIPELINE

**Última actualización:** 2026-04-22
**Agente:** Kilo (ejecutando BN en lugar de Claude)

---

## Pipeline Completo

```
TRACK A ─── Data Layer ──────────────────────────── [COMPLETO] ✅
TRACK B ─── Portfolio Engine ───────────────────── [COMPLETO] ✅
TRACK C ─── Frontend Base ───────────────────────── [COMPLETO] ✅
TRACK D ─── Intelligence Layer ─────────────────── [PENDIENTE] ⏳
TRACK E ─── Integración + Polish ───────────────── [PENDIENTE] ⏳
```

---

## Detalle por BN

### TRACK A — Data Layer ✅

| BN | Descripción | Estado | Archivos |
|----|-------------|--------|----------|
| BN-001 | Scaffold + CLAUDE.md | ✅ COMPLETO | CLAUDE.md, README.md, requirements.txt, .gitignore |
| BN-002 | Modelo de datos + Schemas | ✅ COMPLETO | `src/models/`, `src/schemas/` |
| BN-003 | Ingestion CSV/Excel | ✅ COMPLETO | `src/services/ingestion.py`, `src/api/routes/ingest.py` |
| BN-004 | Carga manual | ✅ COMPLETO | `src/api/routes/positions.py` |

---

### TRACK B — Portfolio Engine ✅

| BN | Descripción | Estado | Archivos |
|----|-------------|--------|----------|
| BN-005 | Consolidación multi-cartera | ✅ COMPLETO | `src/services/portfolio_engine.py` |
| BN-006 | Unified Ticker Layer | ✅ COMPLETO | `src/services/unified_ticker.py` |
| BN-007 | Normalization | ✅ COMPLETO | `src/services/normalization.py` |
| BN-007b | Market Data Service | ✅ COMPLETO | `src/services/market_data.py` |
| BN-008 | API de consulta patrimonial | ✅ COMPLETO | `src/api/routes/portfolio.py`, `src/api/routes/tickers.py` |

---

### TRACK C — Frontend Base ✅

| BN | Descripción | Estado | Archivos |
|----|-------------|--------|----------|
| BN-009 | Scaffold frontend + Layout | ✅ COMPLETO | `v0-financial-toro-dashboard-2-main/app/` |
| BN-010 | Vista Dashboard | ✅ COMPLETO | `v0-financial-toro-dashboard-2-main/app/page.tsx` |
| BN-011 | Vista Carteras | ✅ COMPLETO | `v0-financial-toro-dashboard-2-main/app/instruments/` |
| BN-012 | Vista Tickers + Carga manual | ✅ COMPLETO | `v0-financial-toro-dashboard-2-main/app/tickers/` |

---

### TRACK D — Intelligence Layer ✅ (Completado por Kilo)

| BN | Descripción | Estado | Archivos |
|----|-------------|--------|----------|
| BN-013 | Intelligence Layer — Señales | ✅ COMPLETO | `src/services/intelligence.py`, `src/config/rules.json`, `tests/test_intelligence.py` |
| BN-014 | Portfolio Decision Engine | ✅ COMPLETO | `src/services/decision_engine.py`, `tests/test_decision_engine.py` |
| BN-015 | Capital Reallocation Engine | ✅ COMPLETO | `src/services/reallocation.py`, `tests/test_reallocation.py` |
| BN-016 | API de inteligencia | ✅ COMPLETO | `src/api/routes/intelligence.py`, `src/schemas/intelligence.py` |

---

### TRACK E — Integración + Polish 🔄

| BN | Descripción | Estado | Dependencias | Archivos |
|----|-------------|--------|--------------|----------|
| BN-017 | Integrar FE con API real | ✅ COMPLETO | BN-008, BN-009-012 | `use-minos.ts`, `minos-api.ts`, `types/minos.ts`, `intelligence-panels.tsx` |
| BN-018 | Integrar Intelligence en FE | ⏳ PENDIENTE | BN-016, BN-017 | Dashboard + Tickers |
| BN-019 | Upload + E2E test | ⏳ PENDIENTE | BN-017, BN-018 | Drag & drop + tests |

---

## Resumen

```
✅ Completados: 17/19 BN (89%)
⏳ Pendientes:   2/19 BN (11%)
```

---

## BN-016 — Completado

**Fecha:** 2026-04-23
**Agente:** Kilo (TDD workflow)

**Archivos creados:**
- `src/api/routes/intelligence.py` — 3 endpoints REST
- `src/schemas/intelligence.py` — Schemas Pydantic para responses
- `src/main.py` — Actualizado con router de intelligence

**Endpoints implementados:**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/intelligence/signals` | Señales por ticker + resumen |
| GET | `/api/v1/intelligence/portfolio-status` | Estado + insights + acción |
| GET | `/api/v1/intelligence/reallocation` | Sugerencias de reasignación |

**Validación con datos de prueba:**
```
Cartera: MELI 50%, GGAL 20%, PAMP/EDN/BMA 10% c/u — todo Balanz, 100% USD

GET /signals:
  MELI  → STRONG_SELL (50%)
  PAMP  → HOLD (10%)
  EDN   → HOLD (10%)
  GGAL  → HOLD (20%)
  BMA   → HOLD (10%)

GET /portfolio-status:
  Status: RIESGO
  Insights: ["MELI 50% concentración", "100% USD exposición", "única fuente Balanz"]
  Action: "Reducir MELI y diversificar"

GET /reallocation:
  Capital liberable: $5,000 (MELI STRONG_SELL)
  Oportunidades: 0 (sin BUY)
  Sugerencia: "Mantener en liquidez hasta identificar oportunidad"
```

✅ Syntax OK + lógica validada con test manual

---

## TRACK D — Completado ✅

El Intelligence Layer está completo:

```
BN-013: IntelligenceEngine    → señales por ticker (BUY/HOLD/SELL)
BN-014: DecisionEngine         → estado de cartera (EXPANSIÓN/NEUTRAL/RIESGO)
BN-015: ReallocationEngine    → sugerencias de reasignación
BN-016: API REST               → expone todo en 3 endpoints
```

**Flujo de datos:**
```
1. consolidate()     → portfolio_data
2. unify()           → unified_tickers
3. IntelligenceEngine.evaluate_tickers() → signals
4. IntelligenceEngine.get_portfolio_signal_summary() → signal_summary
5. signal_summary + portfolio_data → DecisionEngine.evaluate_portfolio() → status
6. signal_summary + portfolio_data → ReallocationEngine.suggest() → reallocation
```

---

## Próximos BN (Track E)

**BN-017:** Integrar frontend con API real
**BN-018:** Integrar Intelligence Layer en frontend
**BN-019:** Upload + E2E test

```
BN-017 ⏳ → BN-018 ⏳ → BN-019 ⏳
```

¿Continuamos con BN-017? (Integrar frontend con API real)

---

## Notas

- Track D (Intelligence Layer) es el siguiente bloque a ejecutar
- BN-013 no requiere cambios en el frontend existente
- Interfaz con ARGOS queda como placeholder (interface definida, implementación futura)
- Una vez completado D, se puede ejecutar E (integración final)