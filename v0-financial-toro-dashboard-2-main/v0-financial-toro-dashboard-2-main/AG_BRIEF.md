# AG BRIEF — MINOS PRIME Frontend

## Tu misión

Construir las vistas del dashboard MINOS PRIME sobre la template v0 ya instalada.
La capa técnica (API client, types, hooks, formatters) ya está hecha — **no toques esos archivos**.
Vos construís los componentes de UI.

---

## Stack disponible

- **Next.js 16** + React 19 + TypeScript
- **Tailwind CSS v4** + shadcn/ui (todos los componentes en `components/ui/`)
- **Recharts** (AreaChart, BarChart, PieChart, LineChart, RadialBarChart)
- **Framer Motion** (`motion/react`) para animaciones
- **Lucide React** para íconos

---

## Capa técnica ya construida (NO modificar)

| Archivo | Qué hace |
|---|---|
| `types/minos.ts` | Todos los TypeScript types del backend |
| `lib/minos-api.ts` | API client tipado — 10 endpoints |
| `hooks/use-minos.ts` | React hooks con loading/error/refetch |
| `lib/minos-formatters.ts` | Formatters ARS/USD, números argentinos, colores |

### Cómo usar los hooks

```tsx
import { usePortfolioSummary, usePositions } from "@/hooks/use-minos"
import { formatARS, formatPct, rendimientoColor } from "@/lib/minos-formatters"

function Dashboard() {
  const { data, loading, error } = usePortfolioSummary()

  if (loading) return <Skeleton />
  if (error)   return <ErrorState message={error.message} />

  return (
    <div>
      <h1>{formatARS(data.total_valuation)}</h1>
      {data.by_source.map(s => (
        <div key={s.source}>{s.source}: {formatPct(s.pct)}</div>
      ))}
    </div>
  )
}
```

### Hooks disponibles

```typescript
usePortfolioSummary()     // → { total_valuation, by_asset[], by_source[], by_currency[] }
usePortfolioBySource()    // → SourceSummary[]
usePortfolioByCurrency()  // → CurrencySummary[]
usePortfolios()           // → Portfolio[] con position_count
usePositions(filters?)    // → Position[] — filtrable por portfolio_name o source_name
useUnifiedTickers()       // → UnifiedTicker[] con presence y entries
useMarketPrices()         // → { prices: { [ticker]: { price, fetched_at, expired } } }
useRefreshPrices()        // → { refresh(tickers[]), loading, error }
useFileUpload()           // → { upload(file, source, portfolio), loading, error, result }
```

---

## API del backend (FastAPI en localhost:8001)

```
GET  /api/v1/portfolio/summary      → consolidado completo
GET  /api/v1/portfolio/by-source    → por broker (Balanz, IOL, Manual...)
GET  /api/v1/portfolio/by-currency  → ARS vs USD
GET  /api/v1/portfolios             → lista de portfolios con conteo
GET  /api/v1/positions              → posiciones (filtrables)
POST /api/v1/positions              → carga manual
GET  /api/v1/tickers/unified        → tickers consolidados cross-portfolio
POST /api/v1/market/refresh         → forzar fetch de precios (yfinance)
GET  /api/v1/market/prices          → precios en cache con TTL
POST /api/v1/ingest/upload          → subir CSV/XLSX
```

---

## Vistas a construir

### 1. Dashboard (vista principal)

Referencia visual: Balanz home (`minos-prime/150 - Balanz...png`)

```
KPIs (fila superior):
  - Total ARS    → data.total_valuation  (formatARS)
  - Total USD    → by_currency["USD"].valuation (formatUSD)
  - Fuentes      → by_source.length
  - Posiciones   → sum of entries across portfolios

Donut chart:
  - by_asset[] con pct y colores de ASSET_COLORS
  - Leyenda lateral con ticker + pct

Por fuente (el feature exclusivo):
  - Tabla horizontal: Source | ARS | USD | % del total
  - Colores por fuente

Exposición por moneda:
  - Barra ARS vs USD
```

### 2. Mis Instrumentos (tabla detallada)

Referencia visual: Balanz instruments page (`minos-prime/152 - Balanz...png`)

