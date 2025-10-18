'use client'

import { useState } from 'react'
import { IconButton, Tooltip, Flex } from '@radix-ui/themes'
import { AiOutlineEnvironment, AiOutlineLoading3Quarters, AiOutlineClose, AiOutlineCheck } from 'react-icons/ai'
import { useLocation } from './LocationContext'

interface LocationButtonProps {
  onLocationChange?: (location: { latitude: number; longitude: number } | null) => void
}

const LocationButton = ({ onLocationChange }: LocationButtonProps) => {
  const { location, isLoading, requestLocation, clearLocation, permission, isSupported } = useLocation()
  const [showStatus, setShowStatus] = useState(false)

  const handleLocationClick = async () => {
    if (location) {
      clearLocation()
      onLocationChange?.(null)
      setShowStatus(true)
      setTimeout(() => setShowStatus(false), 2000)
    } else {
      const newLocation = await requestLocation()
      if (newLocation && newLocation.latitude && newLocation.longitude) {
        onLocationChange?.({
          latitude: newLocation.latitude,
          longitude: newLocation.longitude
        })
      }
      setShowStatus(true)
      setTimeout(() => setShowStatus(false), 2000)
    }
  }

  const getTooltipContent = () => {
    if (!isSupported) return 'Location not supported'
    if (isLoading) return 'Getting location...'
    if (permission === 'denied') return 'Location access denied'
    if (location) return 'Clear location'
    return 'Share location'
  }

  const getStatusIcon = () => {
    if (location) return <AiOutlineCheck className="size-4 text-green-500" />
    if (isLoading) return <AiOutlineLoading3Quarters className="size-4 animate-spin text-blue-500" />
    if (permission === 'denied') return <AiOutlineClose className="size-4 text-red-500" />
    return <AiOutlineEnvironment className="size-4" />
  }

  const getButtonColor = () => {
    if (location) return 'green'
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
          onClick={handleLocationClick}
        >
          {isLoading ? (
            <AiOutlineLoading3Quarters className="size-4 animate-spin" />
          ) : (
            <AiOutlineEnvironment className="size-4" />
          )}
        </IconButton>
      </Tooltip>
      
      {showStatus && (
        <Flex align="center" gap="1" className="text-sm">
          {getStatusIcon()}
          <span className="text-xs">
            {location ? 'Location shared' : isLoading ? 'Getting location...' : 'Location not shared'}
          </span>
        </Flex>
      )}
      
      {location && location.latitude !== null && location.longitude !== null && (
        <div className="text-xs text-gray-500">
          <div>Lat: {location.latitude.toFixed(4)}</div>
          <div>Lng: {location.longitude.toFixed(4)}</div>
          <div className="capitalize">Via: {location.source}</div>
        </div>
      )}
    </Flex>
  )
}

export default LocationButton
