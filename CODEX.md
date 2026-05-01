# CODEX.md — MINOS PRIME

Guia local para Codex en el repo MINOS v2.
Complementa `CLAUDE.md` y `AG.md` con foco en reparacion, contratos reales y mantenimiento del frontend conectado al backend.

**Ultima actualizacion:** 2026-04-29
**Commit de referencia:** `3de1f29 fix(frontend): connect minos prime controls`

---

## Rol de Codex

Codex trabaja como agente de reparacion e integracion:

- Auditar UI contra comportamiento real.
- Evitar botones, inputs o acciones decorativas en rutas productivas.
- Cruzar intencion de producto con docs, hooks y endpoints antes de parchear.
- Hacer cambios acotados y verificables.
- No arrastrar cambios ajenos del working tree.

Regla base: **un control visible es una promesa de producto**. Si no se puede cumplir todavia, debe quedar conectado, deshabilitado con motivo, o eliminado.

---

## Contexto del Frontend

Path canonico:

```bash
frontend/client
```

Stack:

- Next.js 16 + React 19 + TypeScript.
- Tailwind CSS v4 + shadcn/ui.
- Lucide para iconos.
- Recharts para graficos.
- Backend FastAPI en `http://localhost:8800`.

Archivos clave:

| Archivo | Funcion |
|---------|---------|
| `frontend/client/lib/minos-api.ts` | Cliente API tipado |
| `frontend/client/hooks/use-minos.ts` | Hooks de datos con loading/error/refetch |
| `frontend/client/types/minos.ts` | Contratos TypeScript del backend |
| `frontend/client/components/layout/app-header.tsx` | Header global, busqueda, sync, movimiento |
| `frontend/client/components/layout/app-sidebar.tsx` | Navegacion principal |
| `frontend/client/components/dashboard/market-widget.tsx` | Mercado en vivo y refresh de precios |

---

## Contratos API Confirmados

Estos contratos fueron revisados contra `src/api/routes/*`:

| Feature | Endpoint real |
|---------|---------------|
| Posiciones | `GET /api/v1/positions` |
| Crear posicion manual | `POST /api/v1/positions` |
| Portfolio summary | `GET /api/v1/portfolio/summary` |
| Por fuente | `GET /api/v1/portfolio/by-source` |
| Por moneda | `GET /api/v1/portfolio/by-currency` |
| Portfolios | `GET /api/v1/portfolios` |
| Tickers unificados | `GET /api/v1/tickers/unified` |
| Refresh market data | `POST /api/v1/market/refresh` |
| Precios cacheados | `GET /api/v1/market/prices` |
| Upload CSV/XLSX | `POST /api/v1/ingest/file` |
| Signals | `GET /api/v1/intelligence/signals` |
| Estado cartera | `GET /api/v1/intelligence/portfolio-status` |
| Reasignacion | `GET /api/v1/intelligence/reallocation` |

Gotchas:

- Upload es `/api/v1/ingest/file`, no `/api/v1/ingest/upload`.
- `POST /api/v1/market/refresh` refresca todos los tickers de cartera desde backend; no requiere body `{ tickers }`.
- `GET /api/v1/portfolios` debe exponer `source_name` para que el frontend pueda mapear posiciones por fuente.

---

## Reparacion Realizada Por Codex

Objetivo: revisar el frontend de MINOS Prime para identificar botones muertos, datos hardcodeados y mocks, y reparar la primera tanda de mayor impacto.

Cambios aplicados:

- Header:
  - Busqueda global conectada a `/instruments?q=...`.
  - Sync global conectado a `MinosAPI.refreshPrices()` y evento de refresh para hooks.
  - Punto animado de notificaciones removido hasta tener alertas reales.

- API client/hooks:
  - Upload corregido a `/api/v1/ingest/file`.
  - Refresh de market data alineado con backend sin body.
  - Agregado evento global `minos:refresh` via `triggerMinosRefresh()`.

- Backend:
  - `GET /api/v1/portfolios` ahora devuelve `source_name`.

- Carga Manual:
  - Removido `operation_type` porque no existe contrato backend para persistirlo.
  - `Descargar Plantilla` genera CSV real.
  - Carteras salen de `usePortfolios()` con fallback a `Principal`.

- Mis Instrumentos:
  - `Exportar` descarga CSV real de datos filtrados.
  - `Filtros` reemplazado por selector real de fuente.
  - Detalle navega a `/tickers?q=TICKER`.

- Por Fuente:
  - `Vincular Fuente` y `Vincular primera fuente` navegan a `/manual-entry`.
  - `Gestionar Posiciones` navega a `/instruments?q=FUENTE`.
  - `Historial` queda deshabilitado con motivo porque falta endpoint dedicado.

