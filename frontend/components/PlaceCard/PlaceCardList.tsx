'use client'

import { useEffect, useRef } from 'react'
import PlaceCard from './PlaceCard'
import type { Place } from '@/components/Chat/interface'

interface PlaceCardListProps {
  places: Place[]
  selectedPlaceId?: string | null
  onCardClick?: (id: string) => void
}

export default function PlaceCardList({ places, selectedPlaceId, onCardClick }: PlaceCardListProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!selectedPlaceId || !scrollRef.current) return
    const card = scrollRef.current.querySelector(`[data-place-id="${selectedPlaceId}"]`)
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
    }
  }, [selectedPlaceId])

  return (
    <div
      ref={scrollRef}
      className="flex gap-3 overflow-x-auto pb-2 md:flex-row flex-col md:flex-nowrap"
      style={{ scrollbarWidth: 'thin' }}
    >
      {places.map((place) => (
        <div key={place.id} data-place-id={place.id}>
          <PlaceCard
            place={place}
            isSelected={selectedPlaceId === place.id}
            onClick={() => onCardClick?.(place.id)}
          />
        </div>
      ))}
    </div>
  )
}
