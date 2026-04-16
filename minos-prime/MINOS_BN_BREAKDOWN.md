# MINOS PRIME — BN BREAKDOWN (Bloques Negros)

**Fase:** Ejecución (Post Gate-2)  
**Generado por:** Claude (CTO)  
**Estado:** APROBADO por Tori (Gate-2 cerrado)  
**Repo de ejecución:** github.com/TORIBUSTOS/MINOS-v2  
**Stack:** Python 3.12+ / FastAPI (BE) + React / Next.js / TailwindCSS (FE) + SQLite (MVP) / PostgreSQL (prod)

---

## Resumen de Tracks

```
TRACK A ─── Data Layer ──────────────── [Claude]     ── BN-001 a BN-004
TRACK B ─── Portfolio Engine ────────── [Claude]     ── BN-005 a BN-008
TRACK C ─── Frontend Base ──────────── [Gemini/AG]  ── BN-009 a BN-012  (paralelo con B)
TRACK D ─── Intelligence Layer ──────── [Claude]     ── BN-013 a BN-016
TRACK E ─── Integración + Polish ────── [Ambos]     ── BN-017 a BN-019
```

```
Dependencias:

A ──→ B ──→ D ──→ E
A ──→ C ─────────→ E
      ↑             ↑
      B y C van en paralelo
```

---

## TRACK A — DATA LAYER (Cimiento)

**Agente:** Claude  
**Dependencias:** Ninguna (arranca primero)

---

### BN-001: Scaffold del proyecto + CLAUDE.md

**Descripción:** Inicializar el repo MINOS-v2 con la estructura de carpetas, CLAUDE.md, dependencias base, y configuración del proyecto.

**Aceptación:**
- Repo tiene estructura: `src/`, `tests/`, `docs/`, `scripts/`
- CLAUDE.md en la raíz con stack, comandos, convenciones y boundaries
- `pyproject.toml` o `requirements.txt` con dependencias iniciales (FastAPI, SQLAlchemy, Pydantic, pytest)
- `.gitignore` configurado
- `README.md` apuntando a docs de Trinity

**Verificar:** `pip install -r requirements.txt` sin errores  
**Archivos:** CLAUDE.md, README.md, requirements.txt, .gitignore, estructura de carpetas  

---

### BN-002: Modelo de datos + Schemas

**Descripción:** Definir los modelos SQLAlchemy y schemas Pydantic para el dominio patrimonial: fuentes, carteras, activos, posiciones, cargas.

**Aceptación:**
- Modelos: `Source`, `Portfolio`, `Asset`, `Position`, `LoadRecord`
- Cada posición tiene: fuente, cartera, ticker, cantidad, moneda, valuación, fecha, tipo_carga, estado_validacion
- Schemas Pydantic para input/output de cada modelo
- Relaciones: Source → Portfolio → Position; Asset como entidad independiente con ticker unificado
- Migración inicial que crea las tablas

**Verificar:** `pytest tests/test_models.py` pasa — tests de creación, relaciones y constraints  
**Archivos:** src/models/, src/schemas/, tests/test_models.py, alembic/ o init_db.py  

---

### BN-003: Data Ingestion — CSV/Excel

**Descripción:** Implementar el ingestion layer para carga desde archivos CSV y Excel. Parsear, detectar columnas, mapear a modelo de datos, validar antes de persistir.

**Aceptación:**
- Endpoint `POST /api/v1/ingest/file` acepta CSV y XLSX
- Detecta columnas automáticamente (ticker, cantidad, moneda, etc.)
- Valida datos antes de guardar (no persiste basura)
- Crea Source y Portfolio si no existen
- Retorna resumen: registros procesados, rechazados, warnings
- Nunca guarda sin validación

**Verificar:** `pytest tests/test_ingestion.py` — test con CSV de ejemplo (5-10 posiciones de prueba tipo Balanz/IOL)  
**Archivos:** src/services/ingestion.py, src/api/routes/ingest.py, tests/test_ingestion.py, tests/fixtures/sample_portfolio.csv  

---