- Tickers:
  - Boton de detalle expande/colapsa fila.
  - Evitado `data.sort()` mutando datos en render.

- Mercado en Vivo:
  - Refresh llama endpoint real.
  - `Ver Monitor Completo` queda deshabilitado si no hay precios; conserva tooltip de estado pendiente.

---

## Regla Anti-Botones Muertos

Antes de agregar o dejar un control en UI productiva:

1. Debe tener `onClick`, `href`, `type="submit"` o `disabled` con motivo.
2. Si es icon-only, debe tener `aria-label` o `title` util.
3. Si llama backend, confirmar endpoint real en `src/api/routes`.
4. Si todavia no existe backend/ruta, elegir una:
   - crear feature minima,
   - deshabilitar explicitamente,
   - eliminar de la UI,
   - mover a demo/preview.
5. No usar `setTimeout` para simular una operacion real fuera de demos.
6. No mostrar indicadores de datos inexistentes, como badges animados de notificaciones sin fuente real.

---

## Datos Hardcodeados Y Mocks

Permitidos:

- Fallbacks locales transparentes, por ejemplo cartera `Principal` si todavia no hay portfolios.
- Placeholders de inputs.
- Demos aisladas en `app/preview` o carpetas claramente marcadas como demo.

No permitidos en rutas productivas:

- Perfil real de usuario hardcodeado.
- Datos financieros ficticios en dashboard real.
- Botones que parezcan ejecutar acciones sin efecto real.
- Estados visuales que prometan alertas, sincronizacion o monitoreo sin fuente de datos.

Pendiente conocido:

- `components/cards/financial-analytics-dashboard.tsx` contiene datasets demo. Si no es productivo, mantenerlo aislado en preview/demo; si entra en producto, convertirlo a props/API.
- `settings/page.tsx` todavia usa perfil/preferencias locales. Requiere decision de auth/config.
- Notificaciones necesitan contrato backend o deben seguir sin badge activo.
- Historial por fuente requiere endpoint dedicado.

---

## Verificacion

Comandos usados en esta reparacion:

```bash
cd frontend/client
npx tsc --noEmit
npm run build
```

Resultado:

- TypeScript: OK.
- Next build: OK.
- Backend tests: no corrieron en el entorno actual porque falta `fastapi`.

Nota:

```bash
py -3.12 -m pytest tests/ -v
```

es el comando recomendado por `CLAUDE.md` cuando las dependencias Python 3.12 estan instaladas.

---

## Git Y Working Tree

El repo puede tener muchos cambios ajenos o generados. Codex debe:

- Stagear solo los archivos que toca.
- No revertir cambios ajenos.
- Revisar `git diff --cached --name-only` antes de commitear.
- Avisar si el working tree ya venia sucio.

Ultimo push realizado:

```bash
git push origin main
```

Commit:

```text
3de1f29 fix(frontend): connect minos prime controls
```

---

## Proximos Pasos Recomendados

1. Definir contrato de notificaciones/alertas.
2. Definir si `operation_type` debe existir en backend o si MINOS maneja solo posiciones snapshot.
3. Crear endpoint/historial de cargas por fuente si el producto lo necesita.
4. Convertir settings/perfil a fuente real o marcar modo local.
5. Mover demos/mocks fuera de rutas productivas.
6. Agregar una verificacion automatica simple para detectar `<Button>` sin accion ni `disabled`.

---

## Sprint 2 - Pricing Core

**Ultima actualizacion:** 2026-04-30
**Branch actual de trabajo:** `codex/bn-s2-02`
**BN ejecutado:** `BN-S2-02 - PriceResult / Quote enriquecido`

Documentos de gobierno leidos antes de ejecutar:

- `minos-prime/SPRINT_2_EXECUTION_ORDER.md`
- `minos-prime/MINOS_BN_BREAKDOWN.md`
- `CLAUDE.md`
- `minos-prime/execution_log.txt` si existe en la rama

Reglas de alcance activas:

- No avanzar a `BN-S2-03` hasta aprobacion.
- No tocar UI.
- No tocar `src/services/intelligence.py` ni reglas de signals.
- No tocar `src/services/portfolio_engine.py`, salvo compatibilidad minima si tests lo exigen.
- No agregar dependencias.
- No tocar modelos ni migraciones.
- Mantener compatibilidad con tests existentes.

### Estado BN-S2-01 en esta rama

La rama `codex/bn-s2-02` no tenia incorporados los cambios previos de `BN-S2-01` al comenzar el trabajo. Para que BN-S2-02 mantuviera el contrato requerido, se incorporo dentro de archivos permitidos el resolver minimo:

