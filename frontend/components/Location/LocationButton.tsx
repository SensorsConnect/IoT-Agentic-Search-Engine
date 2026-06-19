'use client'

import { useState } from 'react'
import { IconButton, Tooltip, Flex } from '@radix-ui/themes'
import { AiOutlineEnvironment, AiOutlineLoading3Quarters, AiOutlineClose } from 'react-icons/ai'
import { MdGpsFixed, MdGpsNotFixed } from 'react-icons/md'
import { useLocation } from './LocationContext'

interface LocationButtonProps {
  onLocationChange?: (location: { latitude: number; longitude: number } | null) => void
}

const LocationButton = ({ onLocationChange }: LocationButtonProps) => {
  const { location, isLoading, requestLocation, clearLocation, permission, isSupported } = useLocation()
  const [showStatus, setShowStatus] = useState(false)

  const isGPS = location?.source === 'gps'
  const hasLocation = !!(location?.latitude && location?.longitude)

  const handleClick = async () => {
    if (isGPS) {
      // Already on GPS — clear and fall back to IP
      clearLocation()
      onLocationChange?.(null)
      setShowStatus(true)
      setTimeout(() => setShowStatus(false), 2000)
    } else {
      // Upgrade from IP/cached to GPS — triggers browser prompt
      const newLocation = await requestLocation()
      if (newLocation?.latitude && newLocation?.longitude) {
        onLocationChange?.({ latitude: newLocation.latitude, longitude: newLocation.longitude })
      } else {
        onLocationChange?.(null)
      }
      setShowStatus(true)
      setTimeout(() => setShowStatus(false), 2000)
    }
  }

  const getTooltipContent = () => {
    if (!isSupported) return 'Location not supported'
    if (isLoading) return 'Getting location...'
    if (permission === 'denied') return 'Location access denied'
    if (isGPS) return 'Using precise GPS — click to clear'
    if (hasLocation) return 'Using approximate location — click for precise GPS'
    return 'Use precise location'
  }

  const getButtonColor = () => {
    if (isGPS) return 'green'
    if (hasLocation) return 'blue'
    if (permission === 'denied') return 'red'
    return 'gray'
  }

  return (
    <Flex align="center" gap="2">
      <Tooltip content={getTooltipContent()}>
        <IconButton
          variant="soft"
          color={getButtonColor()}
          size="2"
          className="rounded-xl cursor-pointer"
          disabled={!isSupported || isLoading}
          onClick={handleClick}
        >
          {isLoading ? (
            <AiOutlineLoading3Quarters className="size-4 animate-spin" />
          ) : isGPS ? (
            <MdGpsFixed className="size-4" />
          ) : hasLocation ? (
            <MdGpsNotFixed className="size-4" />
          ) : permission === 'denied' ? (
            <AiOutlineClose className="size-4" />
          ) : (
            <AiOutlineEnvironment className="size-4" />
          )}
        </IconButton>
      </Tooltip>

      {showStatus && (
        <span className="text-xs text-gray-500">
          {isGPS ? 'Precise GPS active' : hasLocation ? 'Approximate location' : 'Location cleared'}
        </span>
      )}
    </Flex>
  )
}

export default LocationButton
