"use client"

import React from "react"
import {
  ArrowUpRight,
  Download,
  Filter,
  RefreshCw,
  Search,
  Wallet,
} from "lucide-react"
import { useRouter } from "next/navigation"

import { ErrorState, GlowOrb, LoadingState, SectionPanel } from "@/components/dashboard/dashboard-ui"
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
  quantity: number | null
  price: number | null
  priceTime: string | null
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
  return {
    ticker: asset.ticker,
    category: getAssetCategory(asset.ticker),
    quantity: numberOrNull(trace.quantity),
    price: numberOrNull(trace.price),
    priceTime: trace.timestamp ?? trace.fetched_at ?? null,
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

function statusClassName(status: string): string {
  if (status === "OK") return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
  return "bg-rose-500/10 text-rose-400 border-rose-500/25"
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
    <div className="flex flex-col gap-6 animate-fade-up">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground font-display">Mis Instrumentos</h1>
          <p className="text-muted-foreground text-sm font-medium">Valuación broker-grade por ticker, con pricing y rendimiento trazables.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="rounded-xl h-9 font-bold bg-muted/10 border-border/50 hover:bg-primary/5 hover:text-primary transition-all gap-2"
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
            className="rounded-xl h-9 font-bold shadow-lg shadow-primary/20 gap-2"
          >
            <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} />
            Actualizar
          </Button>
        </div>
      </div>

      <SectionPanel className="flex flex-col overflow-hidden">
        <GlowOrb className="w-56 h-56 -bottom-24 -right-24 bg-primary/5" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Buscar ticker, fuente o cartera..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="pl-9 rounded-xl border-border/50 bg-muted/10 focus:ring-primary/20 transition-all h-10 text-sm"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="size-3.5 text-muted-foreground" />
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48 rounded-xl h-9 border-border/50 bg-muted/10 text-xs font-bold">
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

        <div className="rounded-xl border border-border/40 overflow-x-auto bg-surface-elevated/30 backdrop-blur-sm">
          <Table className="min-w-[1320px]">
            <TableHeader className="bg-muted/30">
              <TableRow className="hover:bg-transparent border-border/40">
                <TableHead className="w-[150px] text-[10px] uppercase tracking-widest font-bold">Ticker</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">Nominales</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">Precio</TableHead>
                <TableHead className="text-[10px] uppercase tracking-widest font-bold">Fecha precio</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">PPC</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">V. Actual</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">V. Inicial</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">Rend. $</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">Variación</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">% Cartera</TableHead>
                <TableHead className="text-center text-[10px] uppercase tracking-widest font-bold">Estado</TableHead>
                <TableHead className="text-center text-[10px] uppercase tracking-widest font-bold">Señal</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">Acción</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredRows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={13} className="h-48 text-center">
                    <div className="flex flex-col items-center justify-center text-muted-foreground gap-2">
                      <Wallet className="size-8 opacity-20" />
                      <p className="text-sm font-medium">No se encontraron instrumentos.</p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                filteredRows.map((row) => {
                  const signal = signalMap[row.ticker] ?? "NEUTRAL"
                  const signalStyle = SIGNAL_STYLE[signal]
                  const color = assetColor(row.category)
                  const hasPricingWarning = row.valuationStatus !== "OK"

                  return (
                    <TableRow
                      key={row.ticker}
                      className={`group border-border/40 transition-colors ${hasPricingWarning ? "bg-rose-500/[0.03] hover:bg-rose-500/[0.06]" : "hover:bg-muted/20"}`}
                    >
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-3">
                          <div
                            className="size-9 rounded-lg bg-surface-elevated border border-border/40 flex items-center justify-center font-bold text-xs group-hover:bg-primary/5 transition-colors"
                            style={{ borderLeft: `3px solid ${color}` }}
                          >
                            {row.ticker.substring(0, 4)}
                          </div>
                          <div className="flex flex-col">
                            <span className="font-display font-bold text-sm tracking-tight group-hover:text-primary transition-colors">{row.ticker}</span>
                            <span className="text-[10px] text-muted-foreground font-medium">{row.portfolios.join(", ") || "-"}</span>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-mono text-xs font-semibold">{formatMaybeNumber(row.quantity)}</TableCell>
                      <TableCell className="text-right font-mono text-xs font-semibold">{formatMaybeMoney(row.price)}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">{formatPriceTime(row.priceTime)}</TableCell>
                      <TableCell className="text-right font-mono text-xs font-semibold">{formatMaybeMoney(row.avgCost)}</TableCell>
                      <TableCell className="text-right font-mono text-xs font-bold text-foreground">{formatARS(row.marketValue)}</TableCell>
                      <TableCell className="text-right font-mono text-xs font-semibold text-muted-foreground">{formatARS(row.costBasis)}</TableCell>
                      <TableCell className="text-right font-mono text-xs font-bold">{formatARS(row.pnlAbsolute)}</TableCell>
                      <TableCell className="text-right font-mono text-xs font-bold">{formatPct(row.pnlPercentage)}</TableCell>
                      <TableCell className="text-right font-mono text-xs font-bold">{formatPctAlloc(row.portfolioWeight)}</TableCell>
                      <TableCell className="text-center">
                        <Badge className={`text-[9px] font-black tracking-widest border px-2 py-0.5 ${statusClassName(row.valuationStatus)}`}>
                          {row.valuationStatus}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge className={`text-[9px] font-bold tracking-wider border px-2 py-0.5 opacity-70 ${signalStyle.className}`}>
                          {signalStyle.label}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-8 rounded-lg hover:bg-primary/10 hover:text-primary group/btn transition-all"
                          onClick={() => router.push(`/tickers?q=${encodeURIComponent(row.ticker)}`)}
                          title={`Ver ${row.ticker} en Tickers Unificados`}
                        >
                          <ArrowUpRight className="size-4 group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })
              )}
            </TableBody>
          </Table>
        </div>
      </SectionPanel>
    </div>
  )
}
