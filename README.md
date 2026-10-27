# MINOS Capital — estado vigente

Actualizado: 27/10/2026 por Rosario, por pedido de Tori.

## Decisión de producto y línea de base

La primera versión de MINOS Capital adopta [Wealthfolio oficial](https://github.com/wealthfolio/wealthfolio), web self-hosted AGPL-3.0. Objetivo: consultar la cartera con claridad, como reflejo patrimonial sin ejecución de órdenes.

El código FastAPI/Next.js de este repositorio se conserva como antecedente. Las instrucciones y capacidades históricas que aparecen más abajo corresponden a ese desarrollo; no describen el producto actualmente desplegado.

| Componente | Línea de base al 27/10/2026 |
| --- | --- |
| Wealthfolio | Desplegado en TORO, versión 3.11.0 con imagen fijada por digest |
| Acceso y datos | HTTPS, autenticación y persistencia configurados |
| n8n | Completado y verificado directamente con un flujo real |
| Fuentes Balanz | Excel y resúmenes disponibles; corte inicial 22/10/2026 |
| Portfolio e importación | Próxima tarea: configurar cuenta y validar carga |
| MCP de Wealthfolio | Habilitado; lectura autenticada de cartera pendiente |
| Respaldos | Copia inicial realizada; programación y restauración de prueba pendientes |
| Kanboard | Fuera del alcance por decisión de Tori |

### Evidencia de n8n

Flujo **MINOS — comprobar acceso**, tres nodos: inicio manual → consulta HTTPS de Minos → resultado con estado y fecha.

- Workflow ID: `V1Ta3qEqQ5049tNE`.
- Ejecución `6942`: **success**.
- Resultado observado: `httpStatus: 200`, `accesible: true`.
- Fecha: 27/10/2026, 10:13:55 de Argentina.
- Creación, ejecución y resultado comprobados mediante el conector oficial de n8n.
- Ejecución manual, sin programación. La conexión de n8n queda acreditada; consultar posiciones es el siguiente trabajo de integración.

### Próximo trabajo aprobado

1. Configurar portfolio/cuenta en Wealthfolio y confirmar su plantilla de tenencias.
2. Preparar el corte Balanz del 22/10/2026 y contrastarlo con los resúmenes.
3. Validar cantidades, monedas, CEDEARs, bonos/ON, fondos y efectivo; reimportar sin duplicados.
4. Consultar la misma cartera desde la interfaz, Crew/MCP y n8n.
5. Completar respaldos y personalización gradual con el branding existente.

La base documental y de despliegue también está versionada en Git local en TORO (commit de referencia `0ea67fc`); todavía no tiene un remoto propio conectado. Este README publica la línea de base vigente en GitHub sin incluir archivos financieros, credenciales ni configuración privada.

Génesis sirve para registrar dónde estamos y medir avances. Kanboard no es condición para avanzar. La v0 completa se cerrará con la cartera validada y sus consultas funcionando.

---

## Antecedente técnico: MINOS PRIME


> Sistema operativo patrimonial e inteligencia financiera de TORO

## Visión

MINOS PRIME evoluciona desde un portfolio tracker hacia una terminal institucional de decisión.

El objetivo del sistema es:

- Consolidar patrimonio multi-fuente.
- Centralizar posiciones, valuaciones y señales.
- Integrar inteligencia técnica y contexto operativo.
- Convertir datos financieros en decisiones accionables.
- Funcionar como núcleo financiero del ecosistema TORO.

---

## Arquitectura General

### Backend

- FastAPI
- SQLite
- Python 3.12
- yfinance
- pandas
- Scheduler async
- Cache TTL de precios

### Frontend

- Next.js 16
- React 19
- Tailwind
- UI institucional dark-mode
- Dashboard tipo terminal financiera

---

## Documentación

La especificación completa vive en el repo Trinity:
→ https://github.com/TORIBUSTOS/Trinity — `projects/minos-prime/`

| Doc | Descripción |
|-----|-------------|
| VISION.md | Norte estratégico |
| MISSION.md | Alcance y propósito operativo |
| SPECS.md | Especificaciones funcionales del MVP |
| ARCHITECTURE.md | Arquitectura conceptual y técnica |
| MINOS_BN_BREAKDOWN.md | Bloques de ejecución |
| SPRINT_3_LIVE_MARKET_LAYER.md | Scope ejecutable Sprint 3 |

---

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

---

## Estado Actual

### Fase

MINOS PRIME v2 — Sprint 3 Live Market Layer implementado

### Stack

| Capa | Estado |
|---|---|
| Backend API | Operativo |
| Market Refresh | Operativo |
| Valuación broker-grade | Operativa |
| Parser Balanz PDF | Operativo |
| Dashboard patrimonial | Operativo |
| Signals Engine | Operativo |
| Portfolio Summary | Operativo |
| Sistema de ingestión | Operativo |
| Live Market Layer | Operativo |

---

## Capacidades Activas

- Dashboard patrimonial con API real.
- Consolidación de instrumentos por ticker.
- Carga manual de posiciones.
- Importación masiva por CSV, Excel, PDF y capturas/imágenes.
- Parser de resumen Balanz PDF.
- Detección de acciones, CEDEARs, bonos, corporativos y fondos.
- Valuación broker-grade para instrumentos BYMA usando `.BA`.
- Cache de precios con TTL.
- Señales BUY / HOLD / SELL.
- Reasignación sugerida de cartera.
- Reset seguro de datos cargados.
- Portfolio summary consolidado.
- Tabla institucional de instrumentos.
- Variación diaria, impacto diario y frescura de mercado (`LIVE/CACHE/STALE/UNAVAILABLE`).
- Dashboard con sesión live y heatmap de movimiento diario.

---

## Sprint 2 — Broker-Grade Valuation Core

### Integrado

- Resolución correcta de instrumentos BYMA (`.BA`)
- Pricing trazable con contexto (`PriceResult`)
- Valuación tipo broker (`market_value`, `pnl`, etc.)
- Bloqueo de señales sin valuación confiable
- Tabla institucional de posiciones
- API de refresh market data

### Verificación Real

- `POST /api/v1/market/refresh` devolvió precios reales para `YPFD.BA` y `BMA.BA`
- `GET /api/v1/portfolio/summary` mostró:
  - `valuation_status: OK`
  - `resolved_symbol: YPFD.BA`
  - `resolved_symbol: BMA.BA`

---

## Sprint 3 — Live Market Layer

### LIVE MARKET LAYER

Implementado en PR#15:

- Variación intradiaria (%)
- Variación intradiaria ($)
- Impacto diario sobre cartera
- Estado LIVE/CACHE separado de BUY/HOLD/SELL
- Session summary bar
- Heatmap de rendimiento diario
- Métricas de frescura y exposición diaria

Objetivo:

Transformar MINOS PRIME desde un dashboard financiero hacia una terminal operativa viva.

---

## Ingestión

Endpoint único:

```text
POST /api/v1/ingest/file
```

### Formatos soportados

- `.csv`
- `.xlsx`
- `.xls`
- `.pdf`
- `.png`
- `.jpg`
- `.jpeg`
- `.webp`

### Notas

- PDF Balanz funciona por texto embebido.
- OCR usa `pytesseract`.
- Para OCR hace falta instalar `tesseract` y dejarlo en `PATH`.

---

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

---

## Reset Seguro

```json
{ "confirm": true }
```

Borra solo posiciones y registros de carga `file/manual`; preserva datos `api/visual` y catálogos.

---

## Tests

```bash
py -3.12 -m pytest tests/ -v
```

### Tests relevantes

- `tests/test_api_market.py`
- `tests/test_statement_ingestion.py`
- `tests/test_admin_reset.py`
- `tests/test_cors.py`

---

## Filosofía

MINOS PRIME no busca solamente mostrar precios.

Busca:

- contexto
- riesgo
- exposición
- timing
- memoria histórica
- inteligencia financiera
- soporte de decisión

El objetivo final es construir una terminal financiera institucional TORO.

---

Ver `CODEX.md` y `AGENTS.md` para contexto operativo, handoff entre agentes y arquitectura de colaboración.
