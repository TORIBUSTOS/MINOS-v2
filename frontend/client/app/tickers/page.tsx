"use client"

import React from "react"
import { 
  TrendingUp, 
  Search, 
  ArrowUpRight, 
  Layers, 
  Target,
  Activity,
  ChevronDown,
  ChevronRight,
  TrendingDown,
  Dot
} from "lucide-react"
import { SectionPanel, SectionHeader, GlowOrb, LoadingState, ErrorState } from "@/components/dashboard/dashboard-ui"
import { useUnifiedTickers } from "@/hooks/use-minos"
import { formatARS, formatPctAlloc, assetColor, getAssetCategory } from "@/lib/minos-formatters"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { motion, AnimatePresence } from "framer-motion"

// ── Signal Helper (Mock for now) ──────────────────────────────────────────────

type Signal = "BUY" | "HOLD" | "SELL" | "NEUTRAL"

function getTickerSignal(ticker: string): Signal {
  const hash = ticker.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0)
  const signals: Signal[] = ["BUY", "HOLD", "SELL", "NEUTRAL"]
  return signals[hash % signals.length]
}

function SignalBadge({ signal }: { signal: Signal }) {
  const styles = {
    BUY: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    HOLD: "bg-amber-500/10 text-amber-500 border-amber-500/20",
    SELL: "bg-rose-500/10 text-rose-500 border-rose-500/20",
    NEUTRAL: "bg-muted/10 text-muted-foreground border-border/20",
  }
  
  return (
    <Badge variant="outline" className={`${styles[signal]} text-[10px] font-black tracking-wider py-0 px-2 h-5`}>
      {signal}
    </Badge>
  )
}

// ── Main Page Component ────────────────────────────────────────────────────────

