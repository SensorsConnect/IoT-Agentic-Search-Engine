'use client'

import { FiMapPin, FiClock, FiPhone, FiExternalLink, FiNavigation, FiStar } from 'react-icons/fi'
import type { Place } from '@/components/Chat/interface'

interface PlaceCardProps {
  place: Place
  isSelected?: boolean
  isHovered?: boolean
  onClick?: () => void
  variant?: 'light' | 'dark'
  index?: number
}

function getDirectionsUrl(place: Place): string {
  if (place.latitude != null && place.longitude != null) {
    const dest = `${place.latitude},${place.longitude}`
    const name = place.name ? `&destination_place_name=${encodeURIComponent(place.name)}` : ''
    return `https://www.google.com/maps/dir/?api=1&destination=${dest}${name}`
  }
  if (place.google_maps_url) return place.google_maps_url
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.name)}`
}

function OccupancyMini({ occupancy }: { occupancy: number }) {
  const pct = Math.min(occupancy * 100, 100)
  const color = pct <= 30 ? 'bg-neon-green' : pct <= 70 ? 'bg-neon-amber' : 'bg-neon-red'

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-gray-200 dark:bg-white/10 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full animate-fill-bar`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">{(occupancy * 100).toFixed(0)}%</span>
    </div>
  )
}

