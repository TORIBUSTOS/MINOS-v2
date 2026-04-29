"use client"

import * as React from "react"
import {
  Search,
  Bell,
  Plus,
  RefreshCw,
  CheckCircle2
} from "lucide-react"

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Separator } from "@/components/ui/separator"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import { usePathname, useRouter } from "next/navigation"
import { MinosAPI } from "@/lib/minos-api"
import { triggerMinosRefresh } from "@/hooks/use-minos"
import { useToast } from "@/hooks/use-toast"

export function AppHeader() {
  const pathname = usePathname()
  const router = useRouter()
  const { toast } = useToast()
  const [syncing, setSyncing] = React.useState(false)
  const [search, setSearch] = React.useState("")

  const getPageTitle = (path: string) => {
    switch (path) {
      case "/": return "Dashboard"
      case "/instruments": return "Mis Instrumentos"
      case "/sources": return "Por Fuente"
      case "/tickers": return "Tickers Unificados"
      case "/manual-entry": return "Carga Manual"
      case "/settings": return "Configuración"
      default: return "MINOS"
    }
  }

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const query = search.trim()
    if (!query) return
    router.push(`/instruments?q=${encodeURIComponent(query)}`)
  }

  const handleSync = async () => {
    setSyncing(true)
    try {
      await MinosAPI.refreshPrices()
      triggerMinosRefresh()
      toast({
        title: "Datos sincronizados",
        description: "Se refrescaron precios, cartera, señales y vistas conectadas.",
      })
    } catch (error) {
      toast({
        title: "No se pudo sincronizar",
        description: error instanceof Error ? error.message : "Verificá que el backend esté disponible.",
        variant: "destructive",
      })
    } finally {
      setSyncing(false)
    }
  }

  return (
    <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center justify-between gap-2 border-b bg-background/80 px-4 backdrop-blur-md transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
      <div className="flex items-center gap-2">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem className="hidden md:block">
              <BreadcrumbLink href="/" className="text-muted-foreground/60 transition-colors hover:text-foreground">
                MINOS
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator className="hidden md:block" />
            <BreadcrumbItem>
              <BreadcrumbPage className="font-semibold text-foreground">{getPageTitle(pathname)}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </div>

      <div className="flex items-center gap-4">
        {/* Search - Desktop */}
        <form className="relative hidden md:block group" onSubmit={handleSearch}>
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            type="search"
            placeholder="Buscar instrumento..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="w-64 lg:w-80 h-9 pl-9 bg-muted/30 border-muted-foreground/10 focus-visible:ring-primary/20 transition-all rounded-xl"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex pointer-events-none text-muted-foreground/50">
            <span className="text-xs">⌘</span>K
          </kbd>
        </form>

        {/* Action Buttons */}
        <div className="flex items-center gap-1.5">
          <Button
            variant="ghost"
            size="icon"
            className="group rounded-xl relative"
            onClick={handleSync}
            disabled={syncing}
            title="Sincronizar datos"
          >
            {syncing
              ? <CheckCircle2 className="size-4 text-primary" />
              : <RefreshCw className="size-4 text-muted-foreground transition-transform group-hover:rotate-180 duration-500" />
            }
            <span className="sr-only">Sincronizar</span>
          </Button>

          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" className="group rounded-xl relative">
                <Bell className="size-4 text-muted-foreground transition-colors group-hover:text-primary" />
                <span className="sr-only">Notificaciones</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent align="end" className="w-72 rounded-2xl p-0 overflow-hidden">
              <div className="px-4 py-3 border-b border-border/40">
                <p className="text-sm font-bold text-foreground">Notificaciones</p>
              </div>
              <div className="flex flex-col items-center justify-center py-8 gap-2 text-center px-4">
                <Bell className="size-8 text-muted-foreground/30" />
                <p className="text-sm font-medium text-muted-foreground">Sin notificaciones nuevas</p>
                <p className="text-xs text-muted-foreground/60">Te avisaremos cuando haya alertas de cartera.</p>
              </div>
            </PopoverContent>
          </Popover>

          <Button
            variant="outline"
            size="sm"
            className="hidden lg:flex gap-2 rounded-xl border-primary/20 hover:bg-primary/5 hover:text-primary transition-all font-semibold"
            onClick={() => router.push("/manual-entry")}
          >
            <Plus className="size-3.5" />
            Movimiento
          </Button>
        </div>
      </div>
    </header>
  )
}
