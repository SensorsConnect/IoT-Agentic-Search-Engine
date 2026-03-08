'use client'

import { createContext, useContext, useState, ReactNode, useCallback } from 'react'
import type { Place } from '@/components/Chat/interface'

interface MapContextType {
  activePlaces: Place[]
  activeUserLocation: { latitude: number; longitude: number } | null
  selectedPlaceId: string | null
  hoveredPlaceId: string | null
  aiResponse: string | null
  isQuerying: boolean
  mobileMapRatio: number
  setActivePlaces: (places: Place[]) => void
  setActiveUserLocation: (loc: { latitude: number; longitude: number } | null) => void
  setSelectedPlaceId: (id: string | null) => void
  setHoveredPlaceId: (id: string | null) => void
  setAiResponse: (response: string | null) => void
  setIsQuerying: (loading: boolean) => void
  setMobileMapRatio: (n: number) => void
}

const MapContext = createContext<MapContextType | undefined>(undefined)

export function MapProvider({ children }: { children: ReactNode }) {
  const [activePlaces, setActivePlaces] = useState<Place[]>([])
  const [activeUserLocation, setActiveUserLocation] = useState<{ latitude: number; longitude: number } | null>(null)
  const [selectedPlaceId, setSelectedPlaceId] = useState<string | null>(null)
  const [hoveredPlaceId, setHoveredPlaceId] = useState<string | null>(null)
  const [aiResponse, setAiResponse] = useState<string | null>(null)
  const [isQuerying, setIsQuerying] = useState(false)
  const [mobileMapRatio, setMobileMapRatio] = useState(100)

  return (
    <MapContext.Provider
      value={{
        activePlaces,
        activeUserLocation,
        selectedPlaceId,
        hoveredPlaceId,
        aiResponse,
        isQuerying,
        mobileMapRatio,
        setActivePlaces,
        setActiveUserLocation,
        setSelectedPlaceId,
        setHoveredPlaceId,
        setAiResponse,
        setIsQuerying,
        setMobileMapRatio,
      }}
    >
      {children}
    </MapContext.Provider>
  )
}

export function useMapContext() {
  const context = useContext(MapContext)
  if (!context) {
    throw new Error('useMapContext must be used within a MapProvider')
  }
  return context
}

export default MapContext
