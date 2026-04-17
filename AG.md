# AG.md — MINOS PRIME (Frontend & Integration)

Arquitectura visual y lógica de interfaz para el Sistema de Inteligencia Patrimonial de TORO.
Agente: Antigravity (AG) — Google Deepmind.

---

## Stack (Frontend)

| Capa | Tecnología |
|------|-----------|
| Core | Next.js 16 + React 19 |
| Styling | Vanilla CSS + Radix UI (Shadcn Base) |
| Animaciones | Framer Motion (para micro-interacciones premium) |
| Gráficos | Recharts (Dashboard & Analytics) |
| Iconos | Lucide React |
| API Layer | Custom hooks (`use-minos.ts`) + Fetch API |

---

## Comandos

```bash
# Directorio de trabajo
cd v0-financial-toro-dashboard-2-main

# Instalar dependencias
npm install

# Levantar servidor de desarrollo (en http://localhost:3001)
npm run dev

# Construir para producción
npm run build

# Linting y verificación de tipos
npm run lint
```

---

## Estructura (v0-financial-toro-dashboard-2-main)

```
v0-financial-toro-dashboard-2-main/
├── app/
│   ├── instruments/      # Gestión de activos categorizados
│   ├── tickers/          # Vista unificada cross-portfolio [AG]
│   ├── manual-entry/     # Ingreso de datos manual
│   ├── sources/          # Gestión de brokers/fuentes
│   ├── layout.tsx        # Navegación y branding MINOS Prime
│   └── page.tsx          # Dashboard principal
├── components/
│   ├── dashboard/        # Gráficos y KPIs (Allocation, Market, Currency)
│   ├── layout/           # Sidebar y Header unificado
│   └── ui/               # Componentes atómicos (shadcn)
├── hooks/
│   └── use-minos.ts      # Integración con Minos API (8001)
├── lib/
│   └── minos-formatters.ts # Lógica de formateo y mapeo central [AG]
├── types/
│   └── minos.ts          # Contratos TypeScript con el Backend
└── AG.md                 # Esta documentación
```

---

## Convenciones de AG

- **Aesthetics First:** Diseño dark-mode premium con uso de gradientes sutiles y "Glow Orbs".
- **Zero Placeholders:** Uso de `generate_image` para assets reales y datos simulados coherentes (Balanz data context).
- **Categorización Centralizada:** El mapeo de tickers a categorías NO se hace en los componentes, se centraliza en `lib/minos-formatters.ts`.
- **Responsive Design:** Todas las tablas y dashboards deben ser adaptables a diferentes viewports.
- **Señales Logics:** Implementación de "Semáforo" (BUY/HOLD/SELL) en vistas de tickers para valor agregado visual.

---

## Sync & Integration (BN-006 / BN-008)

- **Frontend-Backend Contract:** Toda la data fluye a través de `useMinos` hooks conectando a `localhost:8001`.
- **Normalization:** AG implementó heurísticas en el frontend para clasificar activos que el backend aún no categoriza dinámicamente.
- **Tickers Layer:** Integración del endpoint `/api/v1/tickers/unified` en la nueva vista de Tickers.

---

## Git Workflow (AG Style)

- **Direct Push:** Para iteraciones de pulido visual aprobadas por Tori, commit directo a `main`.
- **Commit Messages:** Siguen el estándar `feat: description` o `refactor: description`.
- **Documentación:** Cada gran iteración incluye un `walkthrough_N.md` en el directorio de la oficina (`.gemini/antigravity`).

---

## Trabajo Realizado (Antigravity)

**Sprint 1 — TRACK C: Frontend Base** ✅
- [x] AG-001: Branding & Shell (Sidebar, Header, Metadata)
- [x] AG-002: Dashboard View (KPIs, Donut de Alocación, Market Widget)
- [x] AG-003: Currency Exposure (Barra de exposición ARS/USD)
- [x] AG-004: Instruments Page (Categorización dinámica y agrupamiento)
- [x] AG-005: Tickers Unificados (Vista cross-portfolio con lógica de señales)
- [x] AG-006: Rebranding Final (Meridian -> MINOS Prime)

**Estado:** 100% Funcional, Sincronizado con GitHub. 🚀

Branch activo: `main` (Subido a https://github.com/TORIBUSTOS/MINOS-v2.git)

---

> [!IMPORTANT]
> **Antigravity** mantiene la integridad estética por sobre todas las cosas. Si una vista se ve "simple", AG la refactoriza para que sea "Premium".
