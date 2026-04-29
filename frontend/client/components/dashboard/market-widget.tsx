"use client"

import React from "react"
import { motion } from "motion/react"
import { TrendingUp, RefreshCw, Loader2 } from "lucide-react"
import { SectionPanel, SectionHeader, GlowOrb } from "./dashboard-ui"
import { triggerMinosRefresh, useMarketPrices, useRefreshPrices } from "@/hooks/use-minos"
import { formatARS, formatRelativeTime } from "@/lib/minos-formatters"
import { Button } from "@/components/ui/button"

export function MarketWidget() {
  const { data: marketData, loading, refetch } = useMarketPrices()
  const { refresh: triggerRefresh, loading: refreshing } = useRefreshPrices()

  const handleRefresh = async () => {
    await triggerRefresh()
    refetch()
    triggerMinosRefresh()
  }

  const prices = marketData?.prices ? Object.entries(marketData.prices) : []

  return (
    <SectionPanel className="flex flex-col h-full">
      <GlowOrb className="w-24 h-24 -top-12 -left-12 bg-chart-3/10" />
      <SectionHeader title="Mercado en Vivo" subtitle="Precios sugeridos y cotizaciones">
        <Button 
          variant="ghost" 
          size="icon" 
          className="size-7 rounded-lg hover:bg-primary/10 hover:text-primary transition-all"
          onClick={handleRefresh}
          disabled={loading || refreshing}
        >
          <RefreshCw className={`size-3.5 ${(loading || refreshing) ? "animate-spin" : ""}`} />
        </Button>
      </SectionHeader>

      <div className="flex-1 overflow-y-auto pr-1 scrollbar-none">
        {loading && !marketData ? (
          <div className="flex flex-col items-center justify-center py-12 gap-3">
            <Loader2 className="size-6 text-muted-foreground/30 animate-spin" />
            <p className="text-[10px] uppercase tracking-widest text-muted-foreground/50 font-bold">Consultando tickers...</p>
          </div>
        ) : prices.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-xs text-muted-foreground">No hay datos de mercado disponibles.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {prices.map(([ticker, info], i) => (
              <motion.div
                key={ticker}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: i * 0.05 }}
                className="flex items-center justify-between p-3 rounded-xl bg-muted/20 hover:bg-muted/40 border border-transparent hover:border-border/50 transition-all group"
              >
                <div className="flex items-center gap-3">
                  <div className="size-9 rounded-lg bg-surface-elevated flex items-center justify-center border border-border/40 shadow-sm font-bold text-xs group-hover:bg-primary/5 group-hover:text-primary transition-colors">
                    {ticker.substring(0, 4)}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-foreground font-display group-hover:text-primary transition-colors">{ticker}</h4>
                    <p className="text-[10px] text-muted-foreground font-medium">{formatRelativeTime(info.fetched_at)}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs font-bold text-foreground font-mono">
                    {formatARS(info.price)}
                  </p>
                  <div className="flex items-center justify-end gap-1 mt-0.5">
                    {info.expired ? (
                        <span className="text-[9px] font-bold text-amber-500/70 uppercase">Expirado</span>
                    ) : (
                        <span className="text-[9px] font-bold text-fin-gain/70 uppercase">Actual</span>
                    )}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-border/30">
        <Button
          variant="outline"
          className="w-full h-9 rounded-xl text-xs font-bold gap-2 bg-muted/10 hover:bg-primary/5 hover:text-primary hover:border-primary/20 transition-all"
          disabled={prices.length === 0}
          title={prices.length === 0 ? "Cargá posiciones para habilitar el monitor de mercado" : "Monitor completo pendiente de ruta dedicada"}
        >
          <TrendingUp className="size-3.5" />
          Ver Monitor Completo
        </Button>
      </div>
    </SectionPanel>
  )
}
