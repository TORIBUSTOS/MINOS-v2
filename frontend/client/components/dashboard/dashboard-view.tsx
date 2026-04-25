"use client"

import React from "react"
import { motion } from "motion/react"
import {
  DollarSign,
  Building2,
  Globe,
  LayoutGrid,
  BarChart2,
  PieChart
} from "lucide-react"
import {
  KpiCard,
  SectionPanel,
  SectionHeader,
  GlowOrb,
  LoadingState,
  ErrorState
} from "./dashboard-ui"
import { AllocationDonut } from "./allocation-donut"
import { MarketWidget } from "./market-widget"
import { usePortfolioSummary } from "@/hooks/use-minos"
import { formatARS, formatARSCompact, formatPctAlloc } from "@/lib/minos-formatters"
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
      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Patrimonio Total"
          value={formatARSCompact(data.total_valuation)}
          delay={0}
          icon={DollarSign}
        />
        <KpiCard 
          label="Instrumentos" 
          value={data.by_asset.length.toString()} 
          delay={0.1} 
          icon={LayoutGrid} 
          subtext="activos en cartera"
        />
        <KpiCard 
          label="Fuentes" 
          value={data.by_source.length.toString()} 
          delay={0.2} 
          icon={Building2} 
          subtext="brokers conectados"
        />
        <KpiCard 
          label="Exposición USD" 
          value={formatPctAlloc(data.by_currency.find(c => c.currency === "USD")?.pct || 0)} 
          delay={0.3} 
          icon={Globe} 
          subtext="del total invertido"
        />
      </div>

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
        </div>
      </div>
    </div>
  )
}
