# MINOS Sprint 4 — Memory & Validation Layer

**Sprint:** Memory & Validation Layer
**Estado:** EN PROGRESO
**Fecha de formalizacion:** 2026-05-11
**Objetivo rector:** convertir MINOS de una terminal de snapshot/live session en una terminal con memoria operativa: validar antes de guardar, recordar fotos patrimoniales y explicar que cambio desde la ultima carga.

---

## 0. Resultado esperado

Al cerrar Sprint 4, MINOS debe poder responder:

- que datos se detectaron antes de guardar una carga;
- que se va a crear, actualizar, ignorar o rechazar;
- cual fue la ultima foto patrimonial confiable;
- que cambio contra la foto anterior;
- que decisiones quedan pendientes por riesgo, concentracion, senales o datos no confiables;
- si existe caja/liquidez informada, cuanto capital disponible hay.

Sprint 4 prioriza confianza, trazabilidad y memoria. No busca agregar mas widgets; busca que los datos cargados sean explicables y que el dashboard tenga continuidad entre cargas.

---

## 1. Regla central

```text
validacion antes de persistir -> snapshot confiable -> diff patrimonial -> decisiones pendientes
```

MINOS no debe guardar datos dudosos de forma silenciosa. Si no puede explicar el cambio, debe mostrarlo como advertencia o pendiente, no inventar certeza.

---

## 2. Cadena de ejecucion

```text
BN-S4-01 -> BN-S4-02 -> BN-S4-03 -> BN-S4-04 -> BN-S4-05 -> BN-S4-06
```

Ningun BN debe avanzar si el anterior no cumple su criterio de aceptacion minimo, salvo que se documente explicitamente el motivo.

---

## 3. Fuera de scope

- No integrar brokers reales.
- No ejecutar ordenes.
- No integrar AIACOS todavia.
- No depender de ARGOS.
- No implementar ML, prediccion o scoring avanzado.
- No construir templates visuales inteligentes completos en este sprint.
- No hacer contabilidad completa.
- No inventar caja/liquidez cuando la fuente no la informa.
- No reescribir la UI completa.

---

## BN-S4-01 — Upload Preview Contract

**Tipo:** Backend / ingestion contract
**Depende de:** Sprint 3 cerrado
**Archivos esperados:** `src/api/routes/ingest.py`, `src/services/ingestion.py`, schemas si aplica, tests API/ingestion.
**Estado:** IMPLEMENTADO

### Objetivo

Separar deteccion/preview de persistencia. El backend debe poder recibir un archivo y devolver una previsualizacion de lo detectado sin guardar posiciones.

### Contrato objetivo

Una respuesta de preview debe incluir:

```text
preview_id
source_name
portfolio_name
detected_positions[]
rejected_rows[]
warnings[]
summary
can_confirm
expires_at
```

Cada posicion detectada debe incluir, como minimo:

```text
ticker
asset_type
quantity
price / market_value si existe
currency
source_row / source_section
confidence
action_hint
```

`action_hint` puede ser:

```text
CREATE | UPDATE | IGNORE | REVIEW
```

### Criterio de aceptacion

- [x] Existe una forma de pedir preview sin persistir posiciones.
- [x] La respuesta muestra errores y advertencias de forma estructurada.
- [x] Si hay incertidumbre, `can_confirm` puede ser `false` o incluir `REVIEW`.
- [x] Tests verifican que preview no modifica la base.
- [x] No se rompe `POST /api/v1/ingest/file` actual.

### Implementado

- `POST /api/v1/ingest/preview` acepta `source_name` y `portfolio_name` opcionales.
- El contrato expone `preview_id`, `expires_at`, `detected_positions`, `rejected_rows`, `summary`, `action_hint`, `confidence` y `can_confirm`.
- Cada posicion conserva campos legacy (`cantidad`, `moneda`, `valuacion`) y agrega aliases de contrato (`quantity`, `currency`, `market_value`).
- Las posiciones existentes del mismo source/portfolio se marcan como `UPDATE`; las nuevas como `CREATE`; las incompletas como `REVIEW`.
- El preview no persiste posiciones ni registros de carga.

