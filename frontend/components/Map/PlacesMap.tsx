'use client'

import { useRef, useCallback, useEffect, useState } from 'react'
import Map, { Marker, Popup, NavigationControl } from 'react-map-gl/mapbox'
import type { MapRef } from 'react-map-gl/mapbox'
import type { Place } from '@/components/Chat/interface'
import { MdMyLocation } from 'react-icons/md'
import { useTheme } from '@/components/Themes'

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || ''

interface PlacesMapProps {
  places: Place[]
  userLocation?: { latitude: number; longitude: number } | null
  selectedPlaceId?: string | null
  hoveredPlaceId?: string | null
  onMarkerClick?: (id: string) => void
  onMarkerHover?: (id: string | null) => void
  isExplorer?: boolean
}

function NeonMarker({
  place,
  index,
  isSelected,
  isHovered,
}: {
  place: Place
  index: number
  isSelected: boolean
  isHovered: boolean
}) {
  const isIoT = place.source === 'iot_engine'
  const baseColor = isSelected ? '#f472b6' : isIoT ? '#34d399' : '#22d3ee'
  const scale = isSelected || isHovered ? 1.2 : 1

  return (
    <div className="relative" style={{ transform: `scale(${scale})`, transition: 'transform 0.2s ease' }}>
      {/* Pulse ring */}
      {(isIoT || isSelected) && (
        <div
          className="absolute inset-0 rounded-full animate-live-pulse"
          style={{
            width: 36,
            height: 36,
            top: -6,
            left: -6,
            backgroundColor: `${baseColor}20`,
            border: `1px solid ${baseColor}40`,
          }}
        />
      )}
      {/* Marker body */}
      <svg width="24" height="36" viewBox="0 0 24 36">
        <defs>
          <filter id={`glow-${place.id}`}>
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path
          d="M12 0C5.4 0 0 5.4 0 12C0 21 12 36 12 36S24 21 24 12C24 5.4 18.6 0 12 0Z"
          fill={baseColor}
          fillOpacity={0.9}
          filter={`url(#glow-${place.id})`}
        />
        <circle cx="12" cy="12" r="8" fill="rgba(0,0,0,0.4)" />
        <text
          x="12"
          y="16"
          textAnchor="middle"
          fill="white"
          fontSize="10"
          fontWeight="bold"
          fontFamily="system-ui"
        >
          {index}
        </text>
      </svg>
    </div>
  )
}

