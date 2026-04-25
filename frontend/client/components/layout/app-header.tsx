"use client"

import * as React from "react"
import { 
  Search, 
  Bell, 
  Menu, 
  Github, 
  Plus, 
  History, 
  TrendingUp,
  RefreshCw
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
import { usePathname } from "next/navigation"

export function AppHeader() {
  const pathname = usePathname()
  
  const getPageTitle = (path: string) => {
    switch (path) {
      case "/": return "Dashboard"
      case "/instruments": return "Mis Instrumentos"
      case "/sources": return "Por Fuente"
      case "/manual-entry": return "Carga Manual"
      case "/settings": return "Configuración"
      default: return "MINOS"
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
        <div className="relative hidden md:block group">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            type="search"
            placeholder="Buscar instrumento..."
            className="w-64 lg:w-80 h-9 pl-9 bg-muted/30 border-muted-foreground/10 focus-visible:ring-primary/20 transition-all rounded-xl"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 hidden h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100 sm:flex pointer-events-none text-muted-foreground/50">
            <span className="text-xs">⌘</span>K
          </kbd>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-1.5">
          <Button variant="ghost" size="icon" className="group rounded-xl relative">
            <RefreshCw className="size-4 text-muted-foreground transition-transform group-hover:rotate-180 duration-500" />
            <span className="sr-only">Sincronizar</span>
          </Button>

          <Button variant="ghost" size="icon" className="group rounded-xl relative">
            <Bell className="size-4 text-muted-foreground transition-colors group-hover:text-primary" />
            <div className="absolute top-2.5 right-2.5 size-2 rounded-full bg-primary ring-2 ring-background animate-pulse" />
            <span className="sr-only">Notificaciones</span>
          </Button>

          <Button variant="outline" size="sm" className="hidden lg:flex gap-2 rounded-xl border-primary/20 hover:bg-primary/5 hover:text-primary transition-all font-semibold">
            <Plus className="size-3.5" />
            Movimiento
          </Button>
        </div>
      </div>
    </header>
  )
}
