'use client'

import dynamic from 'next/dynamic'
import { useMapContext } from './MapContext'

const PlacesMap = dynamic(() => import('../Map/PlacesMap'), { ssr: false })

export default function MapPanel() {
  const {
    activePlaces,
    activeUserLocation,
    selectedPlaceId,
    hoveredPlaceId,
    setSelectedPlaceId,
    setHoveredPlaceId,
  } = useMapContext()

  return (
    <div className="w-full h-full explorer-map">
      <PlacesMap
        places={activePlaces}
        userLocation={activeUserLocation}
        selectedPlaceId={selectedPlaceId}
        hoveredPlaceId={hoveredPlaceId}
        onMarkerClick={(id) => setSelectedPlaceId(id)}
        onMarkerHover={(id) => setHoveredPlaceId(id)}
        isExplorer
      />
    </div>
  )
}
