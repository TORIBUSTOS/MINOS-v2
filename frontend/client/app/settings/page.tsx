"use client"

import React from "react"
import { Settings, User, Bell, Shield, Database, Palette } from "lucide-react"
import { SectionPanel, SectionHeader } from "@/components/dashboard/dashboard-ui"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"

const SECTIONS = [
  { icon: User, label: "Perfil" },
  { icon: Bell, label: "Notificaciones" },
  { icon: Shield, label: "Seguridad" },
  { icon: Database, label: "Datos" },
  { icon: Palette, label: "Apariencia" },
]

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-6 animate-fade-up max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground font-display">Configuración</h1>
        <p className="text-muted-foreground text-sm font-medium">Administrá tu cuenta y preferencias del sistema.</p>
      </div>

      {/* Perfil */}
      <SectionPanel>
        <SectionHeader title="Perfil" subtitle="Información de tu cuenta" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-xs font-bold text-muted-foreground">Nombre</Label>
            <Input id="name" defaultValue="Mauricio Bustos" className="rounded-xl bg-muted/10 border-border/50 h-10" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email" className="text-xs font-bold text-muted-foreground">Email</Label>
            <Input id="email" defaultValue="m.bustos@toro.holdings" className="rounded-xl bg-muted/10 border-border/50 h-10" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="role" className="text-xs font-bold text-muted-foreground">Rol</Label>
            <Input id="role" defaultValue="Admin" disabled className="rounded-xl bg-muted/5 border-border/30 h-10 text-muted-foreground" />
          </div>
        </div>
        <div className="mt-6">
          <Button size="sm" className="rounded-xl font-bold shadow-lg shadow-primary/20">Guardar cambios</Button>
        </div>
      </SectionPanel>

      {/* Notificaciones */}
      <SectionPanel>
        <SectionHeader title="Notificaciones" subtitle="Configurá qué alertas recibir" />
        <div className="space-y-4">
          {[
            { label: "Alertas de concentración de cartera", description: "Cuando un activo supere el 30% del total" },
            { label: "Actualizaciones de precios", description: "Al expirar el caché de market data" },
            { label: "Confirmación de carga", description: "Al importar o cargar posiciones nuevas" },
          ].map((item) => (
            <div key={item.label} className="flex items-center justify-between py-2">
              <div>
                <p className="text-sm font-semibold text-foreground">{item.label}</p>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </div>
              <Switch defaultChecked />
            </div>
          ))}
        </div>
      </SectionPanel>

      {/* Sistema */}
      <SectionPanel>
        <SectionHeader title="Sistema" subtitle="Información de la instancia" />
        <div className="space-y-3">
          {[
            { label: "Versión", value: "MINOS Prime v2.0" },
            { label: "Backend", value: "http://localhost:8800" },
            { label: "Base de datos", value: "SQLite (MVP)" },
            { label: "Cache TTL", value: "15 minutos" },
          ].map((item) => (
            <div key={item.label} className="flex items-center justify-between py-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground">{item.label}</span>
              <span className="text-xs font-mono font-bold text-foreground">{item.value}</span>
            </div>
          ))}
        </div>
      </SectionPanel>
    </div>
  )
}
