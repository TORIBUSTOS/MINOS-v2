import type { Metadata } from 'next'
import { DM_Sans, JetBrains_Mono, Outfit } from 'next/font/google'
import './globals.css'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/layout/app-sidebar'
import { AppHeader } from '@/components/layout/app-header'

const _dmSans = DM_Sans({ subsets: ["latin"], weight: ["400", "500", "600", "700"] })
const _jetbrains = JetBrains_Mono({ subsets: ["latin"], weight: ["400", "500", "600", "700"] })
const _outfit = Outfit({ subsets: ["latin"], weight: ["400", "500", "600", "700", "800"] })

export const metadata: Metadata = {
  title: 'MINOS Prime — Financial Analytics Dashboard',
  description: 'Professional financial analytics dashboard for TORO HOLDING.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className="dark">
      <body className={`${_outfit.className} font-sans antialiased grain text-foreground`}>
        <SidebarProvider>
          <AppSidebar />
          <SidebarInset>
            <AppHeader />
            <main className="flex-1 p-4 lg:p-6 overflow-x-hidden">
              {children}
            </main>
          </SidebarInset>
        </SidebarProvider>
        <Analytics />
      </body>
    </html>
  )
}