### BN-004: Data Ingestion — Carga manual

**Descripción:** Endpoint para agregar posiciones individuales manualmente (formulario).

**Aceptación:**
- Endpoint `POST /api/v1/positions` con body JSON
- Validación Pydantic del input
- Asocia a Source + Portfolio existente o crea nuevos
- tipo_carga = "manual"
- Endpoint `GET /api/v1/positions` lista posiciones con filtros (por cartera, por fuente)

**Verificar:** `pytest tests/test_positions.py` — CRUD básico  
**Archivos:** src/api/routes/positions.py, tests/test_positions.py  

---

## TRACK B — PORTFOLIO ENGINE (Consolidación)

**Agente:** Claude  
**Dependencias:** Track A completo

---

### BN-005: Portfolio Engine — Consolidación multi-cartera

**Descripción:** Servicio que consolida todas las posiciones en una vista patrimonial total: suma por activo, por plataforma, por moneda.

**Aceptación:**
- Servicio `PortfolioEngine.consolidate()` retorna patrimonio total
- Distribución por activo (% del total)
- Distribución por plataforma/fuente
- Exposición por moneda (ARS vs USD vs otros)
- Mantiene trazabilidad: cada número se puede rastrear a su cartera de origen

**Verificar:** `pytest tests/test_portfolio_engine.py` — con datos de 2+ carteras, 2+ fuentes, 2+ monedas  
**Archivos:** src/services/portfolio_engine.py, tests/test_portfolio_engine.py  

---

### BN-006: Unified Ticker Layer

**Descripción:** Capa que unifica tickers entre carteras. Elimina duplicados por símbolo, detecta presencia en múltiples carteras, genera tabla unificada.

**Aceptación:**
- `UnifiedTickerService.unify()` retorna lista de tickers únicos
- Cada ticker tiene: símbolo, presencia (en cuántas carteras), cuáles carteras, señal (placeholder por ahora)
- MELI en Balanz1 + MELI en Balanz2 = 1 entrada con presencia=2
- No suma nominales entre carteras (regla del spec)

**Verificar:** `pytest tests/test_unified_ticker.py` — test con tickers duplicados entre carteras  
**Archivos:** src/services/unified_ticker.py, tests/test_unified_ticker.py  

---

### BN-007: Processing & Normalization

**Descripción:** Capa de limpieza y normalización de datos entrantes. Estandariza nombres de tickers, detecta duplicados dentro de una misma carga, normaliza moneda.

**Aceptación:**
- Normalización de tickers: "MELI", "meli", "MercadoLibre" → "MELI"
- Diccionario de aliases configurable (JSON)
- Detección de duplicados dentro de una misma carga
- Normalización de moneda: "USD", "usd", "dólares" → "USD"
- Log de transformaciones aplicadas (trazabilidad)

**Verificar:** `pytest tests/test_normalization.py` — test con datos sucios  
**Archivos:** src/services/normalization.py, src/config/ticker_aliases.json, tests/test_normalization.py  

---

### BN-007b: Market Data Service (Precios en vivo)

**Descripción:** Servicio que consulta precios de mercado actuales vía yfinance, actualiza valuaciones de posiciones, y mantiene cache para no saturar la fuente.

**Aceptación:**
- Servicio `MarketDataService.refresh_prices()` consulta yfinance para todos los tickers en cartera
- Soporta tickers US (MELI, NVDA, TSLA) y MERVAL con sufijo .BA (YPFD.BA, GGAL.BA)
- Cache de precios con TTL configurable (default 15 minutos)
- Si cache vigente → devuelve cache, no pega a Yahoo
- Si cache expirado → consulta Yahoo, actualiza cache y recalcula valuaciones
- Fallback: si Yahoo no responde, mantiene última valuación conocida + warning
- Endpoint `POST /api/v1/market/refresh` → fuerza refresh manual
- Endpoint `GET /api/v1/market/prices` → precios actuales con timestamp de última actualización
- Al abrir dashboard → auto-refresh si cache expirado (transparente para el usuario)

**Verificar:** `pytest tests/test_market_data.py` — test con tickers reales, test de cache, test de fallback  
---