export default function PlacesMap({
  places,
  userLocation,
  selectedPlaceId,
  hoveredPlaceId,
  onMarkerClick,
  onMarkerHover,
  isExplorer = false,
}: PlacesMapProps) {
  const mapRef = useRef<MapRef>(null)
  const [popupPlace, setPopupPlace] = useState<Place | null>(null)
  const { resolvedTheme } = useTheme()
  const isDark = resolvedTheme === 'dark'

  const fitBounds = useCallback(() => {
    const map = mapRef.current
    if (!map) return

    const points = places
      .filter((p) => p.latitude != null && p.longitude != null)
      .map((p) => [p.longitude, p.latitude] as [number, number])

    if (userLocation) {
      points.push([userLocation.longitude, userLocation.latitude])
    }

    if (points.length === 0) return

    if (points.length === 1) {
      map.flyTo({ center: points[0], zoom: 18, pitch: isExplorer ? 60 : 45 })
      return
    }

    const lngs = points.map((p) => p[0])
    const lats = points.map((p) => p[1])
    const bounds: [[number, number], [number, number]] = [
      [Math.min(...lngs), Math.min(...lats)],
      [Math.max(...lngs), Math.max(...lats)],
    ]
    map.fitBounds(bounds, {
      padding: isExplorer ? { top: 40, bottom: 40, left: 30, right: 30 } : 40,
      maxZoom: 14,
    })
  }, [places, userLocation, isExplorer])

  useEffect(() => {
    fitBounds()
  }, [fitBounds])

  // flyTo on selection
  useEffect(() => {
  if (!selectedPlaceId || !mapRef.current || !isExplorer) return
  const place = places.find((p) => p.id === selectedPlaceId)
  if (place && place.latitude != null && place.longitude != null) {
    const isMobile = window.innerWidth < 768
    const yOffset = isMobile ? window.innerHeight * 0.22 : 0

    mapRef.current.flyTo({
      center: [place.longitude, place.latitude],
      zoom: 16,
      pitch: 60,
      duration: 1000,
      offset: [0, yOffset],
    })
  }
}, [selectedPlaceId, places, isExplorer])

  // Update map style when theme changes
  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map || !isExplorer) return
    map.setConfigProperty('basemap', 'lightPreset', isDark ? 'night' : 'day')
    if (isDark) {
      map.setFog({
        color: '#070810',
        'high-color': '#070810',
        'horizon-blend': 0.1,
        'space-color': '#070810',
        'star-intensity': 0.3,
      } as any)
    } else {
      map.setFog(null as any)
    }
  }, [isDark, isExplorer])

  const hasPlaces = places.length > 0 && places[0].latitude != null
  const isReady = userLocation || hasPlaces

  // Show loading skeleton until we have a location to center on
  if (!isReady) {
    return (
      <div
        className="flex items-center justify-center bg-gray-200 dark:bg-gray-900/50 animate-pulse"
        style={{
          width: '100%',
          height: '100%',
          ...(isExplorer ? {} : { borderRadius: '8px' }),
        }}
      >
        <div className="flex flex-col items-center gap-2 text-gray-500 dark:text-gray-400">
          <MdMyLocation className="size-6 animate-spin" />
          <span className="text-sm">Getting your location...</span>
        </div>
      </div>
    )
  }

  const initialCenter = userLocation
    ? { longitude: userLocation.longitude, latitude: userLocation.latitude }
    : { longitude: places[0].longitude, latitude: places[0].latitude }

  // Use standard style for both — explorer gets night preset for dark + 3D buildings
  const mapStyle = 'mapbox://styles/mapbox/standard'

  return (
    <Map
      ref={mapRef}
      mapboxAccessToken={MAPBOX_TOKEN}
      initialViewState={{
        ...initialCenter,
        zoom: 13,
        pitch: isExplorer ? 60 : 45,
      }}
      style={{
        width: '100%',
        height: '100%',
        ...(isExplorer ? {} : { borderRadius: '8px' }),
      }}
      mapStyle={mapStyle}
      onLoad={(e) => {
        fitBounds()
        e.target.setConfigProperty('basemap', 'show3dObjects', true)
        if (isExplorer) {
          e.target.setConfigProperty('basemap', 'lightPreset', isDark ? 'night' : 'day')
          if (isDark) {
            e.target.setFog({
              color: '#070810',
              'high-color': '#070810',
              'horizon-blend': 0.1,
              'space-color': '#070810',
              'star-intensity': 0.3,
            } as any)
          } else {
            e.target.setFog(null as any)
          }
        }
      }}
      scrollZoom={isExplorer}
      pitch={isExplorer ? 60 : 45}
    >
      <NavigationControl position="top-right" />

      {/* Recenter on my location button */}
      {userLocation && (
        <div className="absolute bottom-6 right-2.5 z-10">
          <button
            onClick={() => {
              mapRef.current?.flyTo({
                center: [userLocation.longitude, userLocation.latitude],
                zoom: 18,
                pitch: isExplorer ? 60 : 45,
              })
            }}
            className="bg-white rounded-md shadow-md p-1.5 hover:bg-gray-100 transition-colors"
            title="Center on my location"
          >
            <MdMyLocation className="size-5 text-gray-700" />
          </button>
        </div>
      )}

      {/* User location marker */}
      {userLocation && (
        <Marker longitude={userLocation.longitude} latitude={userLocation.latitude} anchor="center">
          {isExplorer ? (
            <div className="relative">
              <div className="absolute -inset-3 rounded-full bg-blue-500/20 animate-live-pulse" />
              <div
                style={{
                  width: 14,
                  height: 14,
                  backgroundColor: '#3b82f6',
                  border: '2px solid #93c5fd',
                  borderRadius: '50%',
                  boxShadow: '0 0 12px rgba(59,130,246,0.5)',
                }}
              />
            </div>
          ) : (
            <div
              style={{
                width: 16,
                height: 16,
                backgroundColor: '#3b82f6',
                border: '3px solid white',
                borderRadius: '50%',
                boxShadow: '0 0 0 2px #3b82f6',
              }}
            />
          )}
        </Marker>
      )}

      {/* Place markers */}
      {places.map((place, index) => {
        if (place.latitude == null || place.longitude == null) return null
        const isSelected = selectedPlaceId === place.id
        const isHovered = hoveredPlaceId === place.id

        return (
          <Marker
            key={place.id}
            longitude={place.longitude}
            latitude={place.latitude}
            anchor="bottom"
            onClick={(e) => {
              e.originalEvent.stopPropagation()
              onMarkerClick?.(place.id)
              if (!isExplorer) setPopupPlace(place)
            }}
          >
            {isExplorer ? (
              <div
                onMouseEnter={() => onMarkerHover?.(place.id)}
                onMouseLeave={() => onMarkerHover?.(null)}
              >
                <NeonMarker
                  place={place}
                  index={index + 1}
                  isSelected={isSelected}
                  isHovered={isHovered}
                />
              </div>
            ) : (
              <svg width="25" height="41" viewBox="0 0 25 41">
                <path
                  d="M12.5 0C5.6 0 0 5.6 0 12.5C0 21.9 12.5 41 12.5 41S25 21.9 25 12.5C25 5.6 19.4 0 12.5 0Z"
                  fill={isSelected ? '#ef4444' : '#3b82f6'}
                />
                <circle cx="12.5" cy="12.5" r="5" fill="white" />
              </svg>
            )}
          </Marker>
        )
      })}

      {/* Popup for non-explorer mode */}
      {!isExplorer && popupPlace && popupPlace.latitude != null && popupPlace.longitude != null && (
        <Popup
          longitude={popupPlace.longitude}
          latitude={popupPlace.latitude}
          anchor="bottom"
          offset={[0, -41]}
          onClose={() => setPopupPlace(null)}
          closeOnClick={false}
        >
          <strong>{popupPlace.name}</strong>
          {popupPlace.address && <br />}
          {popupPlace.address}
        </Popup>
      )}
    </Map>
  )
}