---

## BN-S4-02 — Frontend Preview & Confirm

**Tipo:** Frontend / ingestion UX
**Depende de:** BN-S4-01
**Archivos esperados:** `frontend/client/app/manual-entry/page.tsx`, hooks/API client, tipos frontend.
**Estado:** IMPLEMENTADO

### Objetivo

Mostrar al usuario que detecto MINOS antes de guardar una carga, y pedir confirmacion explicita.

### UI esperada

- Tabla/lista de posiciones detectadas.
- Conteo de nuevas/actualizadas/rechazadas/revision.
- Advertencias visibles.
- Boton `Confirmar carga`.
- Boton `Cancelar`.
- Estados claros si el preview expiro o no es confirmable.

### Criterio de aceptacion

- [x] Subir archivo no guarda silenciosamente cuando se usa flujo preview.
- [x] El usuario puede inspeccionar antes de confirmar.
- [x] Errores/rechazos no se pierden.
- [x] Mobile mantiene lectura usable.
- [x] TypeScript pasa.

### Implementado

- `frontend/client/lib/minos-api.ts` y `frontend/client/hooks/use-minos.ts` mandan `source_name` y `portfolio_name` al preview.
- `frontend/client/types/minos.ts` refleja el contrato de BN-S4-01: `preview_id`, `expires_at`, `detected_positions`, `rejected_rows`, `summary`, `action_hint` y `confidence`.
- `/manual-entry` bloquea la confirmacion si no existe preview valido, si el preview no es confirmable, si vencio o si cambio fuente/cartera.
- La UI muestra conteos por accion (`CREATE`, `UPDATE`, `REVIEW`), filas rechazadas y vista mobile sin tabla horizontal.

---

## BN-S4-03 — Portfolio Snapshots

**Tipo:** Backend / memory layer
**Depende de:** BN-S4-02
**Archivos esperados:** modelos/migracion si aplica, `src/services/portfolio_engine.py`, nuevo servicio de snapshots, tests.
**Estado:** IMPLEMENTADO

### Objetivo

Guardar fotos patrimoniales confiables para que MINOS pueda comparar el estado actual contra estados anteriores.

### Snapshot minimo

```text
snapshot_id
created_at
trigger
total_valuation
by_asset[]
by_source[]
by_currency[]
live_market summary opcional
source_load_record_id opcional
notes/warnings
```

`trigger` puede ser:

```text
UPLOAD_CONFIRMED | MANUAL_ENTRY | MARKET_REFRESH | MANUAL_SNAPSHOT
```

### Criterio de aceptacion

- [x] Se puede crear snapshot desde un portfolio summary consolidado.
- [x] El snapshot preserva suficiente informacion para diff posterior.
- [x] No depende de precios vivos para existir.
- [x] Tests cubren creacion, lectura y snapshot con cartera vacia.

### Implementado

- Modelo `PortfolioSnapshot` con `snapshot_id`, `trigger`, `created_at`, `total_valuation`, `by_asset`, `by_source`, `by_currency`, `live_market`, `source_load_record_id`, `notes` y `warnings`.
- Servicio `src/services/portfolio_snapshots.py` para crear, listar, buscar por id y obtener ultimo snapshot.
- Endpoints:
  - `POST /api/v1/portfolio/snapshots`
  - `GET /api/v1/portfolio/snapshots`
  - `GET /api/v1/portfolio/snapshots/latest`
  - `GET /api/v1/portfolio/snapshots/{snapshot_id}`
- El repo actual no tiene carpeta `alembic`; se mantiene el patron MVP existente con `Base.metadata.create_all`.

---

## BN-S4-04 — Change Detection

**Tipo:** Backend / portfolio diff
**Depende de:** BN-S4-03
**Archivos esperados:** servicio de diff, ruta API, tests.

### Objetivo

Comparar el snapshot actual contra el anterior y devolver cambios patrimoniales legibles.

