# MINOS Sprint 2 — Execution Order + Failover Rules

**Sprint:** Broker-Grade Valuation Core  
**Estado:** Activo  
**Fuente de gobierno:** Trinity → `projects/MINOS/sprints/sprint_2_broker_grade_core.md`  
**Regla central:** primero verdad financiera, después inteligencia.

---

## 0. Regla de gobierno

Este documento convierte Sprint 2 en una cadena de Bloques Negros ejecutables por Claude, AG/Gemini o un agente suplente.

Ningún agente puede ejecutar el bloque siguiente si el bloque anterior no cumple su criterio de aceptación.

```text
BN-S2-DIAG -> BN-S2-01 -> BN-S2-02 -> BN-S2-03 -> BN-S2-04 -> BN-S2-05
```

---

## 1. Failover Trinity

Cuando Claude esté limitado por uso o no pueda ejecutar, se activa failover:

```text
Claude no disponible -> AG ejecuta -> Gemini valida -> Rosario/Tori aprueban
AG no disponible -> Gemini ejecuta -> Rosario valida -> Tori aprueba
Gemini no disponible -> AG ejecuta -> Rosario valida -> Tori aprueba
```

### Reglas del agente suplente

- Ejecuta SOLO el BN activo.
- No cambia el scope.
- No avanza al próximo BN.
- No refactoriza fuera de archivos permitidos.
- Debe entregar evidencia: diff, tests, output y riesgos.
- Si detecta necesidad de ampliar arquitectura, debe frenar y reportar.

### Roles

| Rol | Responsabilidad |
|---|---|
| Tori | Aprobación final y criterio de negocio |
| Rosario | Producto, arquitectura de intención, control de alcance y QA estratégico |
| Claude | CTO, contrato técnico y validación final cuando tenga capacidad |
| AG | Ejecución pesada en repo |
| Gemini | Validación cruzada, revisión de diff y riesgos |

---

## 2. Reglas globales de Sprint 2

### Prohibido en todo Sprint 2 sin aprobación explícita

- Tocar señales BUY/HOLD/SELL salvo para bloquearlas si `valuation_status != OK`.
- Reescribir UI completa.
- Agregar dependencias nuevas.
- Cambiar estructura raíz del repo.
- Implementar CEDEAR avanzado, bonos complejos o FX avanzado antes de cerrar acciones BYMA.
- Usar `price = 0` como fallback silencioso.
- Valuar instrumentos ambiguos.
- Mezclar ARS/USD sin conversión explícita.

### Obligatorio

- Usar `Decimal` para dinero.
- Mantener tests existentes verdes.
- Ejecutar `python3.11 -m pytest` en Linux/CI o `py -3.12 -m pytest` en Windows local.
- Toda valuación debe poder explicar: ticker, exchange, instrument_type, resolved_symbol, price, currency, timestamp y fórmula.

---

# BN-S2-DIAG — Diagnóstico de pricing

**Estado:** Completado si ya existe evidencia de bugs estructurales.  
**Tipo:** Diagnóstico.  
**Agente recomendado:** Claude.  
**Failover:** AG ejecuta, Gemini valida.

## Objetivo

Confirmar cómo MINOS resuelve símbolos y obtiene precios hoy.

## Archivos permitidos

- `scripts/debug_pricing.py`
- módulos de lectura de pricing/market data si hace falta exponer datos de debug
- tests nuevos de debug si no alteran lógica

## Archivos prohibidos

- `src/services/portfolio_engine.py`
- `src/services/intelligence.py`
- frontend
- modelos persistentes, salvo lectura

## Output obligatorio

Tabla:

```text
ticker_input | instrument_type | exchange | resolved_symbol | source | price | currency | quote_timestamp | fetched_at | is_stale | status | error
```

Tickers mínimos:

```text
BMA, YPFD, GGAL, PAMP, SUPV
```

## Criterio de aceptación

El diagnóstico debe decir explícitamente:

- si BMA BYMA resuelve a BMA.BA o no
- si YPFD BYMA resuelve a YPFD.BA o no
- si la moneda es ARS o USD
- si existe timestamp
- si existe fallback silencioso
- si el modelo tiene `exchange` e `instrument_type`

---

# BN-S2-01 — InstrumentResolver mínimo para acciones BYMA

**Estado:** Pendiente.  
**Tipo:** Fix mínimo.  
**Agente recomendado:** AG.  
**Validador:** Gemini o Claude.

## Objetivo

Implementar resolución mínima de símbolo para acciones BYMA sin rediseñar toda la arquitectura.

## Regla funcional

```python
if exchange == "BYMA" and instrument_type == "EQUITY":
    resolved_symbol = f"{ticker}.BA"
else:
    resolved_symbol = ticker
```

## Archivos permitidos

- `src/services/market_data.py` o equivalente
- archivo nuevo pequeño si conviene aislar resolver, por ejemplo `src/services/instrument_resolver.py`
- `tests/test_instrument_resolver.py` o tests equivalentes
- `scripts/debug_pricing.py` solo para adaptar output

## Archivos prohibidos

- `src/services/portfolio_engine.py`
- `src/services/intelligence.py`
- frontend
- modelos/migraciones
- reglas de señales

## Tests obligatorios

- BMA + BYMA + EQUITY -> BMA.BA
- YPFD + BYMA + EQUITY -> YPFD.BA
- GGAL + BYMA + EQUITY -> GGAL.BA
- PAMP + BYMA + EQUITY -> PAMP.BA
- SUPV + BYMA + EQUITY -> SUPV.BA
- BMA + NYSE + EQUITY -> BMA
- YPF + NYSE + EQUITY -> YPF

## Validación

Ejecutar:

```bash
python3.11 -m pytest
python scripts/debug_pricing.py
```

En Windows local puede usarse:

```powershell
py -3.12 -m pytest
python scripts/debug_pricing.py
```

## Output obligatorio

1. Archivos modificados.
2. Diff resumido.
3. Código o ubicación de `resolve_symbol`.
4. Resultado de tests.
5. Output de `debug_pricing.py` para BMA e YPFD.
6. Confirmación explícita: no se tocó UI, intelligence ni portfolio_engine.

## STOP

Frenar si:

- no existe `exchange` o `instrument_type` en el flujo actual
- resolver símbolo exige cambiar modelos persistentes
- hay que tocar `portfolio_engine.py`
- los tests existentes fallan fuera de scope

No avanzar a BN-S2-02.

---

# BN-S2-02 — PriceResult / Quote enriquecido

**Estado:** Pendiente.  
**Tipo:** Estructura de dato de pricing.  
**Depende de:** BN-S2-01 aprobado.

## Objetivo

Hacer que market data devuelva un resultado trazable, no un número suelto.

## Modelo mínimo esperado

```python
PriceResult / Quote:
    input_ticker
    resolved_symbol
    source
    price
    currency
    timestamp
    fetched_at
    instrument_type
    exchange
    quote_unit
    status
    is_stale
    error
```

## Archivos permitidos

- `src/services/market_data.py`
- schemas internos si ya existen para market data
- tests de market data
- `scripts/debug_pricing.py`

## Archivos prohibidos

- frontend
- intelligence
- portfolio_engine salvo adaptación mínima de compatibilidad si tests actuales lo exigen
- migraciones

## Criterio de aceptación

- Market data expone `resolved_symbol`, `currency`, `timestamp`, `status`.
- No hay fallback `price = 0` silencioso.
- Si yfinance falla, status explícito.
- Tests existentes siguen pasando.

## STOP

Frenar si PriceResult exige migración de base de datos o rediseño mayor.

---

# BN-S2-03 — Valuación dinámica broker-grade en PortfolioEngine

**Estado:** Pendiente.  
**Tipo:** Core financiero.  
**Depende de:** BN-S2-02 aprobado.

## Objetivo

PortfolioEngine debe calcular valuación broker-grade usando Quote/PriceResult trazable.

