"use client"

import React from "react"
import { motion } from "motion/react"
import {
  Building2,
  BarChart2,
  PieChart,
  Activity,
  Clock,
  Settings2
} from "lucide-react"
import {
  SectionPanel,
  SectionHeader,
  GlowOrb,
  LoadingState,
  ErrorState
} from "./dashboard-ui"
import { AllocationDonut } from "./allocation-donut"
import { MarketWidget } from "./market-widget"
import { usePortfolioSummary, usePortfolioStatus } from "@/hooks/use-minos"
import type { ConsolidatedPortfolio, PortfolioStatusValue } from "@/types/minos"
import { formatARS, formatARSCompact, formatPct, formatPctAlloc, formatPriceTime } from "@/lib/minos-formatters"
import { cn } from "@/lib/utils"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from "recharts"
import { ShieldAlert, TrendingUp, Minus, ArrowRightLeft, DollarSign as DollarCircle, Lightbulb } from "lucide-react"
import { useReallocation } from "@/hooks/use-minos"

type DashboardKpiId =
  | "total_pnl"
  | "daily_pnl"
  | "top_exposure"
  | "daily_balance"
  | "market_freshness"
  | "last_market_time"
  | "instrument_count"
  | "source_count"
  | "usd_exposure"
  | "unavailable_count"
  | "top_source"
  | "biggest_gain"
  | "biggest_loss"

type DashboardKpi = {
  id: DashboardKpiId
  label: string
  value: string
  subtext: string
  tone?: "default" | "gain" | "loss" | "primary" | "warning"
}

const DASHBOARD_KPI_STORAGE_KEY = "minos.dashboard.kpiSlots.v1"
const DEFAULT_DASHBOARD_KPIS: DashboardKpiId[] = ["total_pnl", "top_exposure", "daily_balance", "market_freshness"]

function signedMoney(value: number): string {
  const sign = value > 0 ? "+" : value < 0 ? "-" : ""
  return `${sign}${formatARS(Math.abs(value))}`
}

function toneFromNumber(value: number | null | undefined): DashboardKpi["tone"] {
  if (value == null) return "default"
  if (value > 0) return "gain"
  if (value < 0) return "loss"
  return "default"
}

function dominantFreshness(data: ConsolidatedPortfolio): string {
  return Object.entries(data.live_market?.freshness_summary ?? {})
    .sort((a, b) => b[1] - a[1])[0]?.[0] ?? "UNAVAILABLE"
}

