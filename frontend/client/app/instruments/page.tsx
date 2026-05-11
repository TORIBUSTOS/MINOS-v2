"use client"

import React from "react"
import {
  ChevronUp,
  Download,
  Filter,
  MoreVertical,
  RefreshCw,
  Search,
} from "lucide-react"
import { useRouter } from "next/navigation"
import { cn } from "@/lib/utils"

import {
  EmptyState,
  ErrorState,
  FinancialMetric,
  LoadingState,
  MobileMetricCard,
  PageHeader,
  ResponsiveFinancialTable,
} from "@/components/dashboard/dashboard-ui"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { usePortfolioSummary, useSignals } from "@/hooks/use-minos"
import { assetColor, formatARS, formatPct, formatPctAlloc, formatPriceTime, formatQty, getAssetCategory } from "@/lib/minos-formatters"
import type { AssetSummary, SignalValue, ValuationTrace } from "@/types/minos"

type BrokerRow = {
  ticker: string
  category: string
  assetType: string
  underlying: string | null
  quantity: number | null
  price: number | null
  priceTime: string | null
  dayChange: number | null
  dayChangePct: number | null
  dayImpact: number | null
  dataFreshness: string
  marketState: string
  lastMarketTime: string | null
  avgCost: number | null
  marketValue: number
  costBasis: number
  pnlAbsolute: number
  pnlPercentage: number
  portfolioWeight: number
  valuationStatus: string
  pricingSource: string
  portfolios: string[]
}

type Density = "comfortable" | "compact" | "dense"
type InstrumentColumn =
  | "quantity"
  | "price"
  | "dayChange"
  | "dayImpact"
  | "avgCost"
  | "marketValue"
  | "costBasis"
  | "pnlAbsolute"
  | "pnlPercentage"
  | "portfolioWeight"
  | "updated"
  | "valuationStatus"
  | "marketStatus"

const DENSITY_CFG: Record<Density, {
  rowH: string
  groupH: string
  headerH: string
  totalsH: string
  px: string
  text: string
  columns: Record<InstrumentColumn, boolean>
}> = {
  comfortable: {
    rowH: "h-8",
    groupH: "h-9",
    headerH: "h-10",
    totalsH: "h-10",
    px: "px-4",
    text: "text-sm",
    columns: {
      quantity: true,
      price: true,
      dayChange: true,
      dayImpact: true,
      avgCost: true,
      marketValue: true,
      costBasis: true,
      pnlAbsolute: true,
      pnlPercentage: true,
      portfolioWeight: true,
      updated: true,
      valuationStatus: true,
      marketStatus: true,
    },
  },
  compact: {
    rowH: "h-[26px]",
    groupH: "h-7",
    headerH: "h-8",
    totalsH: "h-8",
    px: "px-3",
    text: "text-xs",
    columns: {
      quantity: true,
      price: true,
      dayChange: true,
      dayImpact: false,
      avgCost: false,
      marketValue: true,
      costBasis: false,
      pnlAbsolute: true,
      pnlPercentage: true,
      portfolioWeight: true,
      updated: false,
      valuationStatus: true,
      marketStatus: true,
    },
  },
  dense: {
    rowH: "h-6",
    groupH: "h-6",
    headerH: "h-7",
    totalsH: "h-7",
    px: "px-2",
    text: "text-xs",
    columns: {
      quantity: true,
      price: false,
      dayChange: true,
      dayImpact: false,
      avgCost: false,
      marketValue: true,
      costBasis: false,
      pnlAbsolute: true,
      pnlPercentage: false,
      portfolioWeight: true,
      updated: false,
      valuationStatus: true,
      marketStatus: true,
    },
  },
}

const DENSITY_LABEL: Record<Density, string> = {
  comfortable: "Amplio",
  compact: "Compacto",
  dense: "Denso",
}

function getAutoDensity(width: number, height: number): Density {
  if (width >= 1700 && height > 880) return "comfortable"
  if (width >= 1080) return "compact"
  return "dense"
}

const CATEGORY_ORDER = ["Acciones", "Cedears", "Bonos", "Corporativos", "Fondos", "Otros"]