export default function TickersPage() {
  const { data, loading, error, refetch } = useUnifiedTickers()
  const [search, setSearch] = React.useState("")
  const [expandedTickers, setExpandedTickers] = React.useState<Record<string, boolean>>({})

  if (loading && !data) return <LoadingState />
  if (error) return <ErrorState error={error} refetch={refetch} />
  if (!data) return null

  const toggleExpand = (ticker: string) => {
    setExpandedTickers(prev => ({ ...prev, [ticker]: !prev[ticker] }))
  }

  const filteredData = data.filter(t => 
    t.ticker.toLowerCase().includes(search.toLowerCase())
  ).sort((a, b) => b.presence - a.presence)

  return (
    <div className="flex flex-col gap-6 animate-fade-up">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground font-display">Tickers Unificados</h1>
          <p className="text-muted-foreground text-sm font-medium">Consolidación cross-portfolio y señales de mercado.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input 
              placeholder="Buscar ticker..." 
              className="pl-9 bg-surface-elevated border-border/40 focus:ring-primary/20"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={refetch} className="hover:bg-primary/5">
                  <Activity className="size-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">Actualizar señales</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Stats Summary Cards */}
        <SectionPanel className="lg:col-span-1 p-5 flex flex-col justify-between items-start gap-4 group">
            <div className="flex items-center gap-3">
                <div className="size-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                    <Target className="size-5" />
                </div>
                <div>
                    <p className="text-[10px] uppercase tracking-widest font-black text-muted-foreground">Total Unificados</p>
                    <p className="text-2xl font-display font-bold leading-none">{data.length}</p>
                </div>
            </div>
            <GlowOrb color="hsl(var(--primary))" className="opacity-10" />
        </SectionPanel>

        <SectionPanel className="lg:col-span-1 p-5 flex flex-col justify-between items-start gap-4 group">
            <div className="flex items-center gap-3">
                <div className="size-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-500 group-hover:scale-110 transition-transform">
                    <TrendingUp className="size-5" />
                </div>
                <div>
                    <p className="text-[10px] uppercase tracking-widest font-black text-muted-foreground">Más Frecuente</p>
                    <p className="text-2xl font-display font-bold leading-none">
                        {data.sort((a,b) => b.presence - a.presence)[0]?.ticker || "Sin datos"}
                    </p>
                </div>
            </div>
            <GlowOrb color="#10b981" className="opacity-10" />
        </SectionPanel>

        <SectionPanel className="lg:col-span-2 p-5 flex items-center justify-between">
            <div className="flex flex-col gap-1">
                <p className="text-[10px] uppercase tracking-widest font-black text-muted-foreground">Estado Semáforo</p>
                <div className="flex items-center gap-4 mt-1">
                    <div className="flex items-center gap-1.5">
                        <div className="size-2 rounded-full bg-emerald-500" />
                        <span className="text-xs font-bold">Compra</span>
                    </div>
                     <div className="flex items-center gap-1.5">
                        <div className="size-2 rounded-full bg-amber-500" />
                        <span className="text-xs font-bold">Mantener</span>
                    </div>
                     <div className="flex items-center gap-1.5">
                        <div className="size-2 rounded-full bg-rose-500" />
                        <span className="text-xs font-bold">Venta</span>
                    </div>
                </div>
            </div>
            <Layers className="size-8 text-muted-foreground/20" />
        </SectionPanel>
      </div>

      <SectionPanel>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-border/40">
                <TableHead className="w-[40px]"></TableHead>
                <TableHead className="w-[200px] text-[10px] uppercase tracking-widest font-black">Ticker</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-black">Carteras</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-black">Valuación Total</TableHead>
                <TableHead className="w-[120px] text-center text-[10px] uppercase tracking-widest font-black">Señal</TableHead>
                <TableHead className="w-[100px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-32 text-center text-muted-foreground font-medium">
                    No se encontraron tickers unificados.
                  </TableCell>
                </TableRow>
              ) : (
                filteredData.map((ticker) => {
                  const category = getAssetCategory(ticker.ticker)
                  const totalValuation = ticker.entries.reduce((sum, e) => sum + e.valuation, 0)
                  const isExpanded = expandedTickers[ticker.ticker]

                  return (
                    <React.Fragment key={ticker.ticker}>
                      <TableRow className={`group border-border/40 transition-colors ${isExpanded ? 'bg-muted/10' : 'hover:bg-muted/20'}`}>
                        <TableCell>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="size-6 rounded-md hover:bg-primary/20"
                            onClick={() => toggleExpand(ticker.ticker)}
                          >
                            {isExpanded ? <ChevronDown className="size-4" /> : <ChevronRight className="size-4" />}
                          </Button>
                        </TableCell>
                        <TableCell>
                           <div className="flex items-center gap-3">
                              <div 
                                className="size-8 rounded-lg bg-surface-elevated border border-border/40 flex items-center justify-center font-bold text-[10px]"
                                style={{ borderLeft: `3px solid ${assetColor(category)}` }}
                              >
                                {ticker.ticker.substring(0, 4)}
                              </div>
                              <div className="flex flex-col leading-none">
                                <span className="font-display font-bold text-sm tracking-tight">{ticker.ticker}</span>
                                <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-wider">{category}</span>
                              </div>
                            </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-2">
                             <Badge variant="secondary" className="bg-muted/50 border-border/20 text-[10px] h-5 py-0 px-2 font-black">
                                {ticker.presence} {ticker.presence === 1 ? 'Cartera' : 'Carteras'}
                             </Badge>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                           <span className="font-mono font-bold text-sm text-foreground">{formatARS(totalValuation)}</span>
                        </TableCell>
                        <TableCell className="text-center">
                          <SignalBadge signal={getTickerSignal(ticker.ticker)} />
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="icon" className="size-8 rounded-lg hover:bg-primary/10 hover:text-primary group/btn">
                            <ArrowUpRight className="size-4 group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                          </Button>
                        </TableCell>
                      </TableRow>
                      
                      {/* Expanded Section */}
                      <AnimatePresence>
                        {isExpanded && (
                          <TableRow className="border-border/40 bg-muted/5 hover:bg-muted/5">
                            <TableCell colSpan={6} className="p-0">
                               <motion.div 
                                 initial={{ height: 0, opacity: 0 }}
                                 animate={{ height: "auto", opacity: 1 }}
                                 exit={{ height: 0, opacity: 0 }}
                                 className="overflow-hidden"
                               >
                                 <div className="p-4 pl-14">
                                   <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                     {ticker.entries.map((entry, idx) => (
                                       <div key={idx} className="bg-surface-elevated/50 border border-border/20 rounded-xl p-3 flex flex-col gap-2">
                                          <div className="flex items-center justify-between">
                                            <span className="text-[10px] font-black uppercase text-muted-foreground tracking-wider">{entry.portfolio}</span>
                                            <Badge variant="outline" className="text-[9px] h-4 py-0 border-primary/20 text-primary">Detalle</Badge>
                                          </div>
                                          <div className="flex justify-between items-end">
                                             <div>
                                               <p className="text-[10px] text-muted-foreground font-medium">Cantidad</p>
                                               <p className="font-mono text-xs font-bold">{entry.quantity.toLocaleString()}</p>
                                             </div>
                                             <div className="text-right">
                                               <p className="text-[10px] text-muted-foreground font-medium">Valuación</p>
                                               <p className="font-mono text-sm font-bold text-foreground">{formatARS(entry.valuation)}</p>
                                             </div>
                                          </div>
                                       </div>
                                     ))}
                                   </div>
                                 </div>
                               </motion.div>
                            </TableCell>
                          </TableRow>
                        )}
                      </AnimatePresence>
                    </React.Fragment>
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