### BN-008: API de consulta patrimonial

**Descripción:** Endpoints REST para consultar el patrimonio consolidado, distribución, y vista unificada de tickers.

**Aceptación:**
- `GET /api/v1/portfolio/summary` → patrimonio total, distribución, exposición
- `GET /api/v1/portfolio/by-source` → desglose por fuente/plataforma
- `GET /api/v1/portfolio/by-currency` → exposición por moneda
- `GET /api/v1/tickers/unified` → tabla unificada de tickers
- `GET /api/v1/portfolios` → lista de carteras con resumen cada una
- Todos los endpoints usan schemas Pydantic para response

**Verificar:** `pytest tests/test_api_portfolio.py` — test de cada endpoint con datos de prueba  
**Archivos:** src/api/routes/portfolio.py, src/api/routes/tickers.py, tests/test_api_portfolio.py  

---

## TRACK C — FRONTEND BASE (Paralelo con Track B)

**Agente:** Gemini/AG  
**Dependencias:** Track A completo (necesita la API de BN-004 mínimo). Puede arrancar con mock data mientras Track B avanza.

---

### BN-009: Scaffold frontend + Layout base

**Descripción:** Inicializar el proyecto frontend con Next.js + TailwindCSS. Layout principal con sidebar de navegación y área de contenido.

**Aceptación:**
- Proyecto Next.js inicializado con TypeScript y TailwindCSS
- Layout con sidebar: Dashboard, Carteras, Tickers, Cargar Datos
- Tema oscuro como default (coherente con estética TORO)
- Componentes base: PageHeader, Card, DataTable (reutilizables)
- Responsive (mobile-friendly)

**Verificar:** `npm run build` sin errores, navegación entre secciones funciona  
**Archivos:** src/app/, src/components/layout/, src/components/ui/  

---

### BN-010: Vista Dashboard (patrimonio consolidado)

**Descripción:** Pantalla principal que muestra el patrimonio total, distribución por activo, distribución por plataforma, exposición por moneda.

**Aceptación:**
- Número grande: patrimonio total en USD (y equivalente ARS)
- Gráfico de distribución por activo (donut o bar)
- Gráfico de distribución por plataforma
- Indicador de exposición por moneda (% USD vs % ARS)
- Consume `GET /api/v1/portfolio/summary` (o mock data si API no lista)

**Verificar:** Renderiza con datos de prueba, gráficos visibles, responsive  
**Archivos:** src/app/dashboard/, src/components/charts/  

---

### BN-011: Vista Carteras (por cartera individual)

**Descripción:** Pantalla que lista todas las carteras y permite ver el detalle de cada una: posiciones, valuación, composición.

**Aceptación:**
- Lista de carteras con nombre, fuente, cantidad de posiciones, valuación total
- Click en cartera → detalle con tabla de posiciones (ticker, cantidad, moneda, valuación, % del total)
- Consume `GET /api/v1/portfolios` y `GET /api/v1/positions?portfolio_id=X`

**Verificar:** Navegación lista → detalle funciona, tabla de posiciones renderiza  
**Archivos:** src/app/portfolios/, src/components/tables/  

---

### BN-012: Vista Tickers Unificados + Formulario de carga manual

**Descripción:** Dos pantallas: tabla unificada de tickers (presencia, carteras, señal) y formulario para agregar posiciones manualmente.

**Aceptación:**
- Tabla unificada: ticker, presente en N carteras, cuáles, estado (placeholder)
- Formulario de carga manual: ticker, cantidad, moneda, cartera, fuente
- Validación de formulario en frontend antes de submit
- Consume `GET /api/v1/tickers/unified` y `POST /api/v1/positions`

**Verificar:** Tabla renderiza, formulario envía y la posición aparece en la lista  
**Archivos:** src/app/tickers/, src/app/load/  

---

## TRACK D — INTELLIGENCE LAYER

**Agente:** Claude  
**Dependencias:** Track B completo (necesita datos consolidados)

---

### BN-013: Intelligence Layer Base — Señales por ticker