```python
def resolve_symbol(ticker: str, exchange: str | None = None, instrument_type: str | None = None) -> str:
    if exchange == "BYMA" and instrument_type == "EQUITY":
        return f"{ticker}.BA"
    return ticker
```

Casos cubiertos:

- `BMA + BYMA + EQUITY -> BMA.BA`
- `YPFD + BYMA + EQUITY -> YPFD.BA`
- `GGAL + BYMA + EQUITY -> GGAL.BA`
- `PAMP + BYMA + EQUITY -> PAMP.BA`
- `SUPV + BYMA + EQUITY -> SUPV.BA`
- `BMA + NYSE + EQUITY -> BMA`
- `YPF + NYSE + EQUITY -> YPF`

### Trabajo BN-S2-02 Realizado

`src/services/market_data.py` ahora expone un resultado trazable:

```python
@dataclass
class PriceResult:
    input_ticker: str
    resolved_symbol: str
    source: str
    price: Decimal | None
    currency: str
    timestamp: datetime | None
    fetched_at: datetime
    instrument_type: str | None
    exchange: str | None
    quote_unit: str
    status: str
    is_stale: bool
    error: str | None
```

Metodos relevantes:

- `MarketDataService.get_quote(ticker, exchange=None, instrument_type=None) -> PriceResult`
- `MarketDataService.refresh_quotes(tickers) -> dict[str, PriceResult]`
- `MarketDataService.get_price(...) -> float | None` se mantiene por compatibilidad.
- `MarketDataService.refresh_prices(...) -> dict[str, float | None]` se mantiene por compatibilidad.

Estados implementados:

- `OK`: fetch exitoso desde yfinance.
- `CACHED`: cache vigente usado explicitamente.
- `STALE`: yfinance fallo y se devolvio cache vencido con `is_stale=True`.
- `FETCH_ERROR`: yfinance fallo sin cache; `price=None`, nunca `price=0` silencioso.

Notas de diseno:

- Dinero/precios nuevos se guardan en `Decimal` dentro de `PriceResult`.
- `currency` viene de `fast_info.currency` cuando existe.
- Para BYMA o simbolos `.BA`, si yfinance no informa moneda, se usa `ARS`.
- Para el resto, fallback conservador `USD`.
- `timestamp` usa `fast_info.last_trade_time` o `fast_info.last_price_time` si existe; si no existe, usa `fetched_at` como timestamp trazable.

### Archivos Tocadas En BN-S2-02

- `src/services/market_data.py`
- `tests/test_market_data.py`
- `tests/test_instrument_resolver.py`
- `scripts/debug_pricing.py`
- `minos-prime/execution_log.txt`
- `CODEX.md`

Archivos que no se tocaron:

- `src/services/portfolio_engine.py`
- `src/services/intelligence.py`
- `frontend/client/**`
- modelos/migraciones
- reglas de señales

### Tests BN-S2-02

Comandos ejecutados:

```bash
py -3.12 -m pytest tests/test_market_data.py tests/test_instrument_resolver.py
py -3.12 -m pytest tests/
py -3.12 scripts/debug_pricing.py
```

Resultados:

- `tests/test_market_data.py tests/test_instrument_resolver.py`: 23 passed.
- `tests/`: 175 passed.
- `debug_pricing.py`: ejecuto OK con resultados trazables para BMA, YPFD, GGAL, PAMP y SUPV.

Salida relevante de debug:

```text
BMA | EQUITY | BYMA | BMA.BA | yfinance | 10840.0 | ARS | 2026-04-30T19:05:30.030990+00:00 | 2026-04-30T19:05:30.030990+00:00 | False | OK | None
YPFD | EQUITY | BYMA | YPFD.BA | yfinance | 67175.0 | ARS | 2026-04-30T19:05:31.460372+00:00 | 2026-04-30T19:05:31.460372+00:00 | False | OK | None
```

### Riesgos Pendientes

- yfinance puede no exponer timestamp real de mercado para todos los simbolos; en ese caso se usa `fetched_at`.
- Pricing depende de disponibilidad y consistencia de yfinance.
- CEDEAR, bonos y FX siguen fuera de scope.
- `portfolio_engine.py` todavia no consume `PriceResult`; eso corresponde a `BN-S2-03`.

### Continuacion Recomendada

No avanzar a `BN-S2-03` sin aprobacion explicita. Cuando se apruebe:

- Leer nuevamente `minos-prime/SPRINT_2_EXECUTION_ORDER.md`.
- Revisar `minos-prime/execution_log.txt`.
- Usar `PriceResult` desde `MarketDataService.get_quote`.
- Implementar valuacion broker-grade en `src/services/portfolio_engine.py`.
- Mantener uso de `Decimal` para formulas financieras.