const SIGNAL_STYLE: Record<SignalValue, { label: string; className: string }> = {
  BUY: { label: "BUY", className: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" },
  HOLD: { label: "HOLD", className: "bg-amber-500/10 text-amber-400 border-amber-500/20" },
  SELL: { label: "SELL", className: "bg-rose-500/10 text-rose-400 border-rose-500/20" },
  NEUTRAL: { label: "-", className: "bg-muted/10 text-muted-foreground border-border/20" },
}

function firstTrace(asset: AssetSummary): ValuationTrace {
  return asset.valuation_trace ?? asset.valuation_traces?.[0] ?? {}
}

function numberOrNull(value: number | null | undefined): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null
}

function brokerRowFromAsset(asset: AssetSummary): BrokerRow {
  const trace = firstTrace(asset)
  const assetType = asset.asset_type ?? trace.instrument_type ?? "unknown"
  return {
    ticker: asset.ticker,
    category: getAssetCategory(asset.ticker, assetType),
    assetType,
    underlying: asset.underlying ?? null,
    quantity: numberOrNull(trace.quantity),
    price: numberOrNull(trace.price),
    priceTime: trace.timestamp ?? trace.fetched_at ?? null,
    dayChange: numberOrNull(asset.day_change ?? trace.day_change),
    dayChangePct: numberOrNull(asset.day_change_pct ?? trace.day_change_pct),
    dayImpact: numberOrNull(asset.day_impact ?? trace.day_impact),
    dataFreshness: asset.data_freshness ?? trace.data_freshness ?? "UNAVAILABLE",
    marketState: asset.market_state ?? trace.market_state ?? "UNAVAILABLE",
    lastMarketTime: asset.last_market_time ?? trace.last_market_time ?? null,
    avgCost: numberOrNull(trace.avg_cost),
    marketValue: asset.market_value ?? trace.market_value ?? asset.valuation,
    costBasis: asset.cost_basis ?? trace.cost_basis ?? asset.valuation,
    pnlAbsolute: asset.pnl_absolute ?? trace.pnl_absolute ?? 0,
    pnlPercentage: asset.pnl_percentage ?? trace.pnl_percentage ?? 0,
    portfolioWeight: asset.portfolio_weight ?? asset.pct,
    valuationStatus: asset.valuation_status ?? trace.valuation_status ?? trace.status ?? "UNKNOWN",
    pricingSource: trace.source ?? "portfolio_summary",
    portfolios: asset.portfolios,
  }
}

function formatMaybeMoney(value: number | null): string {
  return value === null ? "-" : formatARS(value)
}

function formatMaybeNumber(value: number | null): string {
  return value === null ? "-" : formatQty(value, 2)
}

function formatTime(value: string | null): string {
  if (!value) return "-"
  return formatPriceTime(value)
}

/** Formato Balanz: "+380,00 (1,00%)" */
function formatDayChange(change: number | null, pct: number | null): string {
  if (change === null || pct === null) return "-"
  const sign = change >= 0 ? "+" : ""
  // Strip currency symbol and spacing added by Intl.
  const amount = formatARS(change).replace(/^\$\s*/u, "")
  return `${sign}${amount} (${formatPct(pct)})`
}

function formatDayChangeCompact(change: number | null, pct: number | null): string {
  if (change === null || pct === null) return "-"
  const sign = change > 0 ? "+" : change < 0 ? "-" : ""
  const amount = formatARS(Math.abs(change)).replace(/^\$\s*/u, "").replace(/,00$/u, "")
  return `${sign}$${amount} (${formatPct(pct)})`
}

const STATUS_ABBR: Record<string, string> = {
  OK:                           "OK",
  CACHED:                       "OK",
  STALE:                        "STALE",
  FALLBACK_STORED_VALUATION:    "STORED",
  NO_DYNAMIC_QUOTE:             "STATIC",
  FETCH_ERROR:                  "ERROR",
}

function statusAbbr(status: string): string {
  return STATUS_ABBR[status] ?? status.split("_")[0]
}

function statusClassName(status: string): string {
  if (status === "OK" || status === "CACHED")
    return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
  if (status === "STALE")
    return "bg-amber-500/10 text-amber-400 border-amber-500/20"
  if (status === "FALLBACK_STORED_VALUATION" || status === "NO_DYNAMIC_QUOTE")
    return "bg-sky-500/10 text-sky-400 border-sky-500/20"
  return "bg-rose-500/10 text-rose-400 border-rose-500/25"
}

