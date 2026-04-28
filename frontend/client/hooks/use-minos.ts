/**
 * MINOS PRIME — React hooks
 * Client-side data fetching with manual refresh.
 * Uses React 19 built-ins: useState + useEffect + useCallback.
 * No extra dependencies needed (no SWR/React Query).
 *
 * Pattern:
 *   const { data, loading, error, refetch } = usePortfolioSummary()
 */

"use client"

import { useState, useEffect, useCallback } from "react"
import { MinosAPI, MinosApiError } from "@/lib/minos-api"
import type {
  ConsolidatedPortfolio,
  SourceSummary,
  CurrencySummary,
  Portfolio,
  Position,
  UnifiedTicker,
  AllPricesResponse,
  TickerSignal,
  PortfolioStatus,
  ReallocationSuggestion,
} from "@/types/minos"

// ── Generic hook factory ──────────────────────────────────────────────────────

interface UseQueryResult<T> {
  data: T | null
  loading: boolean
  error: MinosApiError | Error | null
  refetch: () => void
}

function useMinosQuery<T>(fetcher: () => Promise<T>): UseQueryResult<T> {
  const [data, setData]       = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState<MinosApiError | Error | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetcher()
      setData(result)
    } catch (e) {
      setError(e instanceof Error ? e : new Error(String(e)))
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => { fetch() }, [fetch])

  return { data, loading, error, refetch: fetch }
}

// ── Portfolio hooks ───────────────────────────────────────────────────────────

/**
 * Full portfolio consolidation: total_valuation, by_asset, by_source, by_currency.
 * Powers the Dashboard KPI cards + donut chart.
 */
export function usePortfolioSummary() {
  return useMinosQuery<ConsolidatedPortfolio>(
    () => MinosAPI.getPortfolioSummary()
  )
}

/**
 * Breakdown by broker/source (Balanz, IOL, Manual...).
 * Powers the "Por Fuente" view — the killer feature vs single-broker apps.
 */
export function usePortfolioBySource() {
  return useMinosQuery<SourceSummary[]>(
    () => MinosAPI.getPortfolioBySource()
  )
}

/**
 * ARS vs USD breakdown.
 * Powers the currency exposure bar.
 */
export function usePortfolioByCurrency() {
  return useMinosQuery<CurrencySummary[]>(
    () => MinosAPI.getPortfolioByCurrency()
  )
}

/**
 * All portfolios with position counts.
 * Powers the portfolio selector/sidebar.
 */
export function usePortfolios() {
  return useMinosQuery<Portfolio[]>(
    () => MinosAPI.listPortfolios()
  )
}

// ── Position hooks ────────────────────────────────────────────────────────────

/**
 * All positions, optionally filtered by portfolio or source.
 * Powers the "Mis Instrumentos" table (like Balanz's instrument list).
 */
export function usePositions(filters?: {
  portfolio_name?: string
  source_name?: string
}) {
  return useMinosQuery<Position[]>(
    () => MinosAPI.listPositions(filters)
  )
}

// ── Ticker hooks ──────────────────────────────────────────────────────────────

/**
 * Cross-portfolio ticker unification.
 * Shows presence (how many portfolios hold this ticker) without summing quantities.
 */
export function useUnifiedTickers() {
  return useMinosQuery<UnifiedTicker[]>(
    () => MinosAPI.getUnifiedTickers()
  )
}

// ── Intelligence hooks ────────────────────────────────────────────────────────

/**
 * Per-ticker BUY/HOLD/SELL signals from the Intelligence Engine.
 * Replaces the mock hash-based signal in the Tickers page.
 */
export function useSignals() {
  return useMinosQuery<TickerSignal[]>(
    () => MinosAPI.getSignals()
  )
}

/**
 * Portfolio-level status: RIESGO | NEUTRAL | EXPANSIÓN.
 * Powers the intelligence banner on the Dashboard.
 */
export function usePortfolioStatus() {
  return useMinosQuery<PortfolioStatus>(
    () => MinosAPI.getPortfolioStatus()
  )
}

/**
 * Capital reallocation suggestions: releasable capital, rotations, opportunities.
 */
export function useReallocation() {
  return useMinosQuery<ReallocationSuggestion>(
    () => MinosAPI.getReallocation()
  )
}

// ── Market data hooks ─────────────────────────────────────────────────────────

/**
 * All cached prices with TTL metadata.
 * Powers the price column and "last updated" indicator.
 */
export function useMarketPrices() {
  return useMinosQuery<AllPricesResponse>(
    () => MinosAPI.getAllPrices()
  )
}

/**
 * Trigger a price refresh for a list of tickers.
 * Returns { refresh, loading, error } — call refresh(tickers) on demand.
 */
export function useRefreshPrices() {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<MinosApiError | Error | null>(null)

  const refresh = useCallback(async (tickers: string[]) => {
    setLoading(true)
    setError(null)
    try {
      return await MinosAPI.refreshPrices(tickers)
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      setError(err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { refresh, loading, error }
}

// ── File upload hook ──────────────────────────────────────────────────────────

/**
 * CSV/XLSX ingestion.
 * Returns { upload, loading, error, result } — call upload(file, source, portfolio).
 */
export function useFileUpload() {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<MinosApiError | Error | null>(null)
  const [result, setResult]   = useState<{
    positions_created: number
    load_record_id: number
  } | null>(null)

  const upload = useCallback(async (
    file: File,
    sourceName: string,
    portfolioName: string,
  ) => {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await MinosAPI.uploadFile(file, sourceName, portfolioName)
      setResult(res)
      return res
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      setError(err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { upload, loading, error, result }
}

/**
 * Manual position entry.
 * Returns { add, loading, error } — call add(data).
 */
export function useCreatePosition() {
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState<MinosApiError | Error | null>(null)

  const add = useCallback(async (data: any) => {
    setLoading(true)
    setError(null)
    try {
      return await MinosAPI.createPosition(data)
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      setError(err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return { add, loading, error }
}
