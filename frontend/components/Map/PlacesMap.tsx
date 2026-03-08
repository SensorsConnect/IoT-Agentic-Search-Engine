'use client'

import { useRef, useCallback, useEffect, useState } from 'react'
import Map, { Marker, Popup, NavigationControl } from 'react-map-gl/mapbox'
import type { MapRef } from 'react-map-gl/mapbox'
import type { Place } from '@/components/Chat/interface'

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || ''

interface PlacesMapProps {
  places: Place[]
  userLocation?: { latitude: number; longitude: number } | null
  selectedPlaceId?: string | null
  onMarkerClick?: (id: string) => void
}

export default function PlacesMap({ places, userLocation, selectedPlaceId, onMarkerClick }: PlacesMapProps) {
  const mapRef = useRef<MapRef>(null)
  const [popupPlace, setPopupPlace] = useState<Place | null>(null)

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
      map.flyTo({ center: points[0], zoom: 14 })
      return
    }

    const lngs = points.map((p) => p[0])
    const lats = points.map((p) => p[1])
    const bounds: [[number, number], [number, number]] = [
      [Math.min(...lngs), Math.min(...lats)],
      [Math.max(...lngs), Math.max(...lats)],
    ]
    map.fitBounds(bounds, { padding: 40, maxZoom: 14 })
  }, [places, userLocation])

  useEffect(() => {
    fitBounds()
  }, [fitBounds])

  const initialCenter = userLocation
    ? { longitude: userLocation.longitude, latitude: userLocation.latitude }
    : places.length > 0 && places[0].latitude != null
      ? { longitude: places[0].longitude, latitude: places[0].latitude }
      : { longitude: -79.38, latitude: 43.65 }

  return (
    <Map
      ref={mapRef}
      mapboxAccessToken={MAPBOX_TOKEN}
      initialViewState={{
        ...initialCenter,
        zoom: 13,
      }}
      style={{ width: '100%', height: '100%', borderRadius: '8px' }}
      mapStyle="mapbox://styles/mapbox/standard"
      onLoad={(e) => {
        fitBounds()
        e.target.setConfigProperty('basemap', 'show3dObjects', true)
      }}
      scrollZoom={false}
      pitch={45}
    >
      <NavigationControl position="top-right" />

      {userLocation && (
        <Marker longitude={userLocation.longitude} latitude={userLocation.latitude} anchor="center">
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
        </Marker>
      )}

      {places.map((place) => {
        if (place.latitude == null || place.longitude == null) return null
        const isSelected = selectedPlaceId === place.id
        return (
          <Marker
            key={place.id}
            longitude={place.longitude}
            latitude={place.latitude}
            anchor="bottom"
            onClick={(e) => {
              e.originalEvent.stopPropagation()
              onMarkerClick?.(place.id)
              setPopupPlace(place)
            }}
          >
            <svg width="25" height="41" viewBox="0 0 25 41">
              <path
                d="M12.5 0C5.6 0 0 5.6 0 12.5C0 21.9 12.5 41 12.5 41S25 21.9 25 12.5C25 5.6 19.4 0 12.5 0Z"
                fill={isSelected ? '#ef4444' : '#3b82f6'}
              />
              <circle cx="12.5" cy="12.5" r="5" fill="white" />
            </svg>
          </Marker>
        )
      })}

      {popupPlace && popupPlace.latitude != null && popupPlace.longitude != null && (
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
