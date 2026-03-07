'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import { PlaceCardList } from '@/components/PlaceCard'
import type { Place } from '@/components/Chat/interface'

const PlacesMap = dynamic(() => import('./PlacesMap'), { ssr: false })

interface MapWithCardsProps {
  places: Place[]
  userLocation?: { latitude: number; longitude: number } | null
}

export default function MapWithCards({ places, userLocation }: MapWithCardsProps) {
  const [selectedPlaceId, setSelectedPlaceId] = useState<string | null>(null)

  const handleSelect = (id: string) => {
    setSelectedPlaceId((prev) => (prev === id ? null : id))
  }

  return (
    <div className="mt-3 space-y-3">
      <div className="h-[200px] md:h-[300px] w-full">
        <PlacesMap
          places={places}
          userLocation={userLocation}
          selectedPlaceId={selectedPlaceId}
          onMarkerClick={handleSelect}
        />
      </div>
      <PlaceCardList
        places={places}
        selectedPlaceId={selectedPlaceId}
        onCardClick={handleSelect}
      />
    </div>
  )
}
