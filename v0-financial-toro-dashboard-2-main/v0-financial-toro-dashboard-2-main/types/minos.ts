/**
 * MINOS PRIME — TypeScript types
 * Mirror of Python Pydantic schemas in src/schemas/
 * API base: http://localhost:8001/api/v1
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

// ── Portfolio Engine (BN-005) ─────────────────────────────────────────────────

export interface AssetSummary {
  ticker: string
  valuation: number
  pct: number
  portfolios: string[]            // list of portfolio names holding this asset
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
  presence: number                // count of distinct portfolios
  entries: TickerEntry[]
}

// ── Market Data (BN-007b) ─────────────────────────────────────────────────────

export interface PriceRefreshRequest {
  tickers: string[]
}

export interface PriceRefreshResponse {
  refreshed: Record<string, number | null>
}

export interface CachedPrice {
  price: number
  fetched_at: string              // ISO datetime
  expired: boolean
}

export interface AllPricesResponse {
  prices: Record<string, CachedPrice>
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
  uploadFile:        "POST   /api/v1/ingest/upload",
} as const
