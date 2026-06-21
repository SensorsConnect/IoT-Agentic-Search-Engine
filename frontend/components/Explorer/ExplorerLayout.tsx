'use client'

import { useState, useEffect } from 'react'
import MapPanel from './MapPanel'
import SearchBar from './SearchBar'
import AIResponsePanel from './AIResponsePanel'
import PlaceCardStrip from './PlaceCardStrip'
import PlaceDetailSheet from './PlaceDetailSheet'
import HistoryDrawer from './HistoryDrawer'
import MobileSearchSheet from './MobileSearchSheet'
import { useMapContext } from './MapContext'

const SEARCH_BAR_H = 56 // px – idle mobile search bar height

export default function ExplorerLayout() {
  const [historyOpen, setHistoryOpen] = useState(false)
  const { mobileMapRatio, aiResponse, activePlaces } = useMapContext()

  useEffect(() => {
    // Prevent page scroll while the full-screen explorer is mounted.
    // Lock both html and body to cover all browsers (Safari scrolls <html>).
    const html = document.documentElement
    const body = document.body
    const prevHtmlOverflow = html.style.overflow
    const prevBodyOverflow = body.style.overflow
    const prevHtmlHeight = html.style.height
    const prevBodyHeight = body.style.height

    html.style.overflow = 'hidden'
    html.style.height = '100%'
    body.style.overflow = 'hidden'
    body.style.height = '100%'

    // Reset any existing scroll so the container never starts below the header
    window.scrollTo(0, 0)

    return () => {
      html.style.overflow = prevHtmlOverflow
      html.style.height = prevHtmlHeight
      body.style.overflow = prevBodyOverflow
      body.style.height = prevBodyHeight
    }
  }, [])

  const hasResults = !!(aiResponse || activePlaces.length > 0)

  return (
    <div className="relative w-full h-[calc(100svh-56px)] overscroll-contain bg-gray-100 dark:bg-surface-dark overflow-hidden">
      {/* Map container — always full-size on both mobile and desktop */}
      <div className="absolute inset-0">
        <MapPanel />
      </div>

      {/* Desktop floating panels (hidden on mobile) */}
      <div data-desktop-panel>
        <SearchBar onToggleHistory={() => setHistoryOpen(true)} />
        <AIResponsePanel />
        <PlaceCardStrip />
        <PlaceDetailSheet />
      </div>

      {/* Mobile split panel (hidden on desktop) */}
      <MobileSearchSheet onToggleHistory={() => setHistoryOpen(true)} />

      {/* History drawer */}
      <HistoryDrawer open={historyOpen} onClose={() => setHistoryOpen(false)} />
    </div>
  )
}
