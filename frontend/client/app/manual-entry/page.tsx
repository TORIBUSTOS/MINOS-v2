"use client"

import React from "react"
import {
  PlusCircle,
  Upload,
  FileText,
  CheckCircle2,
  ArrowRightLeft,
  ShieldCheck,
  Trash2,
  Loader2
} from "lucide-react"
import { SectionPanel, SectionHeader, GlowOrb } from "@/components/dashboard/dashboard-ui"
import { useCreatePosition, useFileUpload, usePortfolios } from "@/hooks/use-minos"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { 
    Select, 
    SelectContent, 
    SelectItem, 
    SelectTrigger, 
    SelectValue 
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { motion, AnimatePresence } from "motion/react"
import { toast } from "sonner" 

export default function ManualEntryPage() {
  const { add: addTransaction, loading: adding } = useCreatePosition()
  const { upload: uploadFile, loading: uploading } = useFileUpload()
  const { data: portfolios } = usePortfolios()

  const [formData, setFormData] = React.useState({
    date: new Date().toISOString().split('T')[0],
    ticker: "",
    amount: "",
    price: "",
    currency: "ARS",
    source: "",
    portfolio: "Principal",
  })

  const [bulkConfig, setBulkConfig] = React.useState({
    source: "",
    portfolio: "Principal",
  })

  const [file, setFile] = React.useState<File | null>(null)
  const [isDragging, setIsDragging] = React.useState(false)
  const portfolioOptions = React.useMemo(() => {
    const names = (portfolios ?? []).map((portfolio) => portfolio.name)
    return names.length > 0 ? Array.from(new Set(names)) : ["Principal"]
  }, [portfolios])

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files?.[0]
    if (dropped && /\.(csv|xlsx|xls)$/i.test(dropped.name)) setFile(dropped)
    else if (dropped) toast.error("Formato no soportado. Usá .csv o .xlsx")
  }

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await addTransaction({
        source_name: formData.source,
        portfolio_name: formData.portfolio,
        ticker: formData.ticker,
        quantity: Number(formData.amount),
        valuation: Number(formData.amount) * Number(formData.price),
        currency: formData.currency as "ARS" | "USD",
        valuation_date: formData.date
      })
      toast.success("Transacción registrada con éxito")
      setFormData({
        date: new Date().toISOString().split('T')[0],
        ticker: "",
        amount: "",
        price: "",
        currency: "ARS",
        source: formData.source, // Keep source for convenience
        portfolio: formData.portfolio,
      })
    } catch (err: any) {
      toast.error(err.message || "Error al registrar la transacción")
    }
  }

  const handleFileUpload = async () => {
    if (!file) return
    if (!bulkConfig.source) {
      toast.error("Por favor, especifica el bróker de origen")
      return
    }
    try {
      await uploadFile(file, bulkConfig.source, bulkConfig.portfolio)
      toast.success("Archivo procesado correctamente")
      setFile(null)
    } catch (err: any) {
      toast.error(err.message || "Error al procesar el archivo")
    }
  }

  const handleTemplateDownload = () => {
    const headers = ["ticker", "quantity", "currency", "valuation", "valuation_date"]
    const sample = ["AL30", "100", "ARS", "50000", new Date().toISOString().split("T")[0]]
    const csv = `${headers.join(",")}\n${sample.join(",")}\n`
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = "minos-plantilla-posiciones.csv"
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col gap-6 animate-fade-up max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground font-display">Carga Manual</h1>
        <p className="text-muted-foreground text-sm font-medium">Registra nuevas operaciones o importa archivos de transacciones.</p>
      </div>

      <Tabs defaultValue="single" className="w-full">
        <TabsList className="grid w-full grid-cols-2 max-w-md rounded-xl bg-muted/20 p-1 mb-6 border border-border/40">
          <TabsTrigger value="single" className="rounded-lg font-bold text-xs uppercase tracking-wider data-[state=active]:bg-primary data-[state=active]:text-primary-foreground shadow-sm transition-all">
            Carga Individual
          </TabsTrigger>
          <TabsTrigger value="bulk" className="rounded-lg font-bold text-xs uppercase tracking-wider data-[state=active]:bg-primary data-[state=active]:text-primary-foreground shadow-sm transition-all">
            Importar Archivo
          </TabsTrigger>
        </TabsList>

        <TabsContent value="single">
          <SectionPanel className="relative overflow-hidden">
            <GlowOrb className="w-64 h-64 -top-32 -right-32 bg-primary/5" />
            <SectionHeader title="Nueva Transacción" subtitle="Ingreso manual de movimiento financiero" />
            
            <form onSubmit={handleFormSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <div className="space-y-2">
                <Label htmlFor="ticker" className="text-xs font-semibold text-muted-foreground ml-1">Instrumento (Ticker) <span className="text-destructive">*</span></Label>
                <Input 
                    id="ticker" 
                    placeholder="Ej: AL30, AAPL, BTC" 
                    value={formData.ticker}
                    onChange={(e) => setFormData({...formData, ticker: e.target.value.toUpperCase()})}
                    required
                    className="rounded-xl border-border/50 bg-muted/10 h-11 font-bold"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="source" className="text-xs font-semibold text-muted-foreground ml-1">Fuente / Bróker <span className="text-destructive">*</span></Label>
                <Input 
                    id="source" 
                    placeholder="Ej: Bull Market, Binance, Caja" 
                    value={formData.source}
                    onChange={(e) => setFormData({...formData, source: e.target.value})}
                    required
                    className="rounded-xl border-border/50 bg-muted/10 h-11 font-bold"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="amount" className="text-xs font-semibold text-muted-foreground ml-1">Cantidad / Nominal</Label>
                <Input 
                    id="amount" 
                    type="number" 
                    placeholder="0.00" 
                    step="0.000001"
                    value={formData.amount}
                    onChange={(e) => setFormData({...formData, amount: e.target.value})}
                    required
                    className="rounded-xl border-border/50 bg-muted/10 h-11 font-mono font-bold"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="price" className="text-xs font-semibold text-muted-foreground ml-1">Precio Unitario</Label>
                <Input 
                    id="price" 
                    type="number" 
                    placeholder="0.00" 
                    step="0.01"
                    value={formData.price}
                    onChange={(e) => setFormData({...formData, price: e.target.value})}
                    required
                    className="rounded-xl border-border/50 bg-muted/10 h-11 font-mono font-bold"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                    <Label className="text-xs font-semibold text-muted-foreground ml-1">Moneda</Label>
                    <Select value={formData.currency} onValueChange={(v) => setFormData({...formData, currency: v})}>
                        <SelectTrigger className="rounded-xl border-border/50 bg-muted/10 h-11 font-bold">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl border-border/40">
                            <SelectItem value="ARS">ARS</SelectItem>
                            <SelectItem value="USD">USD</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
                <div className="space-y-2">
                    <Label className="text-xs font-semibold text-muted-foreground ml-1">Cartera Destino</Label>
                    <Select value={formData.portfolio} onValueChange={(v) => setFormData({...formData, portfolio: v})}>
                        <SelectTrigger className="rounded-xl border-border/50 bg-muted/10 h-11 font-bold">
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="rounded-xl border-border/40">
                            {portfolioOptions.map((name) => (
                              <SelectItem key={name} value={name}>{name}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="date" className="text-xs font-semibold text-muted-foreground ml-1">Fecha de Operación</Label>
                <Input 
                    id="date" 
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    required
                    className="rounded-xl border-border/50 bg-muted/10 h-11 font-bold"
                />
              </div>

              <div className="md:col-span-2 mt-4">
                <Button 
                    type="submit" 
                    disabled={adding}
                    className="w-full h-12 rounded-xl text-sm font-bold shadow-xl shadow-primary/20 transition-all hover:scale-[1.01] active:scale-[0.99] gap-2"
                >
                    {adding ? <Loader2 className="size-4 animate-spin" /> : <PlusCircle className="size-4" />}
                    Confirmar Registro de Operación
                </Button>
              </div>
            </form>
          </SectionPanel>
        </TabsContent>

        <TabsContent value="bulk">
          <SectionPanel className="relative overflow-hidden group">
            <GlowOrb className="w-56 h-56 -bottom-24 -left-24 bg-chart-4/10" />
            <SectionHeader title="Importación Masiva" subtitle="Sube un archivo Excel o CSV con tus movimientos" />
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 mb-8">
              <div className="space-y-2">
                <Label className="text-xs font-semibold text-muted-foreground ml-1">Bróker / Fuente</Label>
                <Input 
                    placeholder="Ej: Balanz, IOL" 
                    value={bulkConfig.source}
                    onChange={(e) => setBulkConfig({...bulkConfig, source: e.target.value})}
                    className="rounded-xl border-border/50 bg-muted/10 h-10 font-bold"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-xs font-semibold text-muted-foreground ml-1">Cartera Destino</Label>
                <Select value={bulkConfig.portfolio} onValueChange={(v) => setBulkConfig({...bulkConfig, portfolio: v})}>
                    <SelectTrigger className="rounded-xl border-border/50 bg-muted/10 h-10 font-bold">
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                        {portfolioOptions.map((name) => (
                          <SelectItem key={name} value={name}>{name}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
              </div>
            </div>
            
            <div
              className={`mt-8 border-2 border-dashed rounded-3xl p-12 flex flex-col items-center justify-center transition-all cursor-pointer relative overflow-hidden
                ${isDragging
                  ? "border-primary bg-primary/5 scale-[1.01] shadow-lg shadow-primary/10"
                  : "border-border/40 bg-muted/5 group-hover:bg-muted/10 group-hover:border-primary/30"
                }`}
              onClick={() => document.getElementById('file-upload')?.click()}
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragEnter={(e) => { e.preventDefault(); setIsDragging(true) }}
              onDragLeave={(e) => { e.preventDefault(); setIsDragging(false) }}
              onDrop={handleDrop}
            >
              <input 
                id="file-upload"
                type="file" 
                className="hidden" 
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                accept=".csv,.xlsx,.xls"
              />
              
              <AnimatePresence mode="wait">
                {!file ? (
                  <motion.div 
                    key="empty"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="flex flex-col items-center gap-4 text-center"
                  >
                    <div className="size-16 rounded-2xl bg-primary/10 flex items-center justify-center border border-primary/20 text-primary">
                      <Upload className="size-8" />
                    </div>
                    <div>
                      <p className="text-base font-bold text-foreground">
                        {isDragging ? "Soltá el archivo aquí" : "Arrastrá o seleccioná un archivo"}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1 max-w-[240px]">Formato soportado: .xlsx, .csv. Máximo 10MB.</p>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div 
                    key="file"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="flex flex-col items-center gap-4 text-center"
                  >
                    <div className="size-16 rounded-2xl bg-fin-gain/10 flex items-center justify-center border border-fin-gain/20 text-fin-gain">
                      <FileText className="size-8" />
                    </div>
                    <div>
                      <p className="text-base font-bold text-foreground">{file.name}</p>
                      <p className="text-xs text-muted-foreground mt-1">{(file.size / 1024).toFixed(2)} KB</p>
                    </div>
                    <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={(e) => { e.stopPropagation(); setFile(null); }}
                        className="text-destructive hover:bg-destructive/10 h-8 rounded-lg mt-2"
                    >
                        <Trash2 className="size-3.5 mr-2" />
                        Eliminar archivo
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="mt-8 flex flex-col md:flex-row gap-4">
              <Button
                type="button"
                variant="outline"
                className="flex-1 h-11 rounded-xl font-bold border-border/50 bg-muted/10 hover:bg-muted/20 gap-2"
                onClick={handleTemplateDownload}
              >
                <FileText className="size-4" />
                Descargar Plantilla
              </Button>
              <Button 
                disabled={!file || uploading} 
                className="flex-[2] h-11 rounded-xl font-bold shadow-lg shadow-primary/20 gap-2"
                onClick={handleFileUpload}
              >
                {uploading ? <Loader2 className="size-4 animate-spin" /> : <CheckCircle2 className="size-4" />}
                Procesar Archivo Importado
              </Button>
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3 p-4 rounded-2xl bg-muted/20 border border-border/40">
                    <CheckCircle2 className="size-4 text-fin-gain" />
                    <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">Validación Automática</span>
                </div>
                <div className="flex items-center gap-3 p-4 rounded-2xl bg-muted/20 border border-border/40">
                    <ArrowRightLeft className="size-4 text-primary" />
                    <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">Compensación de Precios</span>
                </div>
                <div className="flex items-center gap-3 p-4 rounded-2xl bg-muted/20 border border-border/40">
                    <ShieldCheck className="size-4 text-chart-4" />
                    <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">Audit Log Seguro</span>
                </div>
            </div>
          </SectionPanel>
        </TabsContent>
      </Tabs>
    </div>
  )
}