function buildDashboardKpis(data: ConsolidatedPortfolio): DashboardKpi[] {
  const totalPnl = data.by_asset.reduce((total, asset) => total + (asset.pnl_absolute ?? 0), 0)
  const totalPnlPct = data.total_valuation > totalPnl && data.total_valuation !== 0
    ? (totalPnl / (data.total_valuation - totalPnl)) * 100
    : 0
  const topAsset = [...data.by_asset].sort((a, b) => (b.pct ?? 0) - (a.pct ?? 0))[0]
  const topSource = [...data.by_source].sort((a, b) => (b.pct ?? 0) - (a.pct ?? 0))[0]
  const biggestGain = [...data.by_asset].sort((a, b) => (b.day_change_pct ?? -Infinity) - (a.day_change_pct ?? -Infinity))[0]
  const biggestLoss = [...data.by_asset].sort((a, b) => (a.day_change_pct ?? Infinity) - (b.day_change_pct ?? Infinity))[0]
  const live = data.live_market
  const freshness = dominantFreshness(data)
  const freshnessCount = live?.freshness_summary?.[freshness] ?? 0
  const usd = data.by_currency.find((currency) => currency.currency === "USD")

  return [
    {
      id: "total_pnl",
      label: "Resultado total",
      value: signedMoney(totalPnl),
      subtext: `${formatPct(totalPnlPct)} acumulado`,
      tone: toneFromNumber(totalPnl),
    },
    {
      id: "daily_pnl",
      label: "Impacto día",
      value: live ? signedMoney(live.daily_pnl_total) : "-",
      subtext: live ? formatPct(live.daily_pnl_pct) : "sin dato diario",
      tone: toneFromNumber(live?.daily_pnl_total),
    },
    {
      id: "top_exposure",
      label: "Exposición principal",
      value: topAsset ? `${topAsset.ticker} ${formatPctAlloc(topAsset.pct)}` : "-",
      subtext: "mayor concentración",
      tone: "default",
    },
    {
      id: "daily_balance",
      label: "Balance diario",
      value: live ? `${live.positive_count}+ ${live.negative_count}-` : "-",
      subtext: `${live?.unchanged_count ?? 0} sin cambio`,
      tone: live && live.negative_count > live.positive_count ? "loss" : "gain",
    },
    {
      id: "market_freshness",
      label: "Frescura mercado",
      value: `${freshness} · ${freshnessCount}`,
      subtext: "instrumentos dominantes",
      tone: freshness === "LIVE" ? "gain" : freshness === "STALE" ? "warning" : freshness === "CACHE" ? "primary" : "default",
    },
    {
      id: "last_market_time",
      label: "Último dato",
      value: live?.last_market_time ? formatPriceTime(live.last_market_time) : "-",
      subtext: "timestamp de mercado",
      tone: "default",
    },
    {
      id: "instrument_count",
      label: "Instrumentos",
      value: String(data.by_asset.length),
      subtext: "activos en cartera",
      tone: "default",
    },
    {
      id: "source_count",
      label: "Fuentes",
      value: String(data.by_source.length),
      subtext: "brokers / orígenes",
      tone: "default",
    },
    {
      id: "usd_exposure",
      label: "Exposición USD",
      value: formatPctAlloc(usd?.pct ?? 0),
      subtext: usd ? formatARS(usd.valuation) : "sin USD",
      tone: "primary",
    },
    {
      id: "unavailable_count",
      label: "Sin precio live",
      value: String(live?.unavailable_count ?? 0),
      subtext: "instrumentos unavailable",
      tone: (live?.unavailable_count ?? 0) > 0 ? "warning" : "gain",
    },
    {
      id: "top_source",
      label: "Fuente principal",
      value: topSource ? `${topSource.source} ${formatPctAlloc(topSource.pct)}` : "-",
      subtext: topSource ? formatARS(topSource.valuation) : "sin fuentes",
      tone: "default",
    },
    {
      id: "biggest_gain",
      label: "Mayor suba diaria",
      value: biggestGain ? `${biggestGain.ticker} ${formatPct(biggestGain.day_change_pct ?? 0)}` : "-",
      subtext: biggestGain?.day_impact == null ? "sin impacto" : signedMoney(biggestGain.day_impact),
      tone: "gain",
    },
    {
      id: "biggest_loss",
      label: "Mayor caída diaria",
      value: biggestLoss ? `${biggestLoss.ticker} ${formatPct(biggestLoss.day_change_pct ?? 0)}` : "-",
      subtext: biggestLoss?.day_impact == null ? "sin impacto" : signedMoney(biggestLoss.day_impact),
      tone: "loss",
    },
  ]
}

// ── Intelligence Status Banner ────────────────────────────────────────────────

const STATUS_CONFIG: Record<PortfolioStatusValue, {
  label: string
  icon: React.ElementType
  bg: string
  border: string
  text: string
  dot: string
}> = {
  RIESGO: {
    label: "RIESGO",
    icon: ShieldAlert,
    bg: "bg-rose-500/5",
    border: "border-rose-500/20",
    text: "text-rose-400",
    dot: "bg-rose-500",
  },
  NEUTRAL: {
    label: "NEUTRAL",
    icon: Minus,
    bg: "bg-amber-500/5",
    border: "border-amber-500/20",
    text: "text-amber-400",
    dot: "bg-amber-500",
  },
  EXPANSIÓN: {
    label: "EXPANSIÓN",
    icon: TrendingUp,
    bg: "bg-emerald-500/5",
    border: "border-emerald-500/20",
    text: "text-emerald-400",
    dot: "bg-emerald-500",
  },
}

