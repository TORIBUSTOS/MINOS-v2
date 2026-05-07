/**
 * MINOS PRIME — TypeScript types
 * Mirror of Python Pydantic schemas in src/schemas/
 * API base: http://localhost:8800/api/v1
 */

// ── Enums ────────────────────────────────────────────────────────────────────

export type LoadType = "file" | "manual" | "api" | "visual"
export type ValidationStatus = "valid" | "invalid" | "pending"
export type Currency = "ARS" | "USD" | "EUR"

// ── Source ───────────────────────────────────────────────────────────────────

export interface Source {
  id: number
  name: string
}

// ── Portfolio ─────────────────────────────────────────────────────────────────

export interface Portfolio {
  id: number
  name: string
  source_id: number
  source_name?: string
  position_count?: number
}

// ── Position ─────────────────────────────────────────────────────────────────

export interface Position {
  id: number
  portfolio_id: number
  asset_id: number
  ticker: string
  quantity: number
  currency: Currency
  valuation: number
  valuation_date: string          // ISO date "YYYY-MM-DD"
  load_type: LoadType
  validation_status: ValidationStatus
}

export interface PositionManualCreate {
  source_name: string
  portfolio_name: string
  ticker: string
  quantity: number
  currency?: Currency             // default "ARS"
  valuation: number
  valuation_date: string          // "YYYY-MM-DD"
}

export interface IngestFileResponse {
  processed: number
  rejected: number
  warnings: string[]
}

export interface IngestPreviewRow {
  ticker: string
  cantidad: number
  moneda: string
  precio: number | null
  fecha: string
  ppc: number | null
  valuacion: number
  valor_inicial: number | null
  rendimiento: number | null
  pct_rendimiento: number | null
  dpt: number | null
  asset_type: string
  complete: boolean
}

export interface IngestPreviewResponse {
  filename: string
  detected_layout: string
  can_confirm: boolean
  missing_columns: string[]
  rows: IngestPreviewRow[]
  processed: number
  rejected: number
  warnings: string[]
}

// ── Portfolio Engine (BN-005) ─────────────────────────────────────────────────

export interface AssetSummary {
  ticker: string
  asset_type?: string
  underlying?: string | null
  valuation: number
  market_value?: number
  cost_basis?: number
  pnl_absolute?: number
  pnl_percentage?: number
  portfolio_weight?: number
  valuation_status?: string
  valuation_trace?: ValuationTrace
  valuation_traces?: ValuationTrace[]
  pct: number
  portfolios: string[]            // list of portfolio names holding this asset
}

export interface ValuationTrace {
  input_ticker?: string
  resolved_symbol?: string
  source?: string
  price?: number | null
  currency?: Currency | string
  timestamp?: string | null
  fetched_at?: string | null
  instrument_type?: string | null
  exchange?: string | null
  quote_unit?: string
  status?: string
  valuation_status?: string
  is_stale?: boolean
  error?: string | null
  quantity?: number
  avg_cost?: number
  market_value?: number
  cost_basis?: number
  pnl_absolute?: number
  pnl_percentage?: number
}

export interface SourceSummary {
  source: string
  valuation: number
  pct: number
}

export interface CurrencySummary {
  currency: Currency
  valuation: number
  pct: number
}

export interface ConsolidatedPortfolio {
  total_valuation: number
  by_asset: AssetSummary[]
  by_source: SourceSummary[]
  by_currency: CurrencySummary[]
}

// ── Unified Ticker Layer (BN-006) ─────────────────────────────────────────────

export interface TickerEntry {
  portfolio: string
  quantity: number
  valuation: number
}

export interface UnifiedTicker {
  ticker: string
  asset_type?: string
  underlying?: string | null
  presence: number                // count of distinct portfolios
  entries: TickerEntry[]
}

// ── Market Data (BN-007b) ─────────────────────────────────────────────────────

export interface PriceRefreshResponse {
  refreshed: number
  prices: Record<string, number | null>
}

export interface CachedPrice {
  price: number
  fetched_at: string              // ISO datetime
  expired: boolean
}

export interface AllPricesResponse {
  prices: Record<string, CachedPrice>
}

// ── Intelligence Layer (BN-013/014/015/016) ───────────────────────────────────

export type SignalValue = "BUY" | "HOLD" | "SELL" | "NEUTRAL"
export type LiquidityLevel = "ALTA" | "MEDIA" | "BAJA"
export type PortfolioStatusValue = "EXPANSIÓN" | "NEUTRAL" | "RIESGO"

export interface TickerSignal {
  ticker: string
  signal: SignalValue
  signal_status?: string
  is_actionable?: boolean
  valuation_status?: string | null
  block_reason?: string | null
  reason: string
  pct: number
}

export interface PortfolioStatus {
  status: PortfolioStatusValue
  insights: string[]
  suggested_action: string
  sell_count: number
  buy_count: number
  hold_count: number
}

export interface ReallocationOpportunity {
  ticker: string
  current_pct: number
  suggested_action: string
}

export interface Rotation {
  from_ticker: string
  to: string
  amount: number
  reason: string
}

export interface ReallocationSuggestion {
  releasable_capital: number
  liquidity_level: LiquidityLevel
  opportunities: ReallocationOpportunity[]
  rotations: Rotation[]
  suggested_action: string
}

// ── Admin ────────────────────────────────────────────────────────────────────

export interface ResetUploadedDataResponse {
  positions_deleted: number
  load_records_deleted: number
  preserved_load_types: LoadType[]
}

// ── API endpoints map ─────────────────────────────────────────────────────────
// Used for documentation. Actual calls go through MinosAPI class.

export const MINOS_ENDPOINTS = {
  // Positions
  createPosition:    "POST   /api/v1/positions",
  listPositions:     "GET    /api/v1/positions?portfolio_name=&source_name=",
  // Portfolio engine
  portfolioSummary:  "GET    /api/v1/portfolio/summary",
  portfolioBySource: "GET    /api/v1/portfolio/by-source",
  portfolioByCurrency: "GET  /api/v1/portfolio/by-currency",
  listPortfolios:    "GET    /api/v1/portfolios",
  // Tickers
  unifiedTickers:    "GET    /api/v1/tickers/unified",
  // Market data
  refreshPrices:     "POST   /api/v1/market/refresh",
  allPrices:         "GET    /api/v1/market/prices",
  // Ingestion
  uploadFile:        "POST   /api/v1/ingest/file",
  previewFile:       "POST   /api/v1/ingest/preview",
  resetUploadedData: "POST   /api/v1/admin/reset-uploaded-data",
  // Intelligence
  signals:           "GET    /api/v1/intelligence/signals",
  portfolioStatus:   "GET    /api/v1/intelligence/portfolio-status",
  reallocation:      "GET    /api/v1/intelligence/reallocation",
} as const
