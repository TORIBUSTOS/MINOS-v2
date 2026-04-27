"use client"

import React from "react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { SectionPanel, SectionHeader, GlowOrb } from "./dashboard-ui"
import { assetColor } from "@/lib/minos-formatters"

const CARD_SHADOW =
  "rgba(14, 63, 126, 0.04) 0px 0px 0px 1px, rgba(42, 51, 69, 0.04) 0px 1px 1px -0.5px, rgba(42, 51, 70, 0.04) 0px 3px 3px -1.5px, rgba(42, 51, 70, 0.04) 0px 6px 6px -3px, rgba(14, 63, 126, 0.04) 0px 12px 12px -6px, rgba(14, 63, 126, 0.04) 0px 24px 24px -12px"

function ChartTooltipContent({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const data = payload[0].payload
  return (
    <div className="rounded-xl surface-elevated p-3 text-xs backdrop-blur-md border border-border/50" style={{ boxShadow: CARD_SHADOW }}>
      <p className="text-muted-foreground mb-1.5 font-bold uppercase tracking-wider font-sans">{data.name}</p>
      <div className="flex items-center gap-2">
        <div className="size-2 rounded-full" style={{ backgroundColor: payload[0].color }} />
        <span className="font-mono font-bold text-foreground text-sm">{data.value.toLocaleString()}%</span>
      </div>
    </div>
  )
}

export function AllocationDonut({ data }: { data: { name: string, value: number }[] }) {
  return (
    <SectionPanel className="flex flex-col">
      <GlowOrb className="w-32 h-32 -bottom-16 -right-16 bg-primary/10" />
      <SectionHeader title="Distribución por Activo" subtitle="Exposición porcentual" />
      
      <div className="h-[240px] w-full flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius="62%"
              outerRadius="85%"
              paddingAngle={4}
              dataKey="value"
              animationDuration={1200}
              animationEasing="ease-out"
              stroke="none"
            >
              {data.map((entry, i) => (
                <Cell key={`cell-${i}`} fill={assetColor(entry.name)} />
              ))}
            </Pie>
            <Tooltip content={<ChartTooltipContent />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-2 mt-4">
        {data.map((item, i) => (
          <div key={i} className="flex items-center justify-between text-[11px] group cursor-default">
            <div className="flex items-center gap-2">
              <div className="size-2 rounded-full ring-2 ring-background ring-offset-1 ring-offset-transparent group-hover:ring-offset-muted-foreground/20 transition-all" style={{ backgroundColor: assetColor(item.name) }} />
              <span className="text-muted-foreground font-sans font-medium group-hover:text-foreground transition-colors">{item.name}</span>
            </div>
            <span className="font-mono font-bold text-foreground">{item.value.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </SectionPanel>
  )
}