**Descripción:** Motor de reglas simples que asigna señal BUY/HOLD/SELL a cada ticker basado en thresholds configurables.

**Aceptación:**
- Servicio `IntelligenceEngine.evaluate_tickers()` asigna señal a cada ticker
- Reglas v1 configurables en JSON: thresholds de concentración, exposición, cambio
- Señales: BUY / HOLD / SELL con razón (ej: "concentración > 30%")
- Placeholder para integración futura con ARGOS (interface definida)

**Verificar:** `pytest tests/test_intelligence.py` — test con cartera concentrada → señal correcta  
**Archivos:** src/services/intelligence.py, src/config/rules.json, tests/test_intelligence.py  

---

### BN-014: Portfolio Decision Engine

**Descripción:** Interpreta la cartera completa y genera estado general + insights + acción sugerida.

**Aceptación:**
- `DecisionEngine.evaluate_portfolio()` retorna:
  - Estado: EXPANSIÓN / NEUTRAL / RIESGO
  - Insights: 2-4 observaciones concretas (ej: "70% en un solo activo")
  - Acción sugerida: texto accionable (ej: "Reducir exposición a MELI")
- Evalúa: concentración, exposición por moneda, coherencia, activos débiles vs fuertes
- Reglas configurables en JSON

**Verificar:** `pytest tests/test_decision_engine.py` — test con cartera concentrada → RIESGO; cartera diversificada → NEUTRAL  
**Archivos:** src/services/decision_engine.py, tests/test_decision_engine.py  

---

### BN-015: Capital Reallocation Engine

**Descripción:** Sugiere qué hacer con capital disponible o liberable cuando hay activos en SELL o liquidez ociosa.

**Aceptación:**
- `ReallocationEngine.suggest()` se activa con activos en SELL o liquidez alta
- Retorna: capital liberable, nivel de liquidez, oportunidades, acción sugerida
- Opciones: reforzar posiciones fuertes, rotar, mantener liquidez, nuevas entradas
- Principio: MINOS no sugiere vender sin proponer destino del capital

**Verificar:** `pytest tests/test_reallocation.py` — test con activo SELL → sugerencia de destino  
**Archivos:** src/services/reallocation.py, tests/test_reallocation.py  

---

### BN-016: API de inteligencia

**Descripción:** Endpoints REST para consultar señales, estado de cartera, e insights.

**Aceptación:**
- `GET /api/v1/intelligence/signals` → señales por ticker con razón
- `GET /api/v1/intelligence/portfolio-status` → estado + insights + acción
- `GET /api/v1/intelligence/reallocation` → sugerencias de reasignación
- Schemas Pydantic para todos los responses

**Verificar:** `pytest tests/test_api_intelligence.py`  
**Archivos:** src/api/routes/intelligence.py, tests/test_api_intelligence.py  

---

## TRACK E — INTEGRACIÓN + POLISH

**Agente:** Claude + Gemini  
**Dependencias:** Tracks B, C, D completos

---

### BN-017: Integrar frontend con API real (Claude + Gemini)

**Descripción:** Reemplazar mock data en frontend con llamadas a la API real. Conectar todas las vistas.

**Aceptación:**
- Dashboard consume API real de portfolio/summary
- Carteras consume API real de portfolios + positions
- Tickers consume API real de tickers/unified
- Formulario de carga envía a API real
- Manejo de estados: loading, error, empty

**Verificar:** Flujo completo: cargar CSV → ver en dashboard → ver en carteras → ver en tickers  
**Archivos:** src/app/ (todos los pages), src/lib/api.ts  

---

### BN-018: Integrar Intelligence Layer en frontend (Gemini)

**Descripción:** Mostrar señales, estado de cartera, insights y sugerencias de reasignación en el dashboard y en la vista de tickers.

**Aceptación:**
- Dashboard muestra: estado de cartera (EXPANSIÓN/NEUTRAL/RIESGO), insights, acción sugerida
- Tabla de tickers muestra señal por ticker (BUY/HOLD/SELL) con color
- Sección de reasignación visible cuando hay sugerencias activas
- Consume APIs de intelligence

