import { Analytics } from '@vercel/analytics/react'
import { Toaster } from 'react-hot-toast'
import { Header } from '@/components/Header'
import ThemesProvider from '@/providers/ThemesProvider'
import '@/styles/globals.scss'
import '@/styles/theme-config.css'

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover'
}

export const metadata = {
  title: {
    default: 'localelive',
    template: `%s - localelive`
  },
  description: 'AI assistant powered by Localelive',
  icons: {
    icon: '/localelive-light-icon.png',
    shortcut: '/localelive-light-icon.png',
    apple: '/localelive-light-icon.png'
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'localelive'
  }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="format-detection" content="telephone=no" />
      </head>
      <body>
        <ThemesProvider>
          <Header />
          {children}
          <Toaster />
        </ThemesProvider>
        <Analytics />
      </body>
    </html>
  )
}
