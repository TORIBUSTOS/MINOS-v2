"use client"

import React, { useState, useEffect } from "react"
import { User, Bell, Shield, Database, Palette, Trash2, CheckCircle } from "lucide-react"
import { PageHeader, SectionPanel, SectionHeader } from "@/components/dashboard/dashboard-ui"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { useResetUploadedData } from "@/hooks/use-minos"

const PROFILE_KEY = "minos_profile"

const SECTIONS = [
  { icon: User, label: "Perfil" },
  { icon: Bell, label: "Notificaciones" },
  { icon: Shield, label: "Seguridad" },
  { icon: Database, label: "Datos" },
  { icon: Palette, label: "Apariencia" },
]

function loadProfile() {
  if (typeof window === "undefined") return { name: "Rodrigo Bustos", email: "rbustos@sanarte.com.ar" }
  try {
    const raw = localStorage.getItem(PROFILE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return { name: "Rodrigo Bustos", email: "rbustos@sanarte.com.ar" }
}

export default function SettingsPage() {
  const { reset, loading, error, result } = useResetUploadedData()
  const [name, setName] = useState("Rodrigo Bustos")
  const [email, setEmail] = useState("rbustos@sanarte.com.ar")
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    const profile = loadProfile()
    setName(profile.name)
    setEmail(profile.email)
  }, [])

  function handleSave() {
    localStorage.setItem(PROFILE_KEY, JSON.stringify({ name, email }))
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  return (
    <div className="flex max-w-4xl flex-col gap-6 animate-fade-up">
      <PageHeader title="Configuración" subtitle="Administrá tu cuenta y preferencias del sistema." />

      {/* Perfil */}
      <SectionPanel>
        <SectionHeader title="Perfil" subtitle="Información de tu cuenta" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="text-xs font-bold text-muted-foreground">Nombre</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="rounded-xl bg-muted/10 border-border/50 h-10"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email" className="text-xs font-bold text-muted-foreground">Email</Label>
            <Input
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="rounded-xl bg-muted/10 border-border/50 h-10"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="role" className="text-xs font-bold text-muted-foreground">Rol</Label>
            <Input id="role" defaultValue="Admin" disabled className="rounded-xl bg-muted/5 border-border/30 h-10 text-muted-foreground" />
          </div>
        </div>
        <div className="mt-6 flex items-center gap-3">
          <Button size="sm" className="rounded-xl font-bold shadow-lg shadow-primary/20" onClick={handleSave}>
            Guardar cambios
          </Button>
          {saved && (
            <span className="flex items-center gap-1.5 text-xs font-semibold text-emerald-500">
              <CheckCircle className="size-3.5" />
              Guardado
            </span>
          )}
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
            <div key={item.label} className="flex items-center justify-between gap-4 rounded-xl border border-border/30 bg-background/25 p-3">
              <div className="min-w-0">
                <p className="text-sm font-semibold text-foreground">{item.label}</p>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </div>
              <Switch defaultChecked className="shrink-0" />
            </div>
          ))}
        </div>
      </SectionPanel>

      {/* Datos */}
      <SectionPanel>
        <SectionHeader title="Datos" subtitle="Administración de cargas locales" />
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="min-w-0">
            <p className="text-sm font-semibold text-foreground">Reiniciar datos cargados</p>
            <p className="text-xs text-muted-foreground">
              Borra posiciones importadas por archivo y carga manual. Conserva datos de API y conectores.
            </p>
            {result ? (
              <p className="mt-2 text-xs font-mono text-emerald-500">
                Borradas {result.positions_deleted} posiciones y {result.load_records_deleted} cargas.
              </p>
            ) : null}
            {error ? (
              <p className="mt-2 text-xs font-medium text-rose-500">{error.message}</p>
            ) : null}
          </div>

          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" size="sm" className="h-10 w-full gap-2 rounded-xl font-bold md:w-auto" disabled={loading}>
                <Trash2 className="size-4" />
                {loading ? "Borrando..." : "Reiniciar"}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Reiniciar datos cargados</AlertDialogTitle>
                <AlertDialogDescription>
                  Esta acción borra posiciones importadas por CSV/XLSX y carga manual. No borra datos de API, conectores,
                  fuentes, carteras ni tickers base.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                <AlertDialogAction onClick={reset} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                  Confirmar reinicio
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
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