**Verificar:** Cargar datos → dashboard muestra estado e insights coherentes con los datos  
**Archivos:** src/app/dashboard/, src/app/tickers/, src/components/intelligence/  

---

### BN-019: Upload de archivos + End-to-end test (Claude)

**Descripción:** Pantalla de upload de CSV/Excel con drag & drop, preview de datos antes de confirmar, y test end-to-end del flujo completo.

**Aceptación:**
- Drag & drop de archivos CSV/XLSX
- Preview: muestra tabla con datos parseados antes de guardar
- Botón "Confirmar" persiste, "Cancelar" descarta
- Resumen post-carga: N registros procesados, N warnings, N rechazados
- Test E2E: upload CSV → ver en dashboard → señales correctas → insights coherentes

**Verificar:** Test manual del flujo completo + `pytest tests/test_e2e.py` si aplica  
**Archivos:** src/app/load/, src/components/upload/, tests/test_e2e.py  

---

## RESUMEN DE ASIGNACIÓN

| BN | Track | Descripción corta | Agente | Depende de |
|----|-------|--------------------|--------|------------|
| 001 | A | Scaffold + CLAUDE.md | Claude | — |
| 002 | A | Modelo de datos + Schemas | Claude | 001 |
| 003 | A | Ingestion CSV/Excel | Claude | 002 |
| 004 | A | Ingestion manual | Claude | 002 |
| 005 | B | Consolidación multi-cartera | Claude | 003, 004 |
| 006 | B | Unified Ticker Layer | Claude | 005 |
| 007 | B | Normalization | Claude | 002 |
| 007b | B | Market Data Service (precios vivos) | Claude | 006 |
| 008 | B | API de consulta patrimonial | Claude | 005, 006, 007, 007b |
| 009 | C | Scaffold frontend + Layout | Gemini | 001 |
| 010 | C | Vista Dashboard | Gemini | 009 |
| 011 | C | Vista Carteras | Gemini | 009 |
| 012 | C | Vista Tickers + Carga manual | Gemini | 009 |
| 013 | D | Señales por ticker | Claude | 006, 007b |
| 014 | D | Portfolio Decision Engine | Claude | 005, 013 |
| 015 | D | Capital Reallocation Engine | Claude | 014 |
| 016 | D | API de inteligencia | Claude | 013, 014, 015 |
| 017 | E | Integrar FE con API real | Ambos | 008, 009-012 |
| 018 | E | Integrar Intelligence en FE | Gemini | 016, 017 |
| 019 | E | Upload + E2E test | Claude | 017, 018 |

---

## MAPA DE PARALELISMO

```
Sesión 1:  BN-001 (Claude)
Sesión 2:  BN-002 (Claude)
Sesión 3:  BN-003 + BN-004 (Claude)  |  BN-009 (Gemini — arranca FE)
Sesión 4:  BN-005 + BN-007 (Claude)  |  BN-010 + BN-011 (Gemini — vistas con mock)
Sesión 5:  BN-006 + BN-007b (Claude) |  BN-012 (Gemini — tickers + form)
Sesión 6:  BN-008 + BN-013 (Claude)  |  BN-017 (Gemini — conectar API real)
Sesión 7:  BN-014 + BN-015 (Claude)  |  BN-018 (Gemini — intelligence en FE)
Sesión 8:  BN-016 + BN-019 (Claude)  — E2E final
```

**Total: 20 Bloques Negros en 8 sesiones**  
**Con paralelismo Claude + Gemini: 6-7 sesiones de calendar time**

---

## FUERA DE SCOPE (Sprint 2)

- Captura visual (OCR, templates de extracción)
- Integración con ARGOS (señales por activo externas)
- APIs de brokers en vivo (Balanz, IOL, etc.)
- Conexión con OIKOS
- Análisis avanzado / ML

---

**Estado:** APROBADO por Tori (Gate-2 cerrado)  
**Próximo paso:** Subir a Trinity repo + MINOS-v2 repo → Claude arranca BN-001 en Claude Code