function IntelligenceBanner() {
  const { data: status } = usePortfolioStatus()
  if (!status) return null

  const cfg = STATUS_CONFIG[status.status]
  const Icon = cfg.icon
  const topInsight = status.insights[0] ?? ""

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.35 }}
      className={`rounded-2xl border px-5 py-4 flex flex-col sm:flex-row sm:items-center gap-3 ${cfg.bg} ${cfg.border}`}
    >
      <div className="flex items-center gap-3 flex-shrink-0">
        <div className={`size-8 rounded-xl flex items-center justify-center ${cfg.bg} border ${cfg.border}`}>
          <Icon className={`size-4 ${cfg.text}`} />
        </div>
        <div className="flex items-center gap-2">
          <div className={`size-2 rounded-full animate-pulse ${cfg.dot}`} />
          <span className={`text-[10px] uppercase tracking-[0.15em] font-black ${cfg.text}`}>{cfg.label}</span>
        </div>
      </div>
      <div className="flex-1 min-w-0 sm:border-l sm:border-current/10 sm:pl-4">
        <p className="text-xs font-semibold text-foreground/80 leading-relaxed truncate">{topInsight}</p>
        {status.suggested_action && (
          <p className="text-[11px] text-muted-foreground/70 mt-0.5 leading-relaxed line-clamp-1">
            {status.suggested_action}
          </p>
        )}
      </div>
      <div className="flex items-center gap-3 flex-shrink-0 text-[10px] font-bold text-muted-foreground">
        <span className="text-rose-400">{status.sell_count} SELL</span>
        <span className="text-amber-400">{status.hold_count} HOLD</span>
        <span className="text-emerald-400">{status.buy_count} BUY</span>
      </div>
    </motion.div>
  )
}

function kpiToneClass(tone: DashboardKpi["tone"]): string {
  if (tone === "gain") return "text-emerald-400"
  if (tone === "loss") return "text-rose-400"
  if (tone === "primary") return "text-sky-400"
  if (tone === "warning") return "text-amber-400"
  return "text-foreground"
}

function loadKpiSlots(): DashboardKpiId[] {
  if (typeof window === "undefined") return DEFAULT_DASHBOARD_KPIS
  try {
    const parsed = JSON.parse(window.localStorage.getItem(DASHBOARD_KPI_STORAGE_KEY) ?? "null")
    if (Array.isArray(parsed) && parsed.length === 4) return parsed as DashboardKpiId[]
  } catch {
    return DEFAULT_DASHBOARD_KPIS
  }
  return DEFAULT_DASHBOARD_KPIS
}