## Fórmulas para acciones

```text
market_value = quantity * price
cost_basis = quantity * avg_cost
pnl_absolute = market_value - cost_basis
pnl_percentage = pnl_absolute / cost_basis * 100
portfolio_weight = market_value / total_market_value * 100
```

## Archivos permitidos

- `src/services/portfolio_engine.py`
- tests de portfolio engine
- tests nuevos de reconciliación Balanz
- schemas de respuesta patrimonial si hace falta exponer campos

## Archivos prohibidos

- frontend
- intelligence
- market data, salvo bug menor detectado por tests
- migraciones

## Tests golden obligatorios

### BMA

```text
quantity = 65
price = 10870.00
avg_cost = 9436.97
market_value = 706550.00
cost_basis = 613403.05
pnl_absolute = 93146.95
pnl_percentage = 15.19
```

### YPFD

```text
quantity = 15
price = 66425.00
avg_cost = 42089.79
market_value = 996375.00
cost_basis = 631346.85
pnl_absolute = 365028.15
pnl_percentage = 57.82
```

## Output obligatorio

- `valuation_trace` para BMA e YPFD.
- Resultado de tests.
- Confirmación de uso de `Decimal`.

## STOP

Frenar si se requiere cambiar modelos persistentes o rehacer ingestion.

---

# BN-S2-04 — valuation_status bloquea Intelligence

**Estado:** Pendiente.  
**Tipo:** Protección de decisión.  
**Depende de:** BN-S2-03 aprobado.

## Objetivo

Evitar que MINOS emita señales como válidas cuando la valuación no es confiable.

## Regla funcional

```text
if valuation_status != OK:
    signal_status = BLOCKED_BY_VALUATION
    signal is not actionable
```

## Archivos permitidos

- `src/services/intelligence.py`
- rutas/schemas de intelligence si hace falta exponer status
- tests de intelligence

## Archivos prohibidos

- market_data
- portfolio_engine salvo lectura de `valuation_status`
- frontend salvo que exista test/API que requiera campo nuevo

## Criterio de aceptación

- Una posición con pricing inválido no recibe señal accionable.
- API indica el motivo de bloqueo.
- Tests cubren valuation_status OK y no OK.

## STOP

Frenar si no existe todavía `valuation_status` desde BN-S2-03.

---

# BN-S2-05 — UI broker-like mínima

**Estado:** Pendiente.  
**Tipo:** Visualización.  
**Depende de:** BN-S2-04 aprobado.

## Objetivo

Mostrar una tabla mínima tipo broker con verdad financiera antes de inteligencia.

## Columnas mínimas

- Ticker
- Nominales
- Precio
- Fecha
- PPC
- V. Actual
- V. Inicial
- Rendimiento $
- Variación %
- % de cartera
- Estado pricing
- Fuente

## Archivos permitidos

- `frontend/client/app/instruments/page.tsx`
- componentes de tabla patrimonial existentes
- tipos frontend relacionados
- cliente API si requiere mapear campos nuevos

## Archivos prohibidos

- backend core
- intelligence core
- market data
- migraciones

## Criterio de aceptación

- BMA e YPFD muestran campos equivalentes a Balanz.
- Si pricing_status != OK, aparece advertencia visible.
- Señales quedan visualmente subordinadas a la valuación.

## STOP

Frenar si backend no entrega los campos necesarios.

---

## Checklist de ejecución por cada BN

Cada agente debe responder al cierre:

```text
BN ejecutado:
Agente:
Branch:
Archivos modificados:
Archivos NO tocados:
Tests ejecutados:
Resultado:
Output verificable:
Riesgos:
Próximo BN recomendado:
```

---

## Comandos base

Linux / CI:

```bash
python3.11 -m pytest
```

Windows local:

```powershell
py -3.12 -m pytest
```

Frontend:

```bash
cd frontend/client
npm run dev
```

Backend:

```bash
uvicorn src.main:app --reload --port 8800
```
