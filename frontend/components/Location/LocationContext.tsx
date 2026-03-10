'use client'

import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react'
import { useGeolocated } from 'react-geolocated'

export interface LocationData {
  latitude: number | null
  longitude: number | null
  accuracy: number | null
  timestamp: number
  source: 'gps' | 'network' | 'cached'
}

export interface LocationState {
  location: LocationData | null
  isLoading: boolean
  error: string | null
  permission: PermissionState | null
  isSupported: boolean
}

interface LocationContextType extends LocationState {
  requestLocation: () => Promise<LocationData | null>
  clearLocation: () => void
  setLocation: (location: LocationData) => void
}

const LocationContext = createContext<LocationContextType | undefined>(undefined)

interface LocationProviderProps {
  children: ReactNode
}

export const LocationProvider = ({ children }: LocationProviderProps) => {
  const [location, setLocation] = useState<LocationData | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [permission, setPermission] = useState<PermissionState | null>(null)

  // Promise resolver for requestLocation()
  const resolveRef = useRef<((value: LocationData | null) => void) | null>(null)

  const { coords, isGeolocationAvailable, isGeolocationEnabled, getPosition, positionError } = useGeolocated({
    positionOptions: {
      enableHighAccuracy: false,
      maximumAge: 60000,
      timeout: 10000,
    },
    userDecisionTimeout: 5000,
    watchPosition: false,
    watchLocationPermissionChange: true,
    suppressLocationOnMount: false,
  })

  const isSupported = isGeolocationAvailable

  // Cache location to localStorage
  const cacheLocation = useCallback((locationData: LocationData) => {
    try {
      localStorage.setItem('cached_location', JSON.stringify(locationData))
    } catch (err) {
      console.warn('Failed to cache location:', err)
    }
  }, [])

  // Sync coords from react-geolocated to our state
  useEffect(() => {
    if (coords) {
      const locationData: LocationData = {
        latitude: coords.latitude,
        longitude: coords.longitude,
        accuracy: coords.accuracy,
        timestamp: Date.now(),
        source: 'gps',
      }
      console.log('GPS location detected:', locationData)
      setLocation(locationData)
      cacheLocation(locationData)
      setIsLoading(false)
      setError(null)

      // Resolve any pending requestLocation() promise
      if (resolveRef.current) {
        resolveRef.current(locationData)
        resolveRef.current = null
      }
    }
  }, [coords, cacheLocation])

  // Handle geolocation errors
  useEffect(() => {
    if (positionError) {
      console.warn('Geolocation error:', positionError.message)
      setIsLoading(false)

      if (positionError.code === positionError.PERMISSION_DENIED) {
        setError('Location access denied by user')
        if (resolveRef.current) {
          resolveRef.current(null)
          resolveRef.current = null
        }
      } else {
        // Timeout or position unavailable — fall back to network
        requestNetworkLocation().then((networkResult) => {
          if (resolveRef.current) {
            resolveRef.current(networkResult)
            resolveRef.current = null
          }
        })
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [positionError])

  // Check permissions and load cached location on mount
  useEffect(() => {
    checkPermissions()
    loadCachedLocation()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Derive loading state: loading if geolocation is enabled but we have no coords and no error yet
  useEffect(() => {
    if (!coords && isGeolocationEnabled && !positionError) {
      setIsLoading(true)
    }
  }, [coords, isGeolocationEnabled, positionError])

  const checkPermissions = async () => {
    if ('permissions' in navigator) {
      try {
        const permissionStatus = await navigator.permissions.query({ name: 'geolocation' as PermissionName })
        setPermission(permissionStatus.state)

        permissionStatus.addEventListener('change', () => {
          setPermission(permissionStatus.state)
        })
      } catch (err) {
        console.warn('Permissions API not supported')
      }
    }
  }

  const loadCachedLocation = () => {
    try {
      const cachedLocation = localStorage.getItem('cached_location')
      if (cachedLocation) {
        const locationData = JSON.parse(cachedLocation) as LocationData
        const oneHour = 60 * 60 * 1000
        if (Date.now() - locationData.timestamp < oneHour) {
          console.log('Loaded cached location:', locationData)
          setLocation(locationData)
        } else {
          console.log('Cached location expired, removing...')
          localStorage.removeItem('cached_location')
        }
      }
    } catch (err) {
      console.warn('Failed to load cached location:', err)
    }
  }

  const requestNetworkLocation = async (): Promise<LocationData | null> => {
    setIsLoading(true)
    try {
      console.log('Fetching location from IP address...')
      const response = await fetch('https://ipapi.co/json/')
      if (response.ok) {
        const data = await response.json()
        console.log('IP-based location data:', data)

        const locationData: LocationData = {
          latitude: data.latitude,
          longitude: data.longitude,
          accuracy: null,
          timestamp: Date.now(),
          source: 'network'
        }

        setLocation(locationData)
        cacheLocation(locationData)
        setIsLoading(false)
        return locationData
      } else {
        console.warn('Network location API returned error:', response.status)
      }
    } catch (err) {
      console.warn('Network location failed:', err)
    }

    setIsLoading(false)
    return null
  }

  const requestLocation = async (): Promise<LocationData | null> => {
    if (!isSupported) {
      setError('Geolocation is not supported by this browser')
      return await requestNetworkLocation()
    }

    setIsLoading(true)
    setError(null)

    // If we already have coords from the hook, return them immediately
    if (coords) {
      const locationData: LocationData = {
        latitude: coords.latitude,
        longitude: coords.longitude,
        accuracy: coords.accuracy,
        timestamp: Date.now(),
        source: 'gps',
      }
      setLocation(locationData)
      cacheLocation(locationData)
      setIsLoading(false)
      return locationData
    }

    // Otherwise, trigger a new position request and wait for coords via useEffect
    getPosition()
    return new Promise((resolve) => {
      resolveRef.current = resolve
    })
  }

  const clearLocation = () => {
    console.log('Clearing location from context')
    setLocation(null)
    setError(null)
    localStorage.removeItem('cached_location')
  }

  const handleSetLocation = (locationData: LocationData) => {
    console.log('Setting location in context:', locationData)
    setLocation(locationData)
    cacheLocation(locationData)
  }

  const value: LocationContextType = {
    location,
    isLoading,
    error,
    permission,
    isSupported,
    requestLocation,
    clearLocation,
    setLocation: handleSetLocation
  }

  return <LocationContext.Provider value={value}>{children}</LocationContext.Provider>
}

export const useLocation = (): LocationContextType => {
  const context = useContext(LocationContext)
  if (context === undefined) {
    throw new Error('useLocation must be used within a LocationProvider')
  }
  return context
}

export default LocationContext