function CapitalOverviewPanel({ data }: { data: ConsolidatedPortfolio }) {
  const [isEditing, setIsEditing] = React.useState(false)
  const [slots, setSlots] = React.useState<DashboardKpiId[]>(DEFAULT_DASHBOARD_KPIS)
  const kpis = React.useMemo(() => buildDashboardKpis(data), [data])
  const kpiMap = React.useMemo(() => new Map(kpis.map((kpi) => [kpi.id, kpi])), [kpis])
  const live = data.live_market
  const freshness = dominantFreshness(data)

  React.useEffect(() => {
    setSlots(loadKpiSlots())
  }, [])

  React.useEffect(() => {
    window.localStorage.setItem(DASHBOARD_KPI_STORAGE_KEY, JSON.stringify(slots))
  }, [slots])

  const updateSlot = (index: number, value: DashboardKpiId) => {
    setSlots((current) => current.map((slot, slotIndex) => slotIndex === index ? value : slot))
  }

  return (
    <SectionPanel delay={0} className="px-5 py-5 sm:px-6 sm:py-6">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <p className="text-[10px] font-black uppercase tracking-[0.16em] text-sky-200/85">Patrimonio consolidado</p>
            <h1 className="mt-1.5 font-mono text-[clamp(1.85rem,6.8vw,3.85rem)] font-black leading-none text-foreground">
              {formatARS(data.total_valuation)}
            </h1>
            <div className="mt-2.5 flex flex-wrap gap-1.5">
              {live ? (
                <span className={`rounded-md border px-2 py-0.5 text-[10px] font-black ${liveTone(live.daily_pnl_total)}`}>
                  Día {signedMoney(live.daily_pnl_total)} · {formatPct(live.daily_pnl_pct)}
                </span>
              ) : null}
              <span className="rounded-md border border-sky-500/25 bg-sky-500/10 px-2 py-0.5 text-[10px] font-black text-sky-400">
                {freshness} · {data.live_market?.freshness_summary?.[freshness] ?? 0} instrumentos
              </span>
              <span className="rounded-md border border-amber-500/25 bg-amber-500/10 px-2 py-0.5 text-[10px] font-black text-amber-400">
                Último dato {live?.last_market_time ? formatPriceTime(live.last_market_time) : "-"}
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setIsEditing((value) => !value)}
            className="inline-flex h-9 items-center justify-center gap-2 rounded-md border border-border/60 bg-background/40 px-3 text-xs font-black text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary lg:mt-1"
            aria-pressed={isEditing}
            title="Configurar KPIs del dashboard"
          >
            <Settings2 className="size-3.5" />
            KPIs
          </button>
        </div>

        <div className="grid gap-2">
          {slots.map((slot, index) => {
            const kpi = kpiMap.get(slot) ?? kpis[0]
            return (
              <div
                key={`${index}-${slot}`}
                className="grid min-h-10 grid-cols-1 gap-1.5 rounded-lg border border-border/45 bg-background/35 px-3 py-1.5 sm:grid-cols-[160px_minmax(0,1fr)_auto] sm:items-center sm:gap-3"
              >
                <div className="text-[10px] font-black uppercase tracking-[0.12em] text-sky-200/80">
                  {kpi.label}
                </div>
                <div className={cn("min-w-0 truncate font-mono text-base font-black", kpiToneClass(kpi.tone))}>
                  {kpi.value}
                </div>
                <div className="min-w-0 truncate text-xs font-bold text-muted-foreground sm:text-right">
                  {kpi.subtext}
                </div>
                {isEditing ? (
                  <div className="sm:col-span-3">
                    <select
                      value={slot}
                      onChange={(event) => updateSlot(index, event.target.value as DashboardKpiId)}
                      className="h-8 w-full rounded-md border border-border/60 bg-background px-2 text-xs font-bold text-foreground outline-none focus:border-primary/60"
                      aria-label={`KPI slot ${index + 1}`}
                    >
                      {kpis.map((option) => (
                        <option key={option.id} value={option.id}>{option.label}</option>
                      ))}
                    </select>
                  </div>
                ) : null}
              </div>
            )
          })}
        </div>
      </div>
    </SectionPanel>
  )
}

// ── Reallocation Panel ────────────────────────────────────────────────────────

