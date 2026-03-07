'use client'

import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet'
import L from 'leaflet'
import type { Place } from '@/components/Chat/interface'

// Fix default marker icons for webpack/Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const selectedIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const defaultIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

interface FitBoundsProps {
  places: Place[]
  userLocation?: { latitude: number; longitude: number } | null
}

function FitBounds({ places, userLocation }: FitBoundsProps) {
  const map = useMap()

  useEffect(() => {
    const points: L.LatLngExpression[] = places
      .filter((p) => p.latitude != null && p.longitude != null)
      .map((p) => [p.latitude, p.longitude])

    if (userLocation) {
      points.push([userLocation.latitude, userLocation.longitude])
    }

    if (points.length > 0) {
      const bounds = L.latLngBounds(points)
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 })
    }
  }, [places, userLocation, map])

  return null
}

interface PlacesMapProps {
  places: Place[]
  userLocation?: { latitude: number; longitude: number } | null
  selectedPlaceId?: string | null
  onMarkerClick?: (id: string) => void
}

export default function PlacesMap({ places, userLocation, selectedPlaceId, onMarkerClick }: PlacesMapProps) {
  const center: L.LatLngExpression = userLocation
    ? [userLocation.latitude, userLocation.longitude]
    : places.length > 0
      ? [places[0].latitude, places[0].longitude]
      : [43.65, -79.38]

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: '100%', width: '100%', borderRadius: '8px' }}
      scrollWheelZoom={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <FitBounds places={places} userLocation={userLocation} />

      {userLocation && (
        <CircleMarker
          center={[userLocation.latitude, userLocation.longitude]}
          radius={8}
          pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.8 }}
        >
          <Popup>Your location</Popup>
        </CircleMarker>
      )}

      {places.map((place) => {
        if (place.latitude == null || place.longitude == null) return null
        const isSelected = selectedPlaceId === place.id
        return (
          <Marker
            key={place.id}
            position={[place.latitude, place.longitude]}
            icon={isSelected ? selectedIcon : defaultIcon}
            eventHandlers={{
              click: () => onMarkerClick?.(place.id),
            }}
          >
            <Popup>
              <strong>{place.name}</strong>
              {place.address && <br />}
              {place.address}
            </Popup>
          </Marker>
        )
      })}
    </MapContainer>
  )
}