function freshnessClassName(freshness: string): string {
  if (freshness === "LIVE")
    return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
  if (freshness === "CACHE")
    return "bg-sky-500/10 text-sky-400 border-sky-500/20"
  if (freshness === "STALE")
    return "bg-amber-500/10 text-amber-400 border-amber-500/20"
  return "bg-muted/10 text-muted-foreground border-border/30"
}

function marketBadgeLabel(row: BrokerRow): string {
  if (row.marketState === "CACHE" || row.dataFreshness === "CACHE") return "CERRADO"
  if (row.marketState === "UNAVAILABLE" || row.dataFreshness === "UNAVAILABLE") return "SIN DATO"
  return row.marketState || row.dataFreshness
}

function marketBadgeTitle(row: BrokerRow): string {
  const time = row.lastMarketTime ? ` · ${formatTime(row.lastMarketTime)}` : ""
  if (row.marketState === "CACHE" || row.dataFreshness === "CACHE") {
    return `Mercado cerrado o sin nueva rueda: usando precio cacheado${time}`
  }
  return `${row.marketState}${time}`
}

function pnlClassName(value: number): string {
  if (value > 0) return "text-fin-gain"
  if (value < 0) return "text-fin-loss"
  return "text-muted-foreground"
}

function groupedRows(rows: BrokerRow[]) {
  const groups = new Map<string, BrokerRow[]>()
  rows.forEach((row) => {
    const group = groups.get(row.category) ?? []
    group.push(row)
    groups.set(row.category, group)
  })

  return CATEGORY_ORDER
    .filter((category) => groups.has(category))
    .map((category) => ({
      category,
      rows: groups.get(category) ?? [],
      totalMarketValue: (groups.get(category) ?? []).reduce((total, row) => total + row.marketValue, 0),
      totalCostBasis: (groups.get(category) ?? []).reduce((total, row) => total + row.costBasis, 0),
      totalPnl: (groups.get(category) ?? []).reduce((total, row) => total + row.pnlAbsolute, 0),
    }))
}

