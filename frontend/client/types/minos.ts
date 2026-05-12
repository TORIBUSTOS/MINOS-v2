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

export type IngestActionHint = "CREATE" | "UPDATE" | "IGNORE" | "REVIEW"

export interface IngestPreviewRow {
  ticker: string
  cantidad: number
  quantity: number
  moneda: string
  currency: string
  precio: number | null
  price: number | null
  fecha: string
  ppc: number | null
  valuacion: number
  market_value: number
  valor_inicial: number | null
  initial_value: number | null
  rendimiento: number | null
  return_value: number | null
  pct_rendimiento: number | null
  return_pct: number | null
  dpt: number | null
  asset_type: string
  source_row: number
  source_section: string | null
  confidence: number
  action_hint: IngestActionHint
  complete: boolean
}

export interface IngestRejectedRow {
  row_number: number
  reason: string
  raw: Record<string, string>
}

export interface IngestPreviewSummary {
  detected: number
  rejected: number
  warnings: number
  actions: Record<IngestActionHint, number>
}

export interface IngestPreviewResponse {
  preview_id: string
  filename: string
  source_name: string | null
  portfolio_name: string | null
  detected_layout: string
  can_confirm: boolean
  expires_at: string
  missing_columns: string[]
  detected_positions: IngestPreviewRow[]
  rows: IngestPreviewRow[]
  rejected_rows: IngestRejectedRow[]
  processed: number
  rejected: number
  warnings: string[]
  summary: IngestPreviewSummary
}

// ── Portfolio Engine (BN-005) ─────────────────────────────────────────────────

export interface AssetSummary {
  ticker: string
  asset_type?: string
  underlying?: string | null
  is_liquidity?: boolean
  liquidity_kind?: string | null
  valuation: number
  market_value?: number
  cost_basis?: number
  pnl_absolute?: number
  pnl_percentage?: number
  portfolio_weight?: number
  valuation_status?: string
  day_change?: number | null
  day_change_pct?: number | null
  day_impact?: number | null
  data_freshness?: string
  market_state?: string
  last_market_time?: string | null
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
  previous_close?: number | null
  day_change?: number | null
  day_change_pct?: number | null
  day_impact?: number | null
  daily_impact_status?: string
  data_freshness?: string
  market_state?: string
  last_market_time?: string | null
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
  live_market?: LiveMarketSummary
  liquidity_summary?: LiquiditySummary
}

export interface LiveMarketSummary {
  daily_pnl_total: number
  daily_pnl_pct: number
  positive_count: number
  negative_count: number
  unchanged_count: number
  unavailable_count: number
  freshness_summary: Record<string, number>
  last_market_time: string | null
}

export interface LiquidityItem {
  ticker: string
  asset_type: string
  liquidity_kind: string
  valuation: number
  pct: number
  currencies: Currency[] | string[]
  sources: string[]
}

export interface LiquidityCurrencySummary {
  currency: Currency | string
  valuation: number
  pct: number
}

export interface LiquiditySummary {
  is_informed: boolean
  total: number
  pct: number
  by_currency: LiquidityCurrencySummary[]
  items: LiquidityItem[]
  available_after_reallocation: number | null
  status: "INFORMED" | "NOT_INFORMED" | string
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
  informed_liquidity?: number | null
  available_capital?: number
  liquidity_level: LiquidityLevel
  opportunities: ReallocationOpportunity[]
  rotations: Rotation[]
  suggested_action: string
}

// ── Portfolio snapshots / change detection ──────────────────────────────────

export type SnapshotChangeSeverity = "INFO" | "WARN" | "ACTION"

export interface PortfolioSnapshot {
  id: number
  snapshot_id: string
  created_at: string
  trigger: string
  total_valuation: number
  by_asset: AssetSummary[]
  by_source: SourceSummary[]
  by_currency: CurrencySummary[]
  live_market?: LiveMarketSummary | null
  source_load_record_id?: number | null
  notes: string[]
  warnings: string[]
}

export interface SnapshotChange {
  ticker: string
  change_type: string
  severity: SnapshotChangeSeverity
  before: unknown
  after: unknown
  reason: string
  delta?: number
  pct_change?: number | null
}

export interface PortfolioSnapshotDiffSummary {
  from_snapshot_id: string
  to_snapshot_id: string
  from_created_at: string
  to_created_at: string
  total_valuation_before: number
  total_valuation_after: number
  total_valuation_delta: number
  total_valuation_pct_change: number | null
  change_count: number
  severity_counts: Record<SnapshotChangeSeverity, number>
  has_changes: boolean
}

export interface PortfolioSnapshotDiff {
  from_snapshot: PortfolioSnapshot
  to_snapshot: PortfolioSnapshot
  new_positions: SnapshotChange[]
  removed_positions: SnapshotChange[]
  quantity_changes: SnapshotChange[]
  valuation_changes: SnapshotChange[]
  signal_changes: SnapshotChange[]
  freshness_changes: SnapshotChange[]
  large_moves: SnapshotChange[]
  summary: PortfolioSnapshotDiffSummary
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
  snapshotDiffLatest: "GET   /api/v1/portfolio/snapshots/diff/latest",
} as const
