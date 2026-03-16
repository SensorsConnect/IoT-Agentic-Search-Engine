'use client'

import { useRef, useEffect } from 'react'
import { useMapContext } from './MapContext'
import PlaceCard from '../PlaceCard/PlaceCard'
import { useTheme } from '@/components/Themes'

export default function PlaceCardStrip() {
  const { activePlaces, selectedPlaceId, hoveredPlaceId, setSelectedPlaceId, setHoveredPlaceId } = useMapContext()
  const { resolvedTheme } = useTheme()
  const cardVariant = resolvedTheme === 'dark' ? 'dark' : 'light'
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!selectedPlaceId || !scrollRef.current) return
    const card = scrollRef.current.querySelector(`[data-place-id="${selectedPlaceId}"]`)
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
    }
  }, [selectedPlaceId])

  if (activePlaces.length === 0) return null

  return (
    <div className="absolute bottom-0 left-0 right-0 z-10 hidden md:block">
      {/* Gradient fade at top */}
      <div className="bg-gradient-to-t from-white/60 dark:from-black/40 via-white/30 dark:via-black/20 to-transparent pt-16 pb-4 px-4">
        <div
          ref={scrollRef}
          className="flex gap-3 overflow-x-auto snap-x snap-mandatory dark-scrollbar pb-2"
        >
          {activePlaces.map((place, index) => (
            <div
              key={place.id}
              data-place-id={place.id}
              className="snap-start flex-shrink-0"
              style={{ animation: `cardEntrance 0.4s ease-out ${index * 75}ms both` }}
              onMouseEnter={() => setHoveredPlaceId(place.id)}
              onMouseLeave={() => setHoveredPlaceId(null)}
            >
              <PlaceCard
                place={place}
                isSelected={selectedPlaceId === place.id}
                isHovered={hoveredPlaceId === place.id}
                onClick={() => setSelectedPlaceId(place.id)}
                variant={cardVariant}
                index={index + 1}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
