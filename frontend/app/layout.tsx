import type { Metadata } from 'next'
import { ClerkProvider } from '@clerk/nextjs'
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

export const metadata: Metadata = {
  metadataBase: new URL('https://localelive.space'),
  title: {
    default: 'Localelive - AI-Powered Local Search Engine',
    template: '%s | Localelive'
  },
  description:
    'Find nearby services, restaurants, shops, and local businesses using AI-powered search. Localelive combines real-time IoT data with intelligent agents to deliver personalized local recommendations.',
  keywords: [
    'local search',
    'AI search engine',
    'nearby services',
    'local businesses',
    'IoT search',
    'restaurant finder',
    'local recommendations',
    'localelive',
  ],
  icons: {
    icon: '/localelive-light-icon.png',
    shortcut: '/localelive-light-icon.png',
    apple: '/localelive-light-icon.png'
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Localelive'
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://localelive.space',
    siteName: 'Localelive',
    title: 'Localelive - AI-Powered Local Search Engine',
    description:
      'Find nearby services, restaurants, shops, and local businesses using AI-powered search with real-time IoT data.',
    images: [
      {
        url: '/localelive-light-icon.png',
        width: 512,
        height: 512,
        alt: 'Localelive Logo',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Localelive - AI-Powered Local Search Engine',
    description:
      'Find nearby services, restaurants, shops, and local businesses using AI-powered search with real-time IoT data.',
    images: ['/localelive-light-icon.png'],
  },
  alternates: {
    canonical: 'https://localelive.space',
  },
  manifest: '/manifest.json',
  verification: {
    google: 'pSRgmR-HqtRoDAEwBR92z5KyNsvyiVxfsFQmf8MC6J0',
  },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'Organization',
      name: 'Localelive',
      url: 'https://localelive.space',
      logo: 'https://localelive.space/localelive-light-icon.png',
    },
    {
      '@type': 'WebApplication',
      name: 'Localelive',
      url: 'https://localelive.space',
      applicationCategory: 'SearchApplication',
      description:
        'AI-powered local search engine that combines real-time IoT data with intelligent agents to find nearby services and businesses.',
    },
  ],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="format-detection" content="telephone=no" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>
        <ClerkProvider>
          <ThemesProvider>
            <Header />
            {children}
            <Toaster />
          </ThemesProvider>
          <Analytics />
        </ClerkProvider>
      </body>
    </html>
  )
}
