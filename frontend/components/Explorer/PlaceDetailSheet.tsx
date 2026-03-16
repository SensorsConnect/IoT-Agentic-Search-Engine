'use client'

import { FiX, FiMapPin, FiClock, FiPhone, FiNavigation, FiStar, FiExternalLink } from 'react-icons/fi'
import { useMapContext } from './MapContext'
import type { Place } from '@/components/Chat/interface'

function getDirectionsUrl(place: Place): string {
  if (place.latitude != null && place.longitude != null) {
    const dest = `${place.latitude},${place.longitude}`
    const name = place.name ? `&destination_place_name=${encodeURIComponent(place.name)}` : ''
    return `https://www.google.com/maps/dir/?api=1&destination=${dest}${name}`
  }
  if (place.google_maps_url) return place.google_maps_url
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.name)}`
}

function OccupancyBar({ occupancy }: { occupancy: number }) {
  const pct = Math.min(occupancy * 100, 100)
  const color = pct <= 30 ? 'bg-neon-green' : pct <= 70 ? 'bg-neon-amber' : 'bg-neon-red'
  const label = pct <= 30 ? 'Low' : pct <= 70 ? 'Moderate' : 'High'

  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-400">Occupancy</span>
        <span className="text-gray-700 dark:text-gray-300">{label} ({(occupancy * 100).toFixed(0)}%)</span>
      </div>
      <div className="h-2 bg-gray-100 dark:bg-white/5 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full animate-fill-bar`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function ServiceTimeGauge({ minutes }: { minutes: number }) {
  const radius = 28
  const circumference = 2 * Math.PI * radius
  const maxMinutes = 60
  const progress = Math.min(minutes / maxMinutes, 1)
  const offset = circumference * (1 - progress)

  return (
    <div className="flex items-center gap-3">
      <svg width="72" height="72" viewBox="0 0 72 72">
        <circle cx="36" cy="36" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="4" />
        <circle
          cx="36" cy="36" r={radius} fill="none"
          stroke="#fbbf24" strokeWidth="4"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 36 36)"
          className="transition-all duration-1000"
        />
        <text x="36" y="34" textAnchor="middle" className="fill-gray-700 dark:fill-gray-200 text-xs font-medium">
          {minutes.toFixed(0)}
        </text>
        <text x="36" y="46" textAnchor="middle" className="fill-gray-500 text-[8px]">
          min
        </text>
      </svg>
      <div>
        <p className="text-xs text-gray-400">Est. Service Time</p>
        <p className="text-sm text-gray-700 dark:text-gray-200 font-medium">~{minutes.toFixed(0)} minutes</p>
      </div>
    </div>
  )
}