### Cambios objetivo

```text
new_positions
removed_positions
quantity_changes
valuation_changes
signal_changes
freshness_changes
large_moves
summary
```

### Criterio de aceptacion

- Existe endpoint o contrato para obtener diff entre snapshots.
- Los cambios incluyen severidad (`INFO`, `WARN`, `ACTION`).
- No confunde movimiento de mercado con cambios por carga.
- Tests cubren altas, bajas, cambios de valuacion y sin cambios.

---

## BN-S4-05 — Pending Decisions Panel

**Tipo:** Frontend / decision surface
**Depende de:** BN-S4-04
**Archivos esperados:** dashboard, hooks, tipos frontend.

### Objetivo

Mostrar en Dashboard una lista corta de decisiones pendientes basadas en cambios, riesgo y datos no confiables.

### Entradas esperadas

- diff patrimonial;
- `portfolio-status`;
- `reallocation`;
- `valuation_status`;
- `data_freshness`;
- concentracion por activo;
- senales BUY/HOLD/SELL.

### UI esperada

- Panel `Decisiones pendientes`.
- 3 a 7 items maximos.
- Cada item con motivo, severidad y accion sugerida.
- No mostrar ruido si no hay pendientes reales.

### Criterio de aceptacion

- No duplica el banner de riesgo.
- No inventa decisiones si faltan datos.
- Explica por que algo esta pendiente.
- Funciona con cartera vacia o datos parciales.

---

## BN-S4-06 — Liquidity Minimal Layer

**Tipo:** Backend + Frontend / liquidity
**Depende de:** BN-S4-05
**Archivos esperados:** normalizacion/portfolio engine si aplica, dashboard/instruments si aplica, tests.

### Objetivo

Mostrar caja, fondos money market o capital disponible cuando exista dato informado, sin inventarlo.

### Alcance minimo

- Detectar instrumentos o posiciones marcadas como caja/liquidez si el dato existe.
- Exponer liquidez estimada en summary.
- Mostrar `No informado` si no hay dato confiable.
- Conectar con reallocation cuando haya capital liberable.

### Fuera de scope especifico

- No modelar contabilidad completa.
- No inferir caja por diferencia contra extracto si no hay fuente.
- No integrar cuenta bancaria o broker.

### Criterio de aceptacion

- Liquidez visible solo cuando hay dato.
- Estado claro cuando no esta informada.
- Tests cubren cartera con caja y cartera sin caja.

---

## 4. Test plan recomendado

Backend:

```powershell
py -3.12 -m pytest tests/ -v
```

Tests esperados por sprint:

- `tests/test_ingestion_preview.py`
- `tests/test_api_ingest_preview.py`
- `tests/test_portfolio_snapshots.py`
- `tests/test_portfolio_changes.py`
- `tests/test_pending_decisions.py`
- `tests/test_liquidity_layer.py`

Frontend:

```powershell
cd frontend/client
npx tsc --noEmit
npm run build
```

Validacion visual:

- `/manual-entry` preview desktop/mobile.
- `/` dashboard con decisiones pendientes.
- estados vacios, errores y datos parciales.

---

## 5. Definicion de done del sprint

- Preview de carga antes de guardar operativo.
- Confirmacion explicita de carga implementada.
- Snapshots patrimoniales persistidos o disponibles segun contrato aprobado.
- Diff entre snapshots expuesto.
- Dashboard muestra cambios/decisiones pendientes sin ruido.
- Liquidez minima visible solo con dato confiable.
- Tests backend relevantes verdes.
- TypeScript y build frontend verdes.
- Docs actualizados con estado real.

---

## 6. Primer BN recomendado

Arrancar por **BN-S4-01 — Upload Preview Contract**.

Motivo:

- mejora confianza inmediatamente;
- reduce riesgo de cargas destructivas o confusas;
- prepara snapshots, porque una carga confirmada se vuelve un evento confiable;
- no requiere resolver toda la memoria historica desde el primer commit.
