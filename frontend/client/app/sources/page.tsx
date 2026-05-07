"use client"

import React from "react"
import { 
  Building2, 
  ChevronRight, 
  TrendingUp, 
  Plus,
  ArrowRight,
  ShieldCheck,
  ExternalLink,
  Wallet
} from "lucide-react"
import { EmptyState, ErrorState, GlowOrb, LoadingState, PageHeader, SectionPanel } from "@/components/dashboard/dashboard-ui"
import { usePortfolioSummary, usePositions, usePortfolios } from "@/hooks/use-minos"
import { formatARS, formatPctAlloc } from "@/lib/minos-formatters"
import { Button } from "@/components/ui/button"
import { motion } from "motion/react"
import { useRouter } from "next/navigation"

export default function SourcesPage() {
  const router = useRouter()
  const { data: summary, loading: summaryLoading, error: summaryError, refetch: refetchSummary } = usePortfolioSummary()
  const { data: positions, loading: posLoading, error: posError, refetch: refetchPositions } = usePositions()
  const { data: portfolios } = usePortfolios()

  const loading = summaryLoading || posLoading
  const error = summaryError || posError

  if (loading && !summary) return <LoadingState />
  if (error) return <ErrorState error={error} refetch={() => { refetchSummary(); refetchPositions(); }} />
  if (!summary || !positions) return null

  // Map portfolio_id → source_name
  const portfolioSourceMap = (portfolios ?? []).reduce<Record<number, string>>(
    (map, p) => { map[p.id] = p.source_name ?? ""; return map },
    {}
  )

  const sourcesWithPositions = summary.by_source.map(sourceInfo => {
    const sourcePositions = positions.filter(
      p => portfolioSourceMap[p.portfolio_id] === sourceInfo.source
    )
    return {
      ...sourceInfo,
      instruments: sourcePositions.map(p => ({
        ticker: p.ticker,
        valuation_ars: p.valuation,
        pct: sourceInfo.valuation > 0 ? (p.valuation / sourceInfo.valuation * 100) : 0,
      })),
    }
  })

  return (
    <div className="flex flex-col gap-6 animate-fade-up">
      <PageHeader
        title="Fuentes de Capital"
        subtitle="Consolidación de activos por bróker y entidad financiera."
        actions={
        <Button
          variant="default"
          size="sm"
          className="h-10 w-full rounded-xl font-bold shadow-lg shadow-primary/20 gap-2 sm:w-auto"
          onClick={() => router.push("/manual-entry")}
        >
          <Plus className="size-3.5" />
          Vincular Fuente
        </Button>
        }
      />

      {sourcesWithPositions.length === 0 && (
        <EmptyState
          icon={Building2}
          title="Sin fuentes vinculadas"
          description="Vinculá un bróker o importá un archivo para ver tus fuentes de capital aquí."
          action={
          <Button
            variant="default"
            size="sm"
            className="rounded-xl h-9 font-bold shadow-lg shadow-primary/20 gap-2 mt-2"
            onClick={() => router.push("/manual-entry")}
          >
            <Plus className="size-3.5" />
            Vincular primera fuente
          </Button>
          }
        />
      )}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        {sourcesWithPositions.map((source, idx) => (
          <motion.div
            key={source.source}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: idx * 0.1 }}
          >
            <SectionPanel className="h-full flex flex-col group hover:border-primary/20 transition-all">
              <GlowOrb className="w-32 h-32 -top-16 -right-16 bg-primary/5" />
              
              <div className="mb-6 flex items-start gap-4">
                <div className="size-12 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/20 shadow-inner group-hover:scale-110 transition-transform">
                  <Building2 className="size-6 text-primary" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="text-lg font-bold text-foreground font-display">{source.source}</h3>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground/60">Balance:</span>
                    <span className="text-sm font-mono font-bold text-primary">{formatARS(source.valuation)}</span>
                  </div>
                </div>
                <div className="shrink-0 text-right">
                    <span className="text-xs font-bold text-muted-foreground bg-muted/30 px-2 py-0.5 rounded-full border border-border/40">
                        {formatPctAlloc(source.pct)}
                    </span>
                </div>
              </div>

              <div className="flex-1 space-y-3">
                <p className="text-[10px] uppercase tracking-[0.1em] font-bold text-muted-foreground/50 border-b border-border/20 pb-2">Instrumentos vinculados</p>
                {source.instruments.map((inst, i) => (
                  <div key={i} className="flex items-center justify-between gap-3 rounded-lg p-2 transition-colors hover:bg-muted/30 group/item">
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="size-8 rounded-lg bg-surface-elevated border border-border/40 flex items-center justify-center font-bold text-[10px]">
                        {inst.ticker.substring(0, 3)}
                      </div>
                      <span className="truncate text-xs font-bold text-foreground transition-colors group-hover/item:text-primary">{inst.ticker}</span>
                    </div>
                    <div className="shrink-0 text-right">
                        <p className="text-xs font-mono font-bold">{formatARS(inst.valuation_ars)}</p>
                        <p className="text-[9px] text-muted-foreground font-medium">{formatPctAlloc(inst.pct)} del bróker</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-4 border-t border-border/20 flex items-center justify-between">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-2 text-[11px] font-bold text-muted-foreground hover:text-foreground"
                  disabled
                  title="Historial de cargas pendiente de endpoint dedicado"
                >
                    <History className="size-3.5 mr-1.5" />
                    Historial
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 px-3 text-[11px] font-bold text-primary hover:bg-primary/10 rounded-lg group/btn"
                  onClick={() => router.push(`/instruments?q=${encodeURIComponent(source.source)}`)}
                >
                    Gestionar Posiciones
                    <ArrowRight className="size-3.5 ml-1.5 group-hover/btn:translate-x-1 transition-transform" />
                </Button>
              </div>
            </SectionPanel>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

function History({ className }: { className?: string }) {
    return (
        <svg 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            className={className}
        >
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
            <path d="M12 7v5l4 2" />
        </svg>
    )
}
