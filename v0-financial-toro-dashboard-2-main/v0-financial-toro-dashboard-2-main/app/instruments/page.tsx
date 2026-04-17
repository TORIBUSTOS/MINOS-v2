"use client"

import React from "react"
import { 
  Search, 
  Filter, 
  Download, 
  RefreshCw,
  ArrowUpRight,
  TrendingUp,
  TrendingDown,
  Building2,
  Wallet
} from "lucide-react"
import { SectionPanel, SectionHeader, GlowOrb, LoadingState, ErrorState } from "@/components/dashboard/dashboard-ui"
import { usePositions } from "@/hooks/use-minos"
import { formatARS, formatPctAlloc, assetColor, getAssetCategory } from "@/lib/minos-formatters"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

export default function InstrumentsPage() {
  const { data, loading, error, refetch } = usePositions()
  const [search, setSearch] = React.useState("")

  if (loading && !data) return <LoadingState />
  if (error) return <ErrorState error={error} refetch={refetch} />
  if (!data) return null

  const filteredData = data.filter(p => 
    p.ticker.toLowerCase().includes(search.toLowerCase()) || 
    p.source.toLowerCase().includes(search.toLowerCase())
  )

  // Group by category
  const groupedData = filteredData.reduce((acc, pos) => {
    const cat = getAssetCategory(pos.ticker);
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(pos);
    return acc;
  }, {} as Record<string, typeof data>)

  const categoriesOrder = ["Acciones", "Bonos", "Cedears", "Fondos", "Otros"];

  return (
    <div className="flex flex-col gap-6 animate-fade-up">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground font-display">Mis Instrumentos</h1>
          <p className="text-muted-foreground text-sm font-medium">Glosa detallada de posiciones agrupadas por tipo de activo.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="rounded-xl h-9 font-bold bg-muted/10 border-border/50 hover:bg-primary/5 hover:text-primary transition-all gap-2">
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
              placeholder="Buscar por ticker o bróker..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 rounded-xl border-border/50 bg-muted/10 focus:ring-primary/20 transition-all h-10 text-sm"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="rounded-xl h-9 border-border/50 bg-muted/10 text-muted-foreground hover:text-foreground">
              <Filter className="size-3.5 mr-2" />
              Filtros
            </Button>
          </div>
        </div>

        <div className="rounded-xl border border-border/40 overflow-hidden bg-surface-elevated/30 backdrop-blur-sm">
          <Table>
            <TableHeader className="bg-muted/30">
              <TableRow className="hover:bg-transparent border-border/40">
                <TableHead className="w-[180px] text-[10px] uppercase tracking-widest font-bold">Instrumento</TableHead>
                <TableHead className="text-[10px] uppercase tracking-widest font-bold">Bróker / Fuente</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">Valuación (ARS)</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">Peso (%)</TableHead>
                <TableHead className="text-right text-[10px] uppercase tracking-widest font-bold">Acción</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-48 text-center">
                    <div className="flex flex-col items-center justify-center text-muted-foreground gap-2">
                        <Wallet className="size-8 opacity-20" />
                        <p className="text-sm font-medium">No se encontraron instrumentos.</p>
                    </div>
                  </TableCell>
                </TableRow>
              ) : (
                categoriesOrder.map(category => {
                  const positions = groupedData[category] || [];
                  if (positions.length === 0) return null;

                  return (
                    <React.Fragment key={category}>
                      {/* Category Header Row */}
                      <TableRow className="bg-muted/10 hover:bg-muted/10 border-border/40">
                        <TableCell colSpan={5} className="py-2 px-4">
                          <div className="flex items-center gap-2">
                            <div 
                              className="size-1.5 rounded-full shadow-[0_0_8px_currentColor]" 
                              style={{ color: assetColor(category), backgroundColor: "currentColor" }} 
                            />
                            <span className="text-[10px] uppercase tracking-[0.2em] font-black text-foreground/70">
                              {category}
                            </span>
                            <Badge variant="outline" className="ml-2 text-[9px] font-bold bg-muted/20 border-border/20 py-0 h-4">
                              {positions.length}
                            </Badge>
                          </div>
                        </TableCell>
                      </TableRow>
                      
                      {/* Positions for this category */}
                      {positions.map((pos, i) => (
                        <TableRow key={`${category}-${i}`} className="group hover:bg-muted/20 border-border/40 transition-colors">
                          <TableCell className="font-medium">
                            <div className="flex items-center gap-3">
                              <div 
                                className="size-9 rounded-lg bg-surface-elevated border border-border/40 flex items-center justify-center font-bold text-xs group-hover:bg-primary/5 transition-colors"
                                style={{ borderLeft: `3px solid ${assetColor(category)}` }}
                              >
                                {pos.ticker.substring(0, 4)}
                              </div>
                              <div className="flex flex-col">
                                <span className="font-display font-bold text-sm tracking-tight group-hover:text-primary transition-colors">{pos.ticker}</span>
                                <span className="text-[10px] text-muted-foreground font-medium">{pos.portfolio}</span>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2 text-muted-foreground group-hover:text-foreground transition-colors">
                              <Building2 className="size-3.5" />
                              <span className="text-xs font-semibold">{pos.source}</span>
                            </div>
                          </TableCell>
                          <TableCell className="text-right">
                            <span className="font-mono font-bold text-sm text-foreground">{formatARS(pos.valuation_ars)}</span>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-2">
                              <div className="w-12 h-1 rounded-full bg-muted/40 overflow-hidden hidden md:block">
                                  <div 
                                    className="h-full" 
                                    style={{ width: `${pos.pct}%`, backgroundColor: assetColor(category) }} 
                                  />
                              </div>
                              <span className="font-mono text-[11px] font-bold text-muted-foreground">{formatPctAlloc(pos.pct)}</span>
                            </div>
                          </TableCell>
                          <TableCell className="text-right">
                            <Button variant="ghost" size="icon" className="size-8 rounded-lg hover:bg-primary/10 hover:text-primary group/btn transition-all">
                              <ArrowUpRight className="size-4 group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
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
