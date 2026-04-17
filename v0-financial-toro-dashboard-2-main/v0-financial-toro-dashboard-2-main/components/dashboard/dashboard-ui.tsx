"use client"

import React from "react"
import { motion } from "motion/react"
import { 
  ArrowUpRight, 
  ArrowDownRight, 
  DollarSign, 
  TrendingUp, 
  Wallet, 
  ArrowRightLeft,
  Loader2,
  AlertCircle
} from "lucide-react"

const CARD_SHADOW =
  "rgba(14, 63, 126, 0.04) 0px 0px 0px 1px, rgba(42, 51, 69, 0.04) 0px 1px 1px -0.5px, rgba(42, 51, 70, 0.04) 0px 3px 3px -1.5px, rgba(42, 51, 70, 0.04) 0px 6px 6px -3px, rgba(14, 63, 126, 0.04) 0px 12px 12px -6px, rgba(14, 63, 126, 0.04) 0px 24px 24px -12px"

const EASE_OUT = [0.16, 1, 0.3, 1] as const

interface KpiCardProps {
  label: string
  value: string
  change?: number
  prefix?: string
  suffix?: string
  delay?: number
  icon?: React.ElementType
  subtext?: string
}

export function KpiCard({
  label,
  value,
  change,
  prefix = "",
  suffix = "",
  delay = 0,
  icon: Icon,
  subtext = "vs ayer",
}: KpiCardProps) {
  const isPositive = (change ?? 0) >= 0
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 16, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, delay, ease: EASE_OUT }}
      className="relative overflow-hidden rounded-2xl surface-card p-4 lg:p-5 group hover:scale-[1.01] transition-all duration-300"
      style={{ boxShadow: CARD_SHADOW }}
    >
      <div className="absolute top-0 right-0 w-24 h-24 opacity-[0.03] pointer-events-none group-hover:opacity-[0.05] transition-opacity">
        {Icon && <Icon className="size-24 -translate-y-4 translate-x-4" />}
      </div>
      
      <p className="text-[11px] font-bold tracking-[0.08em] uppercase text-muted-foreground mb-2.5 font-sans">
        {label}
      </p>
      
      <div className="flex items-baseline gap-1">
        <span className="text-muted-foreground/60 text-lg font-mono font-medium">{prefix}</span>
        <p className="text-2xl lg:text-3xl font-bold text-foreground font-mono tracking-tighter leading-none">
          {value}
        </p>
        <span className="text-muted-foreground/60 text-lg font-mono font-medium">{suffix}</span>
      </div>

      {change !== undefined ? (
        <div className="flex items-center gap-1.5 mt-3">
          <div className={`flex items-center gap-0.5 text-[10px] font-bold font-mono px-1.5 py-0.5 rounded-md ${
            isPositive ? "bg-fin-gain/10 text-fin-gain" : "bg-fin-loss/10 text-fin-loss"
          }`}>
            {isPositive ? <ArrowUpRight className="size-3" /> : <ArrowDownRight className="size-3" />}
            {isPositive ? "+" : ""}{change.toFixed(2)}%
          </div>
          <span className="text-[10px] text-muted-foreground/70 font-sans">{subtext}</span>
        </div>
      ) : (
          <div className="h-6 mt-3" /> // Spacer
      )}
    </motion.div>
  )
}

export function GlowOrb({ className }: { className?: string }) {
  return (
    <div className={`absolute rounded-full blur-3xl pointer-events-none opacity-20 ${className}`} />
  )
}

export function SectionPanel({ 
  children, 
  className = "", 
  delay = 0.1 
}: { 
  children: React.ReactNode; 
  className?: string; 
  delay?: number 
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: EASE_OUT }}
      className={`rounded-2xl surface-card p-5 lg:p-6 overflow-hidden relative ${className}`}
      style={{ boxShadow: CARD_SHADOW }}
    >
      {children}
    </motion.div>
  )
}

export function SectionHeader({ 
  title, 
  subtitle, 
  children 
}: { 
  title: string; 
  subtitle: string; 
  children?: React.ReactNode 
}) {
  return (
    <div className="flex items-center justify-between mb-6">
      <div>
        <h3 className="text-sm font-bold text-foreground tracking-tight font-display uppercase tracking-wider">{title}</h3>
        <p className="text-[11px] text-muted-foreground mt-0.5 font-sans font-medium">{subtitle}</p>
      </div>
      {children}
    </div>
  )
}

export function LoadingState({ message = "Cargando datos financieros..." }: { message?: string }) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
            <Loader2 className="size-8 text-primary animate-spin" />
            <p className="text-sm text-muted-foreground font-medium animate-pulse">{message}</p>
        </div>
    )
}

export function ErrorState({ error, refetch }: { error: any, refetch: () => void }) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 p-8 rounded-2xl border border-destructive/20 bg-destructive/5">
            <AlertCircle className="size-12 text-destructive" />
            <div className="text-center">
                <h3 className="text-lg font-bold text-foreground">Error de Conexión</h3>
                <p className="text-sm text-muted-foreground max-w-md mx-auto mt-2">
                    No se pudo conectar con el sistema de inteligencia patrimonial. {error?.message || "Verifique que el backend esté corriendo."}
                </p>
            </div>
            <button 
                onClick={refetch}
                className="mt-4 px-6 py-2 bg-foreground text-background rounded-xl font-bold text-sm hover:scale-105 transition-transform"
            >
                Reintentar Conexión
            </button>
        </div>
    )
}
