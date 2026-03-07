'use client'

import { FiMapPin, FiClock, FiPhone, FiExternalLink, FiNavigation, FiStar, FiUsers } from 'react-icons/fi'
import type { Place } from '@/components/Chat/interface'

interface PlaceCardProps {
  place: Place
  isSelected?: boolean
  onClick?: () => void
}

function getDirectionsUrl(place: Place): string {
  if (place.google_maps_url) return place.google_maps_url
  return `https://www.google.com/maps/dir/?api=1&destination=${place.latitude},${place.longitude}`
}

export default function PlaceCard({ place, isSelected, onClick }: PlaceCardProps) {
  return (
    <div
      onClick={onClick}
      className={`flex-shrink-0 w-72 rounded-lg border cursor-pointer transition-all ${
        isSelected
          ? 'border-blue-500 shadow-lg ring-2 ring-blue-200'
          : 'border-gray-200 shadow-sm hover:shadow-md'
      }`}
      style={{ backgroundColor: 'var(--color-background, #fff)' }}
    >
      {/* Photo or placeholder */}
      {place.photo_url ? (
        <img
          src={place.photo_url}
          alt={place.name}
          className="w-full h-32 object-cover rounded-t-lg"
        />
      ) : (
        <div className="w-full h-20 rounded-t-lg bg-gradient-to-r from-blue-100 to-green-100 flex items-center justify-center">
          <FiMapPin className="size-8 text-gray-400" />
        </div>
      )}

      <div className="p-3 space-y-2">
        {/* Name + Rating */}
        <div className="flex items-start justify-between gap-2">
          <h4 className="font-semibold text-sm leading-tight line-clamp-2">{place.name}</h4>
          {place.rating != null && (
            <span className="flex items-center gap-0.5 text-xs text-amber-600 flex-shrink-0">
              <FiStar className="size-3 fill-amber-500" />
              {place.rating}
            </span>
          )}
        </div>

        {/* Address */}
        {place.address && (
          <p className="text-xs text-gray-500 line-clamp-2">{place.address}</p>
        )}

        {/* Badges row */}
        <div className="flex flex-wrap gap-1.5">
          {place.travel_time_min != null && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 text-xs">
              <FiClock className="size-3" />
              {place.travel_time_min.toFixed(0)} min
            </span>
          )}

          {place.open_now != null && (
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${
              place.open_now ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
            }`}>
              {place.open_now ? 'Open' : 'Closed'}
            </span>
          )}

          {place.occupancy != null && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 text-xs">
              <FiUsers className="size-3" />
              {place.occupancy}x busy
            </span>
          )}

          {place.overall_service_time_min != null && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 text-xs">
              <FiClock className="size-3" />
              ~{place.overall_service_time_min.toFixed(0)} min total
            </span>
          )}
        </div>

        {/* IoT: opening hours */}
        {place.opening_hours && (
          <p className="text-xs text-gray-500">{place.opening_hours}</p>
        )}

        {/* IoT: about */}
        {place.about && (
          <p className="text-xs text-gray-400 line-clamp-2">{place.about}</p>
        )}

        {/* Google Maps: phone / website */}
        {(place.phone || place.website) && (
          <div className="flex flex-wrap gap-2 text-xs text-gray-500">
            {place.phone && (
              <a href={`tel:${place.phone}`} className="inline-flex items-center gap-1 hover:text-blue-600">
                <FiPhone className="size-3" />
                {place.phone}
              </a>
            )}
            {place.website && (
              <a href={place.website} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 hover:text-blue-600">
                <FiExternalLink className="size-3" />
                Website
              </a>
            )}
          </div>
        )}

        {/* Get Directions */}
        <a
          href={getDirectionsUrl(place)}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-blue-600 text-white text-xs font-medium hover:bg-blue-700 transition-colors w-full justify-center"
          onClick={(e) => e.stopPropagation()}
        >
          <FiNavigation className="size-3" />
          Get Directions
        </a>
      </div>
    </div>
  )
}
