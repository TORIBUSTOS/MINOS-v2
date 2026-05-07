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
import { assetColor, formatARS, formatPct, formatPctAlloc, formatQty, formatRelativeTime, getAssetCategory } from "@/lib/minos-formatters"
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
    dayChange: numberOrNull(trace.day_change),
    dayChangePct: numberOrNull(trace.day_change_pct),
    dayImpact: numberOrNull(trace.day_impact),
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

function formatPriceTime(value: string | null): string {
  if (!value) return "-"
  return formatRelativeTime(value)
}

/** Formato Balanz: "+380,00 (1,00%)" */
function formatDayChange(change: number | null, pct: number | null): string {
  if (change === null || pct === null) return "-"
  const sign = change >= 0 ? "+" : ""
  // strip currency symbol + any Unicode whitespace (Intl puede usar   o  )
  const amount = formatARS(change).replace(/^\$\s*/u, "")
  return `${sign}${amount} (${formatPct(pct)})`
}

function statusClassName(status: string): string {
  if (status === "OK") return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
  return "bg-rose-500/10 text-rose-400 border-rose-500/25"
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
          <div className="flex w-full items-center gap-2 md:w-auto">
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
          </div>
        </div>

        {filteredRows.length === 0 ? (
          <EmptyState title="No se encontraron instrumentos" description="Probá limpiar filtros o cargar una nueva posición." />
        ) : (
          <ResponsiveFinancialTable
            table={
          <div className="overflow-x-auto border border-border/50 bg-card/25">
            <div className="min-w-[1700px]">
              {sections.map((section) => {
                const color = assetColor(section.category)

                return (
                  <section key={section.category} className="border-b border-border/50 last:border-b-0">
                    <div
                      className="flex h-12 items-center gap-3 border-b border-border/60 bg-muted/65 px-4"
                      style={{ borderLeft: `6px solid ${color}` }}
                    >
                      <ChevronUp className="size-4 text-muted-foreground" />
                      <h2 className="text-sm font-bold text-foreground">{section.category} ({section.rows.length})</h2>
                    </div>

                    <Table>
                      <TableHeader className="bg-background/50">
                        <TableRow className="h-10 border-border/60 hover:bg-transparent">
                          <TableHead className="w-[120px] px-4 text-xs font-bold">Ticker</TableHead>
                          <TableHead className="w-[120px] text-right text-xs font-bold">Nominales</TableHead>
                          <TableHead className="w-[140px] text-right text-xs font-bold">Precio</TableHead>
                          <TableHead className="w-[180px] text-right text-xs font-bold">
                            <span className="block">Var. Día</span>
                            <span className="block text-[9px] font-normal text-muted-foreground/70 tracking-wide">intradiario</span>
                          </TableHead>
                          <TableHead className="w-[130px] text-right text-xs font-bold">
                            <span className="block">Impacto Día</span>
                            <span className="block text-[9px] font-normal text-muted-foreground/70 tracking-wide">en posición</span>
                          </TableHead>
                          <TableHead className="w-[120px] text-right text-xs font-bold">PPC</TableHead>
                          <TableHead className="w-[150px] text-right text-xs font-bold bg-muted/35">V. Actual</TableHead>
                          <TableHead className="w-[150px] text-right text-xs font-bold bg-muted/35">V. Inicial</TableHead>
                          <TableHead className="w-[150px] text-right text-xs font-bold bg-muted/35">Rendimiento</TableHead>
                          <TableHead className="w-[130px] text-right text-xs font-bold">Variación (%)</TableHead>
                          <TableHead className="w-[110px] text-right text-xs font-bold">% Cartera</TableHead>
                          <TableHead className="w-[112px] text-right text-xs font-bold">Actualizado</TableHead>
                          <TableHead className="w-[120px] text-center text-xs font-bold">Estado</TableHead>
                          <TableHead className="w-[64px] text-center text-xs font-bold" />
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow className="h-9 border-border/50 bg-muted/65 hover:bg-muted/65">
                          <TableCell colSpan={14} className="px-4 text-xs font-bold text-foreground/80">Pesos</TableCell>
                        </TableRow>

                        {section.rows.map((row) => {
                          const signal = signalMap[row.ticker] ?? "NEUTRAL"
                          const signalStyle = SIGNAL_STYLE[signal]

                          return (
                            <TableRow
                              key={row.ticker}
                              className="h-11 border-border/50 text-sm hover:bg-muted/35"
                            >
                              <TableCell className="px-4">
                                <div className="flex flex-col leading-tight">
                                  <span className="font-bold text-slate-300">{row.ticker}</span>
                                  {row.underlying ? (
                                    <span className="mt-1 max-w-[160px] truncate text-[10px] font-semibold text-muted-foreground">
                                      Suby.: {row.underlying}
                                    </span>
                                  ) : null}
                                </div>
                              </TableCell>
                              <TableCell className="text-right font-mono font-semibold">{formatMaybeNumber(row.quantity)}</TableCell>
                              <TableCell className="text-right font-mono text-slate-300">{formatMaybeMoney(row.price)}</TableCell>
                              <TableCell className={`text-right font-mono font-bold ${row.dayChange === null ? "text-muted-foreground" : pnlClassName(row.dayChange)}`}>
                                {formatDayChange(row.dayChange, row.dayChangePct)}
                              </TableCell>
                              <TableCell className={`text-right font-mono font-bold ${row.dayImpact === null ? "text-muted-foreground" : pnlClassName(row.dayImpact)}`}>
                                {row.dayImpact === null ? "-" : formatARS(row.dayImpact)}
                              </TableCell>
                              <TableCell className="text-right font-mono font-semibold">{formatMaybeMoney(row.avgCost)}</TableCell>
                              <TableCell className="text-right font-mono font-bold bg-muted/35">{formatARS(row.marketValue)}</TableCell>
                              <TableCell className="text-right font-mono font-semibold bg-muted/35">{formatARS(row.costBasis)}</TableCell>
                              <TableCell className={`text-right font-mono font-bold bg-muted/35 ${pnlClassName(row.pnlAbsolute)}`}>
                                {formatARS(row.pnlAbsolute)}
                              </TableCell>
                              <TableCell className={`text-right font-mono font-bold ${pnlClassName(row.pnlPercentage)}`}>
                                {formatPct(row.pnlPercentage)}
                              </TableCell>
                              <TableCell className="text-right font-mono font-semibold">{formatPctAlloc(row.portfolioWeight)}</TableCell>
                              <TableCell className="text-right font-mono font-semibold text-muted-foreground">
                                {row.priceTime ? formatPriceTime(row.priceTime) : "-"}
                              </TableCell>
                              <TableCell className="text-center">
                                <Badge className={`border px-2 py-0.5 text-[9px] font-black tracking-widest ${statusClassName(row.valuationStatus)}`}>
                                  {row.valuationStatus}
                                </Badge>
                                {signal !== "NEUTRAL" ? (
                                  <Badge className={`ml-1 border px-1.5 py-0.5 text-[9px] font-bold ${signalStyle.className}`}>
                                    {signalStyle.label}
                                  </Badge>
                                ) : null}
                              </TableCell>
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

                        <TableRow className="h-10 border-border/60 bg-background/40 hover:bg-background/40">
                          <TableCell colSpan={6} className="text-right text-xs font-bold text-muted-foreground">Totales</TableCell>
                          <TableCell className="text-right font-mono text-sm font-bold bg-muted/35 text-slate-300">{formatARS(section.totalMarketValue)}</TableCell>
                          <TableCell className="text-right font-mono text-sm font-bold bg-muted/35 text-slate-300">{formatARS(section.totalCostBasis)}</TableCell>
                          <TableCell className={`text-right font-mono text-sm font-bold bg-muted/35 ${pnlClassName(section.totalPnl)}`}>
                            {formatARS(section.totalPnl)}
                          </TableCell>
                          <TableCell colSpan={5} />
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
                            <div className="space-y-1">
                              <Badge className={`border px-2 py-0.5 text-[9px] font-black tracking-widest ${statusClassName(row.valuationStatus)}`}>
                                {row.valuationStatus}
                              </Badge>
                              {signal !== "NEUTRAL" ? (
                                <Badge className={`block border px-2 py-0.5 text-[9px] font-bold ${signalStyle.className}`}>
                                  {signalStyle.label}
                                </Badge>
                              ) : null}
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
                            value={formatDayChange(row.dayChange, row.dayChangePct)}
                            tone={row.dayChange === null ? undefined : row.dayChange >= 0 ? "gain" : "loss"}
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