```
Columnas (igual que Balanz):
  Ticker | Nominales | Precio | Fecha | PPC* | V. Actual | Rendimiento | Var. día (%) | % del total

*PPC = Precio Promedio de Compra — MINOS no lo calcula aún, mostrar "-"

Agrupamiento:
  - Acciones (6), Bonos (4), Cedears (9), etc.
  - Usar usePositions() — agrupar por categoría de asset (pendiente backend)
  - Por ahora agrupar por source_name como aproximación

Selector de moneda: ARS | USD
Filtros: por fuente (portfolio/source)
```

### 3. Por Fuente (feature exclusivo MINOS)

```
Sidebar de fuentes: Balanz | IOL | Manual | [todas]
Al seleccionar una fuente → usePositions({ source_name })
Muestra la tabla de posiciones filtrada por esa fuente
Comparación: mismo ticker en múltiples fuentes (useUnifiedTickers)
```

### 4. Carga Manual

```
Form:
  - Fuente (Source): input text (ej: "Balanz", "IOL")
  - Cartera (Portfolio): input text (ej: "Principal")
  - Ticker: input text uppercase automático
  - Nominales (Quantity): number > 0
  - Moneda: ARS | USD (select)
  - Valuación: number
  - Fecha: date picker

POST → useFileUpload() o usePositions con create

Feedback: toast con resultado
```

### 5. Precios de mercado (sidebar widget)

```
Usar useMarketPrices() para mostrar precios en cache
Botón "Actualizar" → useRefreshPrices() con todos los tickers
Indicador TTL: verde = fresco, amarillo = expirando, rojo = expirado
```

---

## UX/Diseño

Referencia de diseño: `docs/minos-ui-playground.html` (abrir en browser)

- **Tema**: dark (ya configurado en la template)
- **Acento**: teal (`oklch(0.78 0.16 182)`) — color ya definido en el playground
- **Fuente monospace**: para valores numéricos (`font-mono`)
- **Animaciones**: usar los patterns de `motion/react` ya en `financial-analytics-dashboard.tsx`
- **Colores asset**: importar `ASSET_COLORS` de `lib/minos-formatters.ts`
- **Números**: SIEMPRE usar `formatARS` / `formatUSD` / `formatPct` — nunca `.toLocaleString()` directo

---

## Contexto de negocio

MINOS agrega posiciones de MÚLTIPLES brokers. El usuario tiene:
- Cuenta en **Balanz** (acciones, bonos, cedears, fondos)
- Potencialmente cuenta en **IOL** u otros
- Posiciones cargadas **manualmente**

El valor central es ver TODO unificado en un solo lugar, con la posibilidad de filtrar por fuente.

Tickers argentinos:
- Acciones locales: GGAL, YPFD, PAMP, BMA, etc.
- Cedears: MELI, NVDA, META, MSFT, NFLX, QQQ, etc.
- Bonos: AL30, GD30, GD35, AE38, etc.
- Fondos/FCI: CPRIVADA, BCMMUSDA, etc.

---

## Archivos de referencia (screenshots del broker real)

```
minos-prime/150 - Balanz - [clientes.balanz.com].png   → Dashboard home
minos-prime/152 - Balanz - [clientes.balanz.com].png   → Mis instrumentos (tabla completa)
minos-prime/153 - Balanz - [clientes.balanz.com].png   → Research / Reportes
minos-prime/154 - Balanz - [clientes.balanz.com].png   → Resumen de cuenta / Evolución histórica
```

---

## Comandos

```bash
# Instalar deps (ya tiene pnpm-lock.yaml)
cd v0-financial-toro-dashboard-2-main
pnpm install

# Dev server (puerto 3000)
pnpm dev

# Backend MINOS debe estar corriendo en paralelo:
# cd ../../  &&  uvicorn src.main:app --reload --port 8001
```

---

## Qué NO hacer

- No modificar `types/minos.ts`, `lib/minos-api.ts`, `hooks/use-minos.ts`, `lib/minos-formatters.ts`
- No agregar SWR o React Query — los hooks ya están hechos sin deps extra
- No usar `.toLocaleString()` directo — usar los formatters
- No inventar datos mock en los componentes — conectar a los hooks reales
- No cambiar la estructura de carpetas del proyecto v0