export default function PlaceDetailSheet() {
  const { activePlaces, selectedPlaceId, setSelectedPlaceId } = useMapContext()

  const place = activePlaces.find((p) => p.id === selectedPlaceId)
  if (!place) return null

  const isIoT = place.source === 'iot_engine'

  return (
    <div className="hidden md:block">
      {/* Backdrop */}
      <div
        className="absolute inset-0 z-25 bg-black/50"
        onClick={() => setSelectedPlaceId(null)}
      />
      {/* Desktop: side panel from right */}
      <div className="absolute inset-auto top-0 right-0 bottom-0 w-[400px] z-30 animate-slide-in-right">
        <div className="h-full bg-white/95 dark:bg-surface/95 backdrop-blur-xl border-l border-gray-200 dark:border-white/10 overflow-y-auto dark-scrollbar">
          {/* Close button */}
          <button
            onClick={() => setSelectedPlaceId(null)}
            className="absolute top-4 right-4 z-10 w-8 h-8 rounded-full bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-white/10 transition-all"
          >
            <FiX className="size-4" />
          </button>

          {/* Photo */}
          {place.photo_url ? (
            <img src={place.photo_url} alt={place.name} className="w-full h-48 object-cover" />
          ) : (
            <div className="w-full h-32 bg-gradient-to-br from-neon-cyan/10 to-neon-purple/10 flex items-center justify-center">
              <FiMapPin className="size-10 text-gray-600" />
            </div>
          )}

          <div className="p-5 space-y-4">
            {/* Name + badges */}
            <div>
              <div className="flex items-start gap-2">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex-1">{place.name}</h2>
                {isIoT && (
                  <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-neon-green/10 border border-neon-green/20 text-neon-green text-xs flex-shrink-0">
                    <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-live-pulse" />
                    LIVE
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 mt-2">
                {place.rating != null && (
                  <span className="flex items-center gap-1 text-sm text-neon-amber">
                    <FiStar className="size-3.5 fill-neon-amber" />
                    {place.rating}
                  </span>
                )}
                {place.open_now != null && (
                  <span className={`text-xs font-medium ${place.open_now ? 'text-neon-green' : 'text-neon-red'}`}>
                    {place.open_now ? 'Open Now' : 'Closed'}
                  </span>
                )}
              </div>
            </div>

            {/* Live Conditions */}
            {(place.occupancy != null || place.overall_service_time_min != null || place.travel_time_min != null) && (
              <div className="bg-gray-50 dark:bg-white/[0.03] rounded-xl p-4 border border-gray-200 dark:border-white/5 space-y-4">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-neon-green animate-live-pulse" />
                  <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Live Conditions</span>
                </div>

                {place.occupancy != null && <OccupancyBar occupancy={place.occupancy} />}

                {place.overall_service_time_min != null && (
                  <ServiceTimeGauge minutes={place.overall_service_time_min} />
                )}

                {place.travel_time_min != null && (
                  <div className="flex items-center gap-2 text-sm">
                    <FiClock className="size-4 text-neon-cyan" />
                    <span className="text-gray-400">Travel time:</span>
                    <span className="text-gray-800 dark:text-gray-200 font-medium">{place.travel_time_min.toFixed(0)} min</span>
                  </div>
                )}
              </div>
            )}

            {/* Address */}
            {place.address && (
              <div className="flex gap-2 text-sm">
                <FiMapPin className="size-4 text-gray-500 mt-0.5 flex-shrink-0" />
                <span className="text-gray-400">{place.address}</span>
              </div>
            )}

            {/* Opening hours */}
            {place.opening_hours && (
              <div className="flex gap-2 text-sm">
                <FiClock className="size-4 text-gray-500 mt-0.5 flex-shrink-0" />
                <span className="text-gray-400">{place.opening_hours}</span>
              </div>
            )}

            {/* About */}
            {place.about && (
              <p className="text-sm text-gray-400 leading-relaxed">{place.about}</p>
            )}

            {/* Contact */}
            {(place.phone || place.website) && (
              <div className="flex flex-wrap gap-2">
                {place.phone && (
                  <a
                    href={`tel:${place.phone}`}
                    className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 text-sm text-gray-600 dark:text-gray-300 hover:border-blue-400/30 dark:hover:border-neon-cyan/30 hover:text-blue-600 dark:hover:text-neon-cyan transition-all"
                  >
                    <FiPhone className="size-3.5" />
                    {place.phone}
                  </a>
                )}
                {place.website && (
                  <a
                    href={place.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-gray-50 dark:bg-white/5 border border-gray-200 dark:border-white/10 text-sm text-gray-600 dark:text-gray-300 hover:border-blue-400/30 dark:hover:border-neon-cyan/30 hover:text-blue-600 dark:hover:text-neon-cyan transition-all"
                  >
                    <FiExternalLink className="size-3.5" />
                    Website
                  </a>
                )}
              </div>
            )}

            {/* Get Directions button */}
            <a
              href={getDirectionsUrl(place)}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl bg-blue-50 dark:bg-neon-cyan/10 border border-blue-200 dark:border-neon-cyan/20 text-blue-600 dark:text-neon-cyan font-medium text-sm hover:bg-blue-100 dark:hover:bg-neon-cyan/20 transition-all"
            >
              <FiNavigation className="size-4" />
              Get Directions
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
