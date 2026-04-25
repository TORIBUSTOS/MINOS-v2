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
import { SectionPanel, SectionHeader, GlowOrb, LoadingState, ErrorState } from "@/components/dashboard/dashboard-ui"
import { usePortfolioSummary, usePositions } from "@/hooks/use-minos"
import { formatARS, formatPctAlloc } from "@/lib/minos-formatters"
import { Button } from "@/components/ui/button"
import { motion } from "motion/react"

export default function SourcesPage() {
  const { data: summary, loading: summaryLoading, error: summaryError, refetch: refetchSummary } = usePortfolioSummary()
  const { data: positions, loading: posLoading, error: posError, refetch: refetchPositions } = usePositions()

  const loading = summaryLoading || posLoading
  const error = summaryError || posError

  if (loading && !summary) return <LoadingState />
  if (error) return <ErrorState error={error} refetch={() => { refetchSummary(); refetchPositions(); }} />
  if (!summary || !positions) return null

  const sourcesWithPositions = summary.by_source.map(sourceInfo => ({
    ...sourceInfo,
    instruments: positions.filter(p => p.source === sourceInfo.source)
  }))

  return (
    <div className="flex flex-col gap-6 animate-fade-up">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground font-display">Fuentes de Capital</h1>
          <p className="text-muted-foreground text-sm font-medium">Consolidación de activos por bróker y entidad financiera.</p>
        </div>
        <Button variant="default" size="sm" className="rounded-xl h-9 font-bold shadow-lg shadow-primary/20 gap-2">
          <Plus className="size-3.5" />
          Vincular Fuente
        </Button>
      </div>

      {sourcesWithPositions.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 gap-4 text-center rounded-2xl border border-dashed border-border/40 bg-muted/5">
          <div className="size-14 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/20">
            <Building2 className="size-7 text-primary/60" />
          </div>
          <div>
            <p className="text-base font-bold text-foreground">Sin fuentes vinculadas</p>
            <p className="text-sm text-muted-foreground mt-1 max-w-xs">
              Vinculá un bróker o importá un archivo CSV para ver tus fuentes de capital aquí.
            </p>
          </div>
          <Button variant="default" size="sm" className="rounded-xl h-9 font-bold shadow-lg shadow-primary/20 gap-2 mt-2">
            <Plus className="size-3.5" />
            Vincular primera fuente
          </Button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sourcesWithPositions.map((source, idx) => (
          <motion.div
            key={source.source}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: idx * 0.1 }}
          >
            <SectionPanel className="h-full flex flex-col group hover:border-primary/20 transition-all">
              <GlowOrb className="w-32 h-32 -top-16 -right-16 bg-primary/5" />
              
              <div className="flex items-center gap-4 mb-6">
                <div className="size-12 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/20 shadow-inner group-hover:scale-110 transition-transform">
                  <Building2 className="size-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-foreground font-display">{source.source}</h3>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase tracking-wider font-bold text-muted-foreground/60">Balance:</span>
                    <span className="text-sm font-mono font-bold text-primary">{formatARS(source.valuation)}</span>
                  </div>
                </div>
                <div className="text-right">
                    <span className="text-xs font-bold text-muted-foreground bg-muted/30 px-2 py-0.5 rounded-full border border-border/40">
                        {formatPctAlloc(source.pct)}
                    </span>
                </div>
              </div>

              <div className="flex-1 space-y-3">
                <p className="text-[10px] uppercase tracking-[0.1em] font-bold text-muted-foreground/50 border-b border-border/20 pb-2">Instrumentos vinculados</p>
                {source.instruments.map((inst, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded-lg hover:bg-muted/30 transition-colors group/item">
                    <div className="flex items-center gap-3">
                      <div className="size-8 rounded-lg bg-surface-elevated border border-border/40 flex items-center justify-center font-bold text-[10px]">
                        {inst.ticker.substring(0, 3)}
                      </div>
                      <span className="text-xs font-bold text-foreground group-hover/item:text-primary transition-colors">{inst.ticker}</span>
                    </div>
                    <div className="text-right">
                        <p className="text-xs font-mono font-bold">{formatARS(inst.valuation_ars)}</p>
                        <p className="text-[9px] text-muted-foreground font-medium">{formatPctAlloc(inst.pct)} del bróker</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 pt-4 border-t border-border/20 flex items-center justify-between">
                <Button variant="ghost" size="sm" className="h-8 px-2 text-[11px] font-bold text-muted-foreground hover:text-foreground">
                    <History className="size-3.5 mr-1.5" />
                    Historial
                </Button>
                <Button variant="ghost" size="sm" className="h-8 px-3 text-[11px] font-bold text-primary hover:bg-primary/10 rounded-lg group/btn">
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