export default function PlaceCard({ place, isSelected, isHovered, onClick, variant = 'light', index }: PlaceCardProps) {
  const isDark = variant === 'dark'
  const isIoT = place.source === 'iot_engine'

  if (isDark) {
    return (
      <div
        onClick={onClick}
        className={`flex-shrink-0 w-80 rounded-2xl border cursor-pointer transition-all duration-200 ${
          isSelected
            ? 'border-neon-cyan/50 ring-1 ring-neon-cyan/20 scale-[1.02]'
            : isHovered
              ? 'border-white/20 -translate-y-1 shadow-[0_0_20px_rgba(34,211,238,0.1)]'
              : 'border-white/10 hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(34,211,238,0.1)]'
        } bg-surface/90 backdrop-blur-md`}
      >
        {/* Photo or placeholder */}
        {place.photo_url ? (
          <div className="relative">
            <img src={place.photo_url} alt={place.name} className="w-full h-32 object-cover rounded-t-2xl" />
            {index && (
              <span className="absolute top-2 left-2 w-6 h-6 rounded-full bg-surface/80 backdrop-blur-sm text-xs font-bold text-gray-200 flex items-center justify-center border border-white/10">
                {index}
              </span>
            )}
            {isIoT && (
              <span className="absolute top-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-neon-green/10 backdrop-blur-sm border border-neon-green/20 text-neon-green text-[10px] font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-live-pulse" />
                LIVE
              </span>
            )}
          </div>
        ) : (
          <div className="relative w-full h-20 rounded-t-2xl bg-gradient-to-br from-neon-cyan/5 to-neon-purple/5 flex items-center justify-center">
            <FiMapPin className="size-6 text-gray-600" />
            {index && (
              <span className="absolute top-2 left-2 w-6 h-6 rounded-full bg-surface/80 backdrop-blur-sm text-xs font-bold text-gray-200 flex items-center justify-center border border-white/10">
                {index}
              </span>
            )}
            {isIoT && (
              <span className="absolute top-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-neon-green/10 backdrop-blur-sm border border-neon-green/20 text-neon-green text-[10px] font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-live-pulse" />
                LIVE
              </span>
            )}
          </div>
        )}

        <div className="p-3 space-y-2">
          {/* Name + Rating */}
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-semibold text-sm leading-tight line-clamp-2 text-gray-200">{place.name}</h4>
            {place.rating != null && (
              <span className="flex items-center gap-0.5 text-xs text-neon-amber flex-shrink-0">
                <FiStar className="size-3 fill-neon-amber" />
                {place.rating}
              </span>
            )}
          </div>

          {/* Address */}
          {place.address && (
            <p className="text-xs text-gray-500 line-clamp-1">{place.address}</p>
          )}

          {/* Badges */}
          <div className="flex flex-wrap gap-1.5">
            {place.travel_time_min != null && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-neon-cyan/10 text-neon-cyan text-xs">
                <FiClock className="size-3" />
                {place.travel_time_min.toFixed(0)} min
              </span>
            )}
            {place.open_now != null && (
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${
                place.open_now ? 'bg-neon-green/10 text-neon-green' : 'bg-neon-red/10 text-neon-red'
              }`}>
                {place.open_now ? 'Open' : 'Closed'}
              </span>
            )}
          </div>

          {/* Occupancy bar */}
          {place.occupancy != null && <OccupancyMini occupancy={place.occupancy} />}

          {/* Service time */}
          {place.overall_service_time_min != null && (
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <FiClock className="size-3 text-neon-amber" />
              ~{place.overall_service_time_min.toFixed(0)} min service
            </div>
          )}

          {/* Phone & Website */}
          {(place.phone || place.website) && (
            <div className="flex flex-wrap gap-2 text-xs text-gray-400">
              {place.phone && (
                <a href={`tel:${place.phone}`} className="inline-flex items-center gap-1 hover:text-neon-cyan transition-colors">
                  <FiPhone className="size-3" />
                  {place.phone}
                </a>
              )}
              {place.website && (
                <a href={place.website} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 hover:text-neon-cyan transition-colors">
                  <FiExternalLink className="size-3" />
                  Website
                </a>
              )}
            </div>
          )}

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

  // Light variant — matches dark-variant geometry, light-mode palette
  return (
    <div
      onClick={onClick}
      className={`flex-shrink-0 w-80 rounded-2xl border cursor-pointer transition-all duration-200 ${
        isSelected
          ? 'border-blue-500/50 ring-1 ring-blue-200 scale-[1.02]'
          : isHovered
            ? 'border-gray-300 -translate-y-1 shadow-md'
            : 'border-gray-200 shadow-sm hover:-translate-y-1 hover:shadow-md'
      }`}
      style={{ backgroundColor: 'var(--color-background, #fff)' }}
    >
      {/* Photo or placeholder */}
      {place.photo_url ? (
        <div className="relative">
          <img src={place.photo_url} alt={place.name} className="w-full h-32 object-cover rounded-t-2xl" />
          {index && (
            <span className="absolute top-2 left-2 w-6 h-6 rounded-full bg-white/85 backdrop-blur-sm text-xs font-bold text-gray-700 flex items-center justify-center border border-gray-200">
              {index}
            </span>
          )}
          {isIoT && (
            <span className="absolute top-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-50 backdrop-blur-sm border border-green-200 text-green-700 text-[10px] font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-live-pulse" />
              LIVE
            </span>
          )}
        </div>
      ) : (
        <div className="relative w-full h-20 rounded-t-2xl bg-gradient-to-r from-blue-100 to-green-100 flex items-center justify-center">
          <FiMapPin className="size-6 text-gray-400" />
          {index && (
            <span className="absolute top-2 left-2 w-6 h-6 rounded-full bg-white/85 backdrop-blur-sm text-xs font-bold text-gray-700 flex items-center justify-center border border-gray-200">
              {index}
            </span>
          )}
          {isIoT && (
            <span className="absolute top-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-50 backdrop-blur-sm border border-green-200 text-green-700 text-[10px] font-medium">
              <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-live-pulse" />
              LIVE
            </span>
          )}
        </div>
      )}

      <div className="p-3 space-y-2">
        {/* Name + Rating */}
        <div className="flex items-start justify-between gap-2">
          <h4 className="font-semibold text-sm leading-tight line-clamp-2 text-gray-900">{place.name}</h4>
          {place.rating != null && (
            <span className="flex items-center gap-0.5 text-xs text-amber-600 flex-shrink-0">
              <FiStar className="size-3 fill-amber-500" />
              {place.rating}
            </span>
          )}
        </div>

        {/* Address */}
        {place.address && (
          <p className="text-xs text-gray-500 line-clamp-1">{place.address}</p>
        )}

        {/* Badges */}
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
        </div>

        {/* Occupancy bar */}
        {place.occupancy != null && <OccupancyMini occupancy={place.occupancy} />}

        {/* Service time */}
        {place.overall_service_time_min != null && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <FiClock className="size-3 text-amber-500" />
            ~{place.overall_service_time_min.toFixed(0)} min service
          </div>
        )}

        {/* Phone & Website */}
        {(place.phone || place.website) && (
          <div className="flex flex-wrap gap-2 text-xs text-gray-500">
            {place.phone && (
              <a href={`tel:${place.phone}`} className="inline-flex items-center gap-1 hover:text-blue-600 transition-colors">
                <FiPhone className="size-3" />
                {place.phone}
              </a>
            )}
            {place.website && (
              <a href={place.website} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 hover:text-blue-600 transition-colors">
                <FiExternalLink className="size-3" />
                Website
              </a>
            )}
          </div>
        )}

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
