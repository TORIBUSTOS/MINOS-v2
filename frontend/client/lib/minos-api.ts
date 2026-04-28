/**
 * MINOS PRIME — API Client
 * Typed wrapper over fetch for all MINOS backend endpoints.
 * Base URL from NEXT_PUBLIC_MINOS_API_URL (default: http://localhost:8800)
 */

import type {
  Position,
  PositionManualCreate,
  ConsolidatedPortfolio,
  SourceSummary,
  CurrencySummary,
  Portfolio,
  UnifiedTicker,
  PriceRefreshRequest,
  PriceRefreshResponse,
  AllPricesResponse,
  TickerSignal,
  PortfolioStatus,
  ReallocationSuggestion,
} from "@/types/minos"

// ── Config ───────────────────────────────────────────────────────────────────

const BASE_URL =
  process.env.NEXT_PUBLIC_MINOS_API_URL ?? "http://localhost:8800"

// ── Error handling ────────────────────────────────────────────────────────────

export class MinosApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(`MINOS API ${status}: ${detail}`)
    this.name = "MinosApiError"
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })

  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body?.detail ?? detail
    } catch {}
    throw new MinosApiError(res.status, detail)
  }

  // 204 No Content
  if (res.status === 204) return undefined as T

  return res.json() as Promise<T>
}

// ── API Methods ───────────────────────────────────────────────────────────────

export const MinosAPI = {

  // ── Positions ──────────────────────────────────────────────────────────────

  /** GET /api/v1/positions — list all positions, optionally filtered */
  async listPositions(filters?: {
    portfolio_name?: string
    source_name?: string
  }): Promise<Position[]> {
    const params = new URLSearchParams()
    if (filters?.portfolio_name) params.set("portfolio_name", filters.portfolio_name)
    if (filters?.source_name)    params.set("source_name", filters.source_name)
    const qs = params.size ? `?${params}` : ""
    return request<Position[]>(`/api/v1/positions${qs}`)
  },

  /** POST /api/v1/positions — manual position entry */
  async createPosition(data: PositionManualCreate): Promise<Position> {
    return request<Position>("/api/v1/positions", {
      method: "POST",
      body: JSON.stringify(data),
    })
  },

  // ── Portfolio Engine ───────────────────────────────────────────────────────

  /** GET /api/v1/portfolio/summary — full consolidation */
  async getPortfolioSummary(): Promise<ConsolidatedPortfolio> {
    return request<ConsolidatedPortfolio>("/api/v1/portfolio/summary")
  },

  /** GET /api/v1/portfolio/by-source — breakdown by broker/source */
  async getPortfolioBySource(): Promise<SourceSummary[]> {
    return request<SourceSummary[]>("/api/v1/portfolio/by-source")
  },

  /** GET /api/v1/portfolio/by-currency — ARS vs USD breakdown */
  async getPortfolioByCurrency(): Promise<CurrencySummary[]> {
    return request<CurrencySummary[]>("/api/v1/portfolio/by-currency")
  },

  /** GET /api/v1/portfolios — list portfolios with position counts */
  async listPortfolios(): Promise<Portfolio[]> {
    return request<Portfolio[]>("/api/v1/portfolios")
  },

  // ── Tickers ────────────────────────────────────────────────────────────────

  /** GET /api/v1/tickers/unified — cross-portfolio ticker aggregation */
  async getUnifiedTickers(): Promise<UnifiedTicker[]> {
    return request<UnifiedTicker[]>("/api/v1/tickers/unified")
  },

  // ── Market Data ────────────────────────────────────────────────────────────

  /** POST /api/v1/market/refresh — force-fetch prices from yfinance */
  async refreshPrices(tickers: string[]): Promise<PriceRefreshResponse> {
    const body: PriceRefreshRequest = { tickers }
    return request<PriceRefreshResponse>("/api/v1/market/refresh", {
      method: "POST",
      body: JSON.stringify(body),
    })
  },

  /** GET /api/v1/market/prices — all cached prices with TTL info */
  async getAllPrices(): Promise<AllPricesResponse> {
    return request<AllPricesResponse>("/api/v1/market/prices")
  },

  // ── Intelligence ───────────────────────────────────────────────────────────

  /** GET /api/v1/intelligence/signals — BUY/HOLD/SELL signal per ticker */
  async getSignals(): Promise<TickerSignal[]> {
    return request<TickerSignal[]>("/api/v1/intelligence/signals")
  },

  /** GET /api/v1/intelligence/portfolio-status — RIESGO/NEUTRAL/EXPANSIÓN */
  async getPortfolioStatus(): Promise<PortfolioStatus> {
    return request<PortfolioStatus>("/api/v1/intelligence/portfolio-status")
  },

  /** GET /api/v1/intelligence/reallocation — capital reallocation suggestions */
  async getReallocation(): Promise<ReallocationSuggestion> {
    return request<ReallocationSuggestion>("/api/v1/intelligence/reallocation")
  },

  // ── Ingestion ──────────────────────────────────────────────────────────────

  /** POST /api/v1/ingest/upload — CSV/XLSX file upload */
  async uploadFile(
    file: File,
    sourceName: string,
    portfolioName: string,
  ): Promise<{ positions_created: number; load_record_id: number }> {
    const form = new FormData()
    form.append("file", file)
    form.append("source_name", sourceName)
    form.append("portfolio_name", portfolioName)
    // Note: no Content-Type header — browser sets multipart boundary
    const res = await fetch(`${BASE_URL}/api/v1/ingest/upload`, {
      method: "POST",
      body: form,
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new MinosApiError(res.status, body?.detail ?? res.statusText)
    }
    return res.json()
  },
}
