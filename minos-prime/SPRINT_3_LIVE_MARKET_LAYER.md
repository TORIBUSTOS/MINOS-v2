# MINOS Sprint 3 — Live Market Layer

**Sprint:** Live Market Layer  
**Estado:** CERRADO  
**Fecha de formalizacion:** 2026-05-10  
**Fecha de cierre:** 2026-05-10  
**Objetivo rector:** convertir la valuacion broker-grade de Sprint 2 en una capa operativa viva, separando movimiento de mercado, frescura de datos e inteligencia accionable.

---

## 0. Resultado esperado

Al cerrar Sprint 3, MINOS debe mostrar no solo cuanto vale la cartera, sino tambien como se esta moviendo durante la rueda:

- variacion intradiaria por instrumento
- impacto diario por posicion y total cartera
- estado de dato de mercado (`LIVE`, `CACHE`, `STALE`, `UNAVAILABLE`)
- resumen de sesion visible en dashboard
- tabla de instrumentos con movimiento diario legible
- heatmap de rendimiento diario
- tests backend/frontend suficientes para no romper valuacion ni senales

---

## 1. Regla central

Sprint 3 no cambia la tesis de inteligencia. Agrega contexto operativo de mercado.

```text
pricing trazable -> movimiento diario -> impacto cartera -> UI live
```

Las senales `BUY/HOLD/SELL` siguen subordinadas a `valuation_status`. El estado `LIVE/CACHE/STALE` describe frescura del dato de mercado, no recomendacion de inversion.

---

## 2. Cadena de ejecucion

```text
BN-S3-01 -> BN-S3-02 -> BN-S3-03 -> BN-S3-04 -> BN-S3-05 -> BN-S3-06
```

Ningun BN debe avanzar si el anterior no cumple su criterio de aceptacion minimo.

---

## 3. Fuera de scope

- No integrar brokers reales todavia.
- No agregar dependencias nuevas sin aprobacion.
- No implementar ML, prediccion o scoring avanzado.
- No cambiar modelos persistentes salvo aprobacion explicita.
- No reescribir UI completa.
- No mezclar ARS/USD sin conversion explicita.
- No usar precios, variaciones o estados simulados en rutas productivas.

---

## BN-S3-01 — Quote intradiario enriquecido

**Tipo:** Backend / market data  
**Depende de:** Sprint 2 cerrado  
**Archivos esperados:** `src/services/market_data.py`, tests de market data, schemas/tipos internos si aplica.

### Objetivo

Extender el resultado de pricing para exponer movimiento intradiario y frescura del dato.

### Campos objetivo

```text
previous_close
day_change
day_change_pct
market_state
data_freshness
last_market_time
```

Estados sugeridos:

```text
LIVE | CACHE | STALE | UNAVAILABLE
```

### Criterio de aceptacion

- `MarketDataService` mantiene `PriceResult` trazable de Sprint 2.
- No rompe consumidores actuales de `price`, `currency`, `resolved_symbol`, `status`.
- Si yfinance no entrega `previous_close`, el estado queda explicito y no inventa variacion.
- Tests cubren quote con variacion disponible y quote sin variacion disponible.

---

## BN-S3-02 — Impacto diario en PortfolioEngine

**Tipo:** Backend / portfolio core  
**Depende de:** BN-S3-01  
**Archivos esperados:** `src/services/portfolio_engine.py`, tests de portfolio engine.

### Objetivo

Calcular impacto diario por instrumento y total cartera usando quote intradiario.

### Campos objetivo

```text
day_change
day_change_pct
daily_pnl
daily_pnl_pct
daily_portfolio_impact
daily_impact_status
```

### Formula base

```text
daily_pnl = quantity * day_change
daily_portfolio_impact = daily_pnl / total_market_value * 100
```

### Criterio de aceptacion

- Usa `Decimal` para dinero.
- No calcula impacto si falta precio actual o cierre anterior confiable.
- Expone estado explicito cuando el impacto no es calculable.
- Mantiene `valuation_status` y `valuation_trace` de Sprint 2.

---

## BN-S3-03 — Contrato API Live Market

**Tipo:** Backend / API contract  
**Depende de:** BN-S3-02  
**Archivos esperados:** rutas portfolio/market, schemas, tests API.

### Objetivo

Exponer una capa API coherente para UI live sin duplicar logica financiera.

### Opciones validas

1. Extender `GET /api/v1/portfolio/summary` con campos live.
2. Extender `GET /api/v1/market/prices` con frescura y variacion.
3. Crear endpoint dedicado `GET /api/v1/market/session-summary` si el resumen no encaja limpio en contratos existentes.

### Criterio de aceptacion

- API retorna datos suficientes para session bar y tabla de instrumentos.
- Los nombres de campos son estables y documentados.
- Tests verifican respuesta con datos live y respuesta degradada sin mercado disponible.

---

## BN-S3-04 — UI live en Instrumentos

**Tipo:** Frontend / tabla operativa  
**Depende de:** BN-S3-03  
**Archivos esperados:** `frontend/client/app/instruments/page.tsx`, tipos y cliente API si aplica.

### Objetivo

Mostrar movimiento diario sin confundirlo con rendimiento total ni senales.

### UI esperada

- columna `Var. Dia`
- columna `Impacto Dia`
- badge de frescura `LIVE/CACHE/STALE`
- estados vacios claros cuando no hay mercado
- layout responsive sin superposicion

### Criterio de aceptacion

- La tabla no usa mocks.
- Los badges de senal siguen separados de estado de mercado.
- Mobile mantiene cards legibles.
- TypeScript pasa.

---

## BN-S3-05 — Dashboard Live Session

**Tipo:** Frontend / dashboard  
**Depende de:** BN-S3-04  
**Archivos esperados:** componentes dashboard, hooks, tipos frontend.

### Objetivo

Agregar lectura de sesion en el dashboard principal.

### UI esperada

- session summary bar
- impacto diario total
- conteo de instrumentos positivos/negativos/sin dato
- heatmap simple de rendimiento diario
- timestamp/frescura de mercado

### Criterio de aceptacion

- La primera pantalla muestra estado de mercado sin tapar KPIs existentes.
- No introduce botones muertos ni indicadores sin fuente real.
- Funciona con datos parciales.

---

## BN-S3-06 — Verificacion y cierre

**Tipo:** QA / docs  
**Depende de:** BN-S3-05  
**Archivos esperados:** tests, README/docs de cierre.

### Objetivo

Cerrar Sprint 3 con evidencia tecnica y visual.

### Verificacion minima

```powershell
py -3.12 -m pytest tests/ -v
cd frontend/client
npx tsc --noEmit
npm run build
```

Si hay server disponible:

```powershell
uvicorn src.main:app --reload --port 8800
cd frontend/client && npm run dev
```

### Criterio de aceptacion

- Tests backend relevantes verdes.
- TypeScript/build frontend verdes.
- Capturas o notas de validacion visual para desktop/mobile.
- `README.md` y `MINOS_BN_BREAKDOWN.md` actualizados con estado real.

---

## 4. Primer BN recomendado

Sprint cerrado en PR#15.

Implementado:

- `PriceResult` expone `data_freshness`, `market_state`, `last_market_time`.
- `/api/v1/portfolio/summary` expone datos live por instrumento y agregado `live_market`.
- Instrumentos muestra badge de mercado separado de valuacion/senal.
- Dashboard muestra panel `Sesion Live` y heatmap diario.

Verificacion de cierre:

```powershell
py -3.12 -m pytest tests/ -v  # 216 passed
cd frontend/client
npx tsc --noEmit              # OK
npm run build                 # OK
```