export default function InstrumentsPage() {
  const router = useRouter()
  const { data: summary, loading, error, refetch } = usePortfolioSummary()
  const { data: signals } = useSignals()
  const [search, setSearch] = React.useState("")
  const [statusFilter, setStatusFilter] = React.useState("all")

  // Auto-detect row density from the actual content width, with manual override.
  const [density, setDensity] = React.useState<Density>("comfortable")
  const [densityManual, setDensityManual] = React.useState(false)

  const d = DENSITY_CFG[density]
  const show = d.columns
  const visibleColumnCount = 2 + Object.values(show).filter(Boolean).length

  // Measure from the real DOM position so the table adapts to layout changes.
  const tableWrapperRef = React.useRef<HTMLDivElement>(null)
  const [tableHeight, setTableHeight] = React.useState(400)

  const measureLayout = React.useCallback(() => {
    const el = tableWrapperRef.current
    if (!el) return
    const top = el.getBoundingClientRect().top
    const width = el.clientWidth
    setTableHeight(Math.max(240, window.innerHeight - top - 24))
    if (!densityManual) setDensity(getAutoDensity(width, window.innerHeight))
  }, [densityManual])

  React.useEffect(() => {
    measureLayout()
    window.addEventListener("resize", measureLayout)
    return () => window.removeEventListener("resize", measureLayout)
  }, [measureLayout])

  React.useEffect(() => {
    const query = new URLSearchParams(window.location.search).get("q")
    if (query) setSearch(query)
  }, [])

  const signalMap = React.useMemo(
    () => Object.fromEntries((signals ?? []).map((signal) => [signal.ticker, signal.signal as SignalValue])),
    [signals],
  )

  const rows = React.useMemo(
    () => (summary?.by_asset ?? []).map(brokerRowFromAsset),
    [summary],
  )

  const statusOptions = Array.from(new Set(rows.map((row) => row.valuationStatus).filter(Boolean)))
  const normalizedSearch = search.toLowerCase()
  const filteredRows = rows.filter((row) => {
    const matchesSearch =
      row.ticker.toLowerCase().includes(normalizedSearch) ||
      row.portfolios.join(" ").toLowerCase().includes(normalizedSearch) ||
      row.pricingSource.toLowerCase().includes(normalizedSearch)
    const matchesStatus = statusFilter === "all" || row.valuationStatus === statusFilter
    return matchesSearch && matchesStatus
  })
  const sections = groupedRows(filteredRows)

  // Re-measure after data changes alter the table body.
  React.useEffect(() => {
    measureLayout()
  }, [measureLayout, sections.length])

  const exportCsv = () => {
    const headers = [
      "ticker",
      "quantity",
      "price",
      "price_timestamp",
      "avg_cost",
      "market_value",
      "cost_basis",
      "pnl_absolute",
      "pnl_percentage",
      "portfolio_weight",
      "valuation_status",
      "data_freshness",
      "market_state",
    ]
    const data = filteredRows.map((row) => [
      row.ticker,
      row.quantity,
      row.price,
      row.priceTime,
      row.avgCost,
      row.marketValue,
      row.costBasis,
      row.pnlAbsolute,
      row.pnlPercentage,
      row.portfolioWeight,
      row.valuationStatus,
      row.dataFreshness,
      row.marketState,
    ])
    const escapeCell = (value: unknown) => `"${String(value ?? "").replace(/"/g, '""')}"`
    const csv = [headers, ...data].map((row) => row.map(escapeCell).join(",")).join("\n")
    const blob = new Blob([`${csv}\n`], { type: "text/csv;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = "minos-broker-valuation.csv"
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  if (loading && !summary) return <LoadingState />
  if (error) return <ErrorState error={error} refetch={refetch} />

  return (
    <div className="flex flex-col gap-4 animate-fade-up">
      <PageHeader
        title="Mis Instrumentos"
        subtitle="Tenencias consolidadas por especie, precio y rendimiento."
        actions={
          <>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="h-9 flex-1 rounded-md border-border/60 bg-muted/10 px-3 text-xs font-bold transition-all hover:bg-primary/5 hover:text-primary sm:flex-none"
            onClick={exportCsv}
            disabled={filteredRows.length === 0}
          >
            <Download className="size-3.5" />
            Exportar
          </Button>
          <Button
            onClick={() => refetch()}
            disabled={loading}
            variant="default"
            size="sm"
            className="h-9 flex-1 rounded-md px-3 text-xs font-bold shadow-none gap-2 sm:flex-none"
          >
            <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} />
            Actualizar
          </Button>
          </>
        }
      />

      <div className="flex flex-col gap-3">
        <div className="flex flex-col gap-3 border border-border/50 bg-card/40 px-4 py-3 md:flex-row md:items-center md:justify-between">
          <div className="relative w-full md:max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Buscar ticker, fuente o cartera..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="h-8 rounded-md border-border/60 bg-background/50 pl-9 text-sm transition-all focus:ring-primary/20"
            />
          </div>
          <div className="flex w-full flex-wrap items-center gap-2 md:w-auto">
            <Filter className="size-3.5 text-muted-foreground" />
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="h-8 flex-1 rounded-md border-border/60 bg-background/50 text-xs font-bold md:w-48 md:flex-none">
                <SelectValue placeholder="Estado pricing" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos los estados</SelectItem>
                {statusOptions.map((status) => (
                  <SelectItem key={status} value={status}>{status}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="ml-auto flex h-8 items-center rounded-md border border-border/60 bg-background/50 p-0.5 md:ml-2" role="group" aria-label="Densidad de filas">
              {(["comfortable", "compact", "dense"] as Density[]).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => { setDensity(mode); setDensityManual(true) }}
                  className={cn(
                    "h-7 rounded px-2.5 text-[10px] font-bold transition-all",
                    density === mode
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                  title={DENSITY_LABEL[mode]}
                >
                  {DENSITY_LABEL[mode]}
                </button>
              ))}
            </div>
          </div>
        </div>

        {filteredRows.length === 0 ? (
          <EmptyState title="No se encontraron instrumentos" description="Probá limpiar filtros o cargar una nueva posición." />
        ) : (
          <ResponsiveFinancialTable
            table={
              <div
                ref={tableWrapperRef}
                className="overflow-y-auto overflow-x-hidden border border-border/50 bg-card/25"
                style={{ height: tableHeight }}
              >
                <div className="w-full min-w-0">
                  {sections.map((section) => {
                    const color = assetColor(section.category)

                    return (
                      <section key={section.category} className="border-b border-border/50 last:border-b-0">
                        <div
                          className={cn("flex items-center gap-3 border-b border-border/60 bg-muted/65 px-4", d.groupH)}
                          style={{ borderLeft: `6px solid ${color}` }}
                        >
                          <ChevronUp className="size-4 text-muted-foreground" />
                          <h2 className="text-sm font-bold text-foreground">{section.category} ({section.rows.length})</h2>
                        </div>

                        <Table className="table-fixed">
                          <TableHeader className="sticky top-0 z-10 bg-background/95 backdrop-blur-sm shadow-[0_1px_0_0_hsl(var(--border)/0.5)]">
                            <TableRow className={cn("border-border/60 hover:bg-transparent", d.headerH)}>
                              <TableHead className={cn("w-[7%] text-xs font-bold", d.px)}>Ticker</TableHead>
                              {show.quantity && <TableHead className="w-[6.5%] text-right text-xs font-bold">Nominales</TableHead>}
                              {show.price && <TableHead className="w-[7%] text-right text-xs font-bold">Precio</TableHead>}
                              {show.dayChange && (
                                <TableHead className="w-[8.5%] text-right text-xs font-bold">
                                  <span className="block truncate">Var. Día</span>
                                  <span className="block truncate text-[9px] font-normal tracking-wide text-muted-foreground/70">intradiario</span>
                                </TableHead>
                              )}
                              {show.dayImpact && (
                                <TableHead className="w-[7.5%] text-right text-xs font-bold">
                                  <span className="block">Impacto Día</span>
                                  <span className="block truncate text-[9px] font-normal tracking-wide text-muted-foreground/70">en posición</span>
                                </TableHead>
                              )}
                              {show.avgCost && <TableHead className="w-[6.5%] text-right text-xs font-bold">PPC</TableHead>}
                              {show.marketValue && <TableHead className="w-[8%] bg-muted/35 text-right text-xs font-bold">V. Actual</TableHead>}
                              {show.costBasis && <TableHead className="w-[8%] bg-muted/35 text-right text-xs font-bold">V. Inicial</TableHead>}
                              {show.pnlAbsolute && <TableHead className="w-[8%] bg-muted/35 text-right text-xs font-bold">Rendimiento</TableHead>}
                              {show.pnlPercentage && <TableHead className="w-[6.5%] text-right text-xs font-bold">Var. %</TableHead>}
                              {show.portfolioWeight && <TableHead className="w-[6%] text-right text-xs font-bold">% Cart.</TableHead>}
                              {show.updated && (
                                <TableHead className="w-[6.5%] text-right text-xs font-bold">Actualizado</TableHead>
                              )}
                              {show.valuationStatus && <TableHead className="w-[6.5%] text-center text-xs font-bold">Estado</TableHead>}
                              {show.marketStatus && <TableHead className="w-[6.5%] text-center text-xs font-bold">Mercado</TableHead>}
                              <TableHead className="w-[3.5%] text-center text-xs font-bold" />
                            </TableRow>
                          </TableHeader>

                          <TableBody>
                            <TableRow className={cn("border-border/50 bg-muted/65 hover:bg-muted/65", d.rowH)}>
                              <TableCell colSpan={visibleColumnCount} className={cn("text-xs font-bold text-foreground/80", d.px)}>Pesos</TableCell>
                            </TableRow>

                            {section.rows.map((row) => {
                              const signal = signalMap[row.ticker] ?? "NEUTRAL"
                              const signalStyle = SIGNAL_STYLE[signal]

                              return (
                                <TableRow
                                  key={row.ticker}
                                  className={cn("border-border/50 hover:bg-muted/35", d.rowH, d.text)}
                                >
                                  <TableCell className={cn("min-w-0", d.px)}>
                                    <span
                                      className="block cursor-default truncate font-bold text-slate-300"
                                      title={row.underlying ? `Subyacente: ${row.underlying}` : undefined}
                                    >
                                      {row.ticker}
                                      {row.underlying ? <span className="ml-1 text-[9px] text-muted-foreground/50">◈</span> : null}
                                    </span>
                                  </TableCell>
                                  {show.quantity && <TableCell className="truncate text-right font-mono font-semibold">{formatMaybeNumber(row.quantity)}</TableCell>}
                                  {show.price && <TableCell className="truncate text-right font-mono text-slate-300">{formatMaybeMoney(row.price)}</TableCell>}
                                  {show.dayChange && (
                                    <TableCell
                                      className={cn("truncate text-right font-mono font-bold", row.dayChange === null ? "text-muted-foreground" : pnlClassName(row.dayChange))}
                                      title={formatDayChange(row.dayChange, row.dayChangePct)}
                                    >
                                      {formatDayChange(row.dayChange, row.dayChangePct)}
                                    </TableCell>
                                  )}
                                  {show.dayImpact && (
                                    <TableCell className={cn("text-right font-mono font-bold", row.dayImpact === null ? "text-muted-foreground" : pnlClassName(row.dayImpact))}>
                                      {row.dayImpact === null ? "-" : formatARS(row.dayImpact)}
                                    </TableCell>
                                  )}
                                  {show.avgCost && <TableCell className="truncate text-right font-mono font-semibold">{formatMaybeMoney(row.avgCost)}</TableCell>}
                                  {show.marketValue && <TableCell className="truncate bg-muted/35 text-right font-mono font-bold">{formatARS(row.marketValue)}</TableCell>}
                                  {show.costBasis && <TableCell className="truncate bg-muted/35 text-right font-mono font-semibold">{formatARS(row.costBasis)}</TableCell>}
                                  {show.pnlAbsolute && <TableCell className={cn("truncate bg-muted/35 text-right font-mono font-bold", pnlClassName(row.pnlAbsolute))}>
                                    {formatARS(row.pnlAbsolute)}
                                  </TableCell>}
                                  {show.pnlPercentage && <TableCell className={cn("truncate text-right font-mono font-bold", pnlClassName(row.pnlPercentage))}>
                                    {formatPct(row.pnlPercentage)}
                                  </TableCell>}
                                  {show.portfolioWeight && <TableCell className="truncate text-right font-mono font-semibold">{formatPctAlloc(row.portfolioWeight)}</TableCell>}
                                  {show.updated && (
                                    <TableCell className="text-right font-mono text-xs font-semibold text-muted-foreground tabular-nums">
                                      {formatTime(row.priceTime)}
                                    </TableCell>
                                  )}
                                  {show.valuationStatus && <TableCell className="text-center">
                                    <div className="flex items-center justify-center gap-1">
                                      <Badge
                                        className={cn("border px-1.5 py-0 text-[9px] font-black tracking-widest", statusClassName(row.valuationStatus))}
                                        title={row.valuationStatus}
                                      >
                                        {statusAbbr(row.valuationStatus)}
                                      </Badge>
                                      {signal !== "NEUTRAL" ? (
                                        <Badge className={cn("border px-1.5 py-0 text-[9px] font-bold", signalStyle.className)}>
                                          {signalStyle.label}
                                        </Badge>
                                      ) : null}
                                    </div>
                                  </TableCell>}
                                  {show.marketStatus && <TableCell className="text-center">
                                    <Badge
                                      className={cn("max-w-full truncate border px-1.5 py-0 text-[9px] font-black tracking-widest", freshnessClassName(row.dataFreshness))}
                                      title={marketBadgeTitle(row)}
                                    >
                                      {marketBadgeLabel(row)}
                                    </Badge>
                                  </TableCell>}
                                  <TableCell className="text-center">
                                    <Button
                                      variant="ghost"
                                      size="icon"
                                      className="size-7 rounded-md text-muted-foreground hover:bg-primary/10 hover:text-primary"
                                      onClick={() => router.push(`/tickers?q=${encodeURIComponent(row.ticker)}`)}
                                      title={`Ver ${row.ticker} en Tickers Unificados`}
                                    >
                                      <MoreVertical className="size-4" />
                                    </Button>
                                  </TableCell>
                                </TableRow>
                              )
                            })}

                            <TableRow className={cn("border-border/60 bg-background/40 hover:bg-background/40", d.totalsH)}>
                              <TableCell colSpan={visibleColumnCount} className={cn("bg-muted/20", d.px)}>
                                <div className="flex min-w-0 flex-wrap items-center justify-end gap-x-5 gap-y-1 text-xs">
                                  <span className="font-bold text-muted-foreground">Totales</span>
                                  <span className="font-mono font-bold text-slate-300">Actual {formatARS(section.totalMarketValue)}</span>
                                  {density !== "dense" ? (
                                    <span className="font-mono font-bold text-slate-300">Inicial {formatARS(section.totalCostBasis)}</span>
                                  ) : null}
                                  <span className={cn("font-mono font-bold", pnlClassName(section.totalPnl))}>
                                    P/L {formatARS(section.totalPnl)}
                                  </span>
                                </div>
                              </TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </section>
                    )
                  })}
                </div>
              </div>
            }
            cards={
              sections.map((section) => {
                const color = assetColor(section.category)
                return (
                  <section key={section.category} className="space-y-3">
                    <div
                      className="flex h-11 items-center gap-3 border border-border/50 bg-muted/55 px-3"
                      style={{ borderLeft: `5px solid ${color}` }}
                    >
                      <ChevronUp className="size-4 text-muted-foreground" />
                      <h2 className="text-sm font-bold text-foreground">{section.category} ({section.rows.length})</h2>
                    </div>
                    {section.rows.map((row) => {
                      const signal = signalMap[row.ticker] ?? "NEUTRAL"
                      const signalStyle = SIGNAL_STYLE[signal]
                      return (
                        <MobileMetricCard
                          key={row.ticker}
                          title={row.ticker}
                          subtitle={row.underlying ? `Subyacente: ${row.underlying}` : row.portfolios.join(", ") || section.category}
                          accent={color}
                          meta={
                            <div className="flex flex-col gap-1">
                              <Badge
                                className={cn("border px-1.5 py-0 text-[9px] font-black tracking-widest", statusClassName(row.valuationStatus))}
                                title={row.valuationStatus}
                              >
                                {statusAbbr(row.valuationStatus)}
                              </Badge>
                              {signal !== "NEUTRAL" ? (
                                <Badge className={cn("border px-1.5 py-0 text-[9px] font-bold", signalStyle.className)}>
                                  {signalStyle.label}
                                </Badge>
                              ) : null}
                              <Badge
                                className={cn("border px-1.5 py-0 text-[9px] font-black tracking-widest", freshnessClassName(row.dataFreshness))}
                                title={marketBadgeTitle(row)}
                              >
                                {marketBadgeLabel(row)}
                              </Badge>
                            </div>
                          }
                          action={
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-full rounded-md text-xs font-bold text-primary hover:bg-primary/10"
                              onClick={() => router.push(`/tickers?q=${encodeURIComponent(row.ticker)}`)}
                            >
                              Ver ticker unificado
                            </Button>
                          }
                        >
                          <FinancialMetric label="Nominales" value={formatMaybeNumber(row.quantity)} />
                          {row.underlying ? (
                            <FinancialMetric label="Subyacente" value={row.underlying} className="font-sans text-[12px]" />
                          ) : null}
                          <FinancialMetric label="Precio" value={formatMaybeMoney(row.price)} />
                          <FinancialMetric
                            label="Var. Día"
                            value={formatDayChangeCompact(row.dayChange, row.dayChangePct)}
                            tone={row.dayChange === null ? undefined : row.dayChange >= 0 ? "gain" : "loss"}
                            className="text-[12px]"
                          />
                          <FinancialMetric label="V. Actual" value={formatARS(row.marketValue)} />
                          <FinancialMetric label="Rendimiento" value={formatARS(row.pnlAbsolute)} tone={row.pnlAbsolute < 0 ? "loss" : "gain"} />
                          <FinancialMetric label="Variación" value={formatPct(row.pnlPercentage)} tone={row.pnlPercentage < 0 ? "loss" : "gain"} />
                          <FinancialMetric label="% Cartera" value={formatPctAlloc(row.portfolioWeight)} />
                        </MobileMetricCard>
                      )
                    })}
                    <div className="rounded-xl border border-border/50 bg-background/40 p-3">
                      <div className="grid grid-cols-3 gap-2">
                        <FinancialMetric label="Total" value={formatARS(section.totalMarketValue)} />
                        <FinancialMetric label="Inicial" value={formatARS(section.totalCostBasis)} />
                        <FinancialMetric label="P/L" value={formatARS(section.totalPnl)} tone={section.totalPnl < 0 ? "loss" : "gain"} />
                      </div>
                    </div>
                  </section>
                )
              })
            }
          />
        )}
      </div>
    </div>
  )
}
