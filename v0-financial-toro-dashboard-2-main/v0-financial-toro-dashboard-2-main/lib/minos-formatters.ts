/**
 * MINOS PRIME — Argentine financial formatters
 *
 * Argentina uses: period as thousands separator, comma as decimal.
 * Example: $ 21.041.244,07
 *
 * Dual currency context: ARS (pesos) and USD (dólares).
 * US Dollar (Cable) ≠ Dólar MEP — both shown in UI.
 */

import type { Currency } from "@/types/minos"

// ── Locale config ─────────────────────────────────────────────────────────────

const AR_LOCALE = "es-AR"

// ── Currency formatters ───────────────────────────────────────────────────────

/**
 * Format a value as ARS (pesos argentinos).
 * Output: $ 21.041.244,07
 */
export function formatARS(value: number, decimals = 2): string {
  return new Intl.NumberFormat(AR_LOCALE, {
    style: "currency",
    currency: "ARS",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

/**
 * Format a value as USD.
 * Output: u$s 1.868,04
 * (Argentine convention uses "u$s" prefix for USD)
 */
export function formatUSD(value: number, decimals = 2): string {
  const formatted = new Intl.NumberFormat(AR_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
  return `u$s ${formatted}`
}

/**
 * Format by currency type — picks ARS or USD formatter automatically.
 */
export function formatByCurrency(
  value: number,
  currency: Currency,
  decimals = 2,
): string {
  if (currency === "USD") return formatUSD(value, decimals)
  return formatARS(value, decimals)
}

/**
 * Compact format for large ARS values (KPI cards).
 * 21_041_244 → "$ 21,0 M"
 * 1_500_000  → "$ 1,5 M"
 * 450_000    → "$ 450 K"
 */
export function formatARSCompact(value: number): string {
  if (value >= 1_000_000) {
    return `$ ${(value / 1_000_000).toLocaleString(AR_LOCALE, {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    })} M`
  }
  if (value >= 1_000) {
    return `$ ${(value / 1_000).toLocaleString(AR_LOCALE, {
      minimumFractionDigits: 0,
      maximumFractionDigits: 1,
    })} K`
  }
  return formatARS(value, 0)
}

// ── Percentage formatters ─────────────────────────────────────────────────────

/**
 * Format a percentage with sign.
 * Output: "+5,43%" or "-1,16%"
 */
export function formatPct(value: number, decimals = 2): string {
  const sign = value >= 0 ? "+" : ""
  return `${sign}${value.toLocaleString(AR_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}%`
}

/**
 * Format a percentage without sign (for allocation/distribution).
 * Output: "14,11%"
 */
export function formatPctAlloc(value: number, decimals = 2): string {
  return `${value.toLocaleString(AR_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}%`
}

// ── Number formatters ─────────────────────────────────────────────────────────

/**
 * Format a plain number with AR locale (no currency symbol).
 * Output: "1.700" or "80"
 */
export function formatQty(value: number, decimals = 0): string {
  return value.toLocaleString(AR_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

// ── Date formatters ───────────────────────────────────────────────────────────

/**
 * Format ISO date string to DD/MM/YYYY (Argentine convention).
 * Input:  "2024-01-15"
 * Output: "15/01/2024"
 */
export function formatDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-")
  return `${day}/${month}/${year}`
}

/**
 * Relative date label (for "last updated" indicators).
 */
export function formatRelativeTime(isoDatetime: string): string {
  const diff = Date.now() - new Date(isoDatetime).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1)  return "hace un momento"
  if (mins < 60) return `hace ${mins} min`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24)  return `hace ${hrs} h`
  return `hace ${Math.floor(hrs / 24)} días`
}

// ── Color helpers ─────────────────────────────────────────────────────────────

/**
 * Return Tailwind CSS class for positive/negative values.
 * Used on rendimiento and variación columns.
 */
export function rendimientoColor(value: number): string {
  if (value > 0) return "text-emerald-500"
  if (value < 0) return "text-rose-500"
  return "text-muted-foreground"
}

/**
 * Palette for up to 10 asset categories (Balanz-inspired).
 * Bonos=blue, Acciones=green, Cedears=amber, Fondos=purple, Corporativos=teal
 */
export const ASSET_COLORS: Record<string, string> = {
  Acciones:      "#22c55e",   // green-500
  Bonos:         "#3b82f6",   // blue-500
  Cedears:       "#f59e0b",   // amber-500
  Fondos:        "#a855f7",   // purple-500
  Corporativos:  "#14b8a6",   // teal-500
  Packs:         "#f97316",   // orange-500
  default:       "#94a3b8",   // slate-400
}

export function assetColor(category: string): string {
  return ASSET_COLORS[category] ?? ASSET_COLORS.default
}
/**
 * Shared category mapping for when backend doesn't provide metadata.
 * Based on quasi-actual data from Balanz screenshots.
 */
export const TICKER_CATEGORIES: Record<string, string> = {
  // Acciones
  BMA: "Acciones", ECOG: "Acciones", GGAL: "Acciones", PAMP: "Acciones", 
  SUPV: "Acciones", YPFD: "Acciones", ALUA: "Acciones", TXAR: "Acciones",
  EDN: "Acciones", CEPU: "Acciones", COME: "Acciones", TRAN: "Acciones",
  TECO2: "Acciones",
  // Bonos
  AE38: "Bonos", AL30: "Bonos", GD30: "Bonos", GD38: "Bonos", 
  AL29: "Bonos", GD29: "Bonos", GD35: "Bonos",
  // Cedears
  EEM: "Cedears", MELI: "Cedears", META: "Cedears", MSFT: "Cedears",
  NFLX: "Cedears", NVDA: "Cedears", QQQ: "Cedears", SPY: "Cedears",
  TSM: "Cedears", AAPL: "Cedears", AMZN: "Cedears", TSLA: "Cedears",
  KO: "Cedears", DIA: "Cedears", GOOGL: "Cedears",
  // Corporativos / ONs
  IRCPO: "Corporativos",
}

/**
 * Heuristic to categorize a ticker based on the map or its name.
 */
export function getAssetCategory(ticker: string): string {
  const upperTicker = ticker.toUpperCase()
  if (TICKER_CATEGORIES[upperTicker]) return TICKER_CATEGORIES[upperTicker]
  
  if (
    upperTicker.startsWith("BALANZ") || 
    upperTicker.includes("FCI") || 
    upperTicker.includes("FONDO") ||
    upperTicker.includes("BCMM") ||
    upperTicker.includes("PRIVAD")
  ) {
    return "Fondos"
  }
  
  return "Otros"
}