function ReallocationPanel() {
  const { data } = useReallocation()
  if (!data) return null

  const hasRotations = data.rotations.length > 0
  const hasCapital = data.releasable_capital > 0

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.5 }}
    >
      <SectionPanel>
        <SectionHeader title="Reasignación" subtitle="Capital liberable y rotaciones" />
        <div className="mt-4 space-y-3">
          {/* Releasable capital */}
          <div className="flex items-center gap-3 p-3 rounded-xl bg-muted/10 border border-border/30">
            <div className="size-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0">
              <DollarCircle className="size-4 text-primary" />
            </div>
            <div className="min-w-0">
              <p className="text-[9px] uppercase tracking-widest font-bold text-muted-foreground">Capital liberable</p>
              <p className={`text-sm font-mono font-bold ${hasCapital ? "text-primary" : "text-muted-foreground"}`}>
                {hasCapital ? formatARSCompact(data.releasable_capital) : "Sin ventas sugeridas"}
              </p>
            </div>
          </div>

          {/* Rotations */}
          {hasRotations ? (
            <div className="space-y-2">
              <p className="text-[9px] uppercase tracking-widest font-bold text-muted-foreground px-1">Rotaciones</p>
              {data.rotations.slice(0, 3).map((r, i) => (
                <div key={i} className="flex items-center gap-2 px-1">
                  <span className="text-[11px] font-bold text-rose-400 font-mono">{r.from_ticker}</span>
                  <ArrowRightLeft className="size-3 text-muted-foreground flex-shrink-0" />
                  <span className="text-[11px] font-bold text-emerald-400 font-mono truncate">{r.to}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center gap-2 px-1 text-muted-foreground/60">
              <ArrowRightLeft className="size-3.5 flex-shrink-0" />
              <span className="text-xs">Sin rotaciones sugeridas</span>
            </div>
          )}

          {/* Suggested action */}
          {data.suggested_action && (
            <div className="flex items-start gap-2 pt-1 border-t border-border/20">
              <Lightbulb className="size-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
              <p className="text-[11px] text-muted-foreground/80 leading-relaxed">{data.suggested_action}</p>
            </div>
          )}
        </div>
      </SectionPanel>
    </motion.div>
  )
}

function liveTone(value: number | null | undefined): string {
  if (value === null || value === undefined) return "border-border/40 bg-muted/10 text-muted-foreground"
  if (value > 0) return "border-emerald-500/20 bg-emerald-500/10 text-emerald-400"
  if (value < 0) return "border-rose-500/20 bg-rose-500/10 text-rose-400"
  return "border-border/40 bg-muted/10 text-muted-foreground"
}

function freshnessTone(freshness: string): string {
  if (freshness === "LIVE") return "text-emerald-400"
  if (freshness === "CACHE") return "text-sky-400"
  if (freshness === "STALE") return "text-amber-400"
  return "text-muted-foreground"
}

function LiveSessionPanel({ data }: { data: ConsolidatedPortfolio }) {
  const live = data.live_market
  if (!live) return null

  const heatmap = data.by_asset
    .slice()
    .sort((a, b) => Math.abs(b.day_change_pct ?? 0) - Math.abs(a.day_change_pct ?? 0))
    .slice(0, 12)

  const dominantFreshness = Object.entries(live.freshness_summary ?? {})
    .sort((a, b) => b[1] - a[1])[0]?.[0] ?? "UNAVAILABLE"

  return (
    <SectionPanel delay={0.2}>
      <SectionHeader title="Sesión Live" subtitle="Movimiento diario y frescura de mercado">
        <div className={`flex items-center gap-1.5 text-[10px] font-black tracking-widest ${freshnessTone(dominantFreshness)}`}>
          <Activity className="size-3.5" />
          {dominantFreshness}
        </div>
      </SectionHeader>

      <div className="grid gap-3 md:grid-cols-4">
        <div className={`rounded-xl border px-4 py-3 ${liveTone(live.daily_pnl_total)}`}>
          <p className="text-[9px] font-bold uppercase tracking-widest opacity-80">Impacto día</p>
          <p className="mt-1 font-mono text-lg font-black">{formatARS(live.daily_pnl_total)}</p>
          <p className="text-[11px] font-bold">{formatPct(live.daily_pnl_pct)}</p>
        </div>
        <div className="rounded-xl border border-border/40 bg-background/35 px-4 py-3">
          <p className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground">Balance</p>
          <div className="mt-2 flex items-center gap-3 text-xs font-black">
            <span className="text-emerald-400">{live.positive_count} +</span>
            <span className="text-rose-400">{live.negative_count} -</span>
            <span className="text-muted-foreground">{live.unavailable_count} s/d</span>
          </div>
        </div>
        <div className="rounded-xl border border-border/40 bg-background/35 px-4 py-3">
          <p className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground">Frescura</p>
          <div className="mt-2 flex flex-wrap gap-2 text-[10px] font-black">
            {Object.entries(live.freshness_summary ?? {}).map(([key, count]) => (
              <span key={key} className={freshnessTone(key)}>{key}:{count}</span>
            ))}
          </div>
        </div>
        <div className="rounded-xl border border-border/40 bg-background/35 px-4 py-3">
          <p className="text-[9px] font-bold uppercase tracking-widest text-muted-foreground">Último dato</p>
          <div className="mt-2 flex items-center gap-2 text-xs font-bold text-foreground">
            <Clock className="size-3.5 text-muted-foreground" />
            {live.last_market_time ? formatPriceTime(live.last_market_time) : "-"}
          </div>
        </div>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
        {heatmap.map((asset) => (
          <div key={asset.ticker} className={`rounded-lg border px-3 py-2 ${liveTone(asset.day_change_pct)}`}>
            <div className="flex items-center justify-between gap-2">
              <span className="truncate text-xs font-black">{asset.ticker}</span>
              <span className="font-mono text-[11px] font-black">{asset.day_change_pct == null ? "-" : formatPct(asset.day_change_pct)}</span>
            </div>
            <p className="mt-1 truncate font-mono text-[10px] opacity-80">
              {asset.day_impact == null ? "sin dato diario" : formatARS(asset.day_impact)}
            </p>
          </div>
        ))}
      </div>
    </SectionPanel>
  )
}

export function DashboardView() {
  const { data, loading, error, refetch } = usePortfolioSummary()

  if (loading && !data) return <LoadingState />
  if (error) return <ErrorState error={error} refetch={refetch} />
  if (!data) return null

  const allocationData = data.by_asset.map(a => ({
    name: a.ticker,
    value: a.pct
  }))

  const sourceData = data.by_source.map(s => ({
    name: s.source,
    value: s.valuation
  }))

  const currencyData = data.by_currency.map(c => ({
    name: c.currency,
    value: c.valuation
  }))

  return (
    <div className="flex flex-col gap-6 animate-fade-up">
      <CapitalOverviewPanel data={data} />

      {/* Intelligence Status Banner */}
      <IntelligenceBanner />

      <LiveSessionPanel data={data} />

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Valuation by Asset Bar Chart */}
          <SectionPanel className="h-[400px]">
            <GlowOrb className="w-64 h-64 -top-32 -left-32 bg-primary/5" />
            <SectionHeader title="Valuación por Instrumento" subtitle="Top activos por peso en cartera" />
            {data.by_asset.length === 0 ? (
              <div className="h-[280px] flex flex-col items-center justify-center gap-3 text-center">
                <BarChart2 className="size-10 text-muted-foreground/20" />
                <p className="text-sm font-medium text-muted-foreground">Sin instrumentos cargados</p>
                <p className="text-xs text-muted-foreground/60">Importá un CSV o cargá posiciones manualmente para ver la distribución.</p>
              </div>
            ) : (
              <div className="h-[280px] mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.by_asset.slice(0, 8)} layout="vertical" margin={{ left: 40, right: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="oklch(0.24 0.01 260)" />
                    <XAxis type="number" hide />
                    <YAxis
                      dataKey="ticker"
                      type="category"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fontSize: 11, fontWeight: 700, fill: "oklch(0.58 0.015 260)" }}
                    />
                    <Tooltip
                      cursor={{ fill: 'oklch(0.20 0.012 260 / 0.4)' }}
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="surface-elevated p-3 rounded-xl border border-border/50 shadow-xl">
                              <p className="text-xs font-bold text-foreground mb-1">{payload[0].payload.ticker}</p>
                              <p className="text-sm font-mono text-primary font-bold">{formatARS(payload[0].value as number)}</p>
                            </div>
                          )
                        }
                        return null
                      }}
                    />
                    <Bar dataKey="valuation" fill="var(--primary)" radius={[0, 4, 4, 0]} barSize={24}>
                      {data.by_asset.map((entry, index) => (
                        <Cell key={`cell-${index}`} fillOpacity={1 - (index * 0.1)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </SectionPanel>

          {/* Source/Broker Breakdown */}
          <SectionPanel>
            <SectionHeader title="Capital por Fuente" subtitle="Consolidación multibróker" />
            {data.by_source.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 gap-3 text-center">
                <PieChart className="size-10 text-muted-foreground/20" />
                <p className="text-sm font-medium text-muted-foreground">Sin fuentes vinculadas</p>
                <p className="text-xs text-muted-foreground/60">Vinculá un bróker o importá datos para ver la distribución por fuente.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {data.by_source.map((source, i) => (
                  <div key={i} className="flex items-center gap-4">
                    <div className="size-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20">
                      <Building2 className="size-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-sm text-foreground">{source.source}</span>
                        <span className="font-mono text-sm font-bold">{formatARS(source.valuation)}</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-muted/30 overflow-hidden text-[0px]">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${source.pct}%` }}
                          transition={{ duration: 1, delay: 0.5 + (i * 0.1) }}
                          className="h-full bg-primary rounded-full shadow-[0_0_10px_rgba(var(--primary),0.3)]"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </SectionPanel>

          {/* Currency Exposure */}
          <SectionPanel>
            <SectionHeader title="Exposición por Moneda" subtitle="Distribución ARS vs USD" />
            <div className="mt-4 space-y-6">
                <div className="flex items-center justify-between">
                    <div className="flex flex-col">
                        <span className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground">Pesos (ARS)</span>
                        <span className="text-lg font-mono font-bold text-foreground">
                            {formatPctAlloc(data.by_currency.find(c => c.currency === "ARS")?.pct || 0)}
                        </span>
                    </div>
                    <div className="flex flex-col text-right">
                        <span className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground">Dólares (USD)</span>
                        <span className="text-lg font-mono font-bold text-primary">
                            {formatPctAlloc(data.by_currency.find(c => c.currency === "USD")?.pct || 0)}
                        </span>
                    </div>
                </div>

                <div className="relative h-4 w-full rounded-full bg-muted/30 overflow-hidden flex border border-border/20 p-0.5">
                    <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${data.by_currency.find(c => c.currency === "ARS")?.pct || 0}%` }}
                        transition={{ duration: 1.2, ease: "easeOut" }}
                        className="h-full bg-muted-foreground/30 rounded-l-full"
                    />
                    <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${data.by_currency.find(c => c.currency === "USD")?.pct || 0}%` }}
                        transition={{ duration: 1.2, ease: "easeOut", delay: 0.2 }}
                        className="h-full bg-primary rounded-r-full shadow-[0_0_15px_rgba(var(--primary),0.4)]"
                    />
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="p-3 rounded-2xl bg-muted/10 border border-border/40 flex flex-col gap-1">
                        <span className="text-[9px] uppercase font-bold text-muted-foreground tracking-wider">Total en Pesos</span>
                        <span className="text-xs font-mono font-bold">{formatARS(data.by_currency.find(c => c.currency === "ARS")?.valuation || 0)}</span>
                    </div>
                    <div className="p-3 rounded-2xl bg-primary/5 border border-primary/20 flex flex-col gap-1">
                        <span className="text-[9px] uppercase font-bold text-primary tracking-wider">Total en Dólares</span>
                        <span className="text-xs font-mono font-bold text-primary">{formatARS(data.by_currency.find(c => c.currency === "USD")?.valuation || 0)}</span>
                    </div>
                </div>
            </div>
          </SectionPanel>
        </div>

        <div className="space-y-6">
          <AllocationDonut data={allocationData} />
          <MarketWidget />
          <ReallocationPanel />
        </div>
      </div>
    </div>
  )
}
