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
    if (typeof screen !== 'undefined' && screen.orientation?.lock) {
      screen.orientation.lock('portrait').catch(() => {})
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
