'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import toast from 'react-hot-toast'

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
  const [isSupported, setIsSupported] = useState(false)

  // Check if geolocation is supported
  useEffect(() => {
    const supported = 'geolocation' in navigator
    setIsSupported(supported)
    
    if (supported) {
      checkPermissions()
      // Try to load cached location
      loadCachedLocation()
    }
  }, [])

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
        // Check if cached location is less than 1 hour old
        const oneHour = 60 * 60 * 1000
        if (Date.now() - locationData.timestamp < oneHour) {
          setLocation(locationData)
        } else {
          localStorage.removeItem('cached_location')
        }
      }
    } catch (err) {
      console.warn('Failed to load cached location:', err)
    }
  }

  const cacheLocation = (locationData: LocationData) => {
    try {
      localStorage.setItem('cached_location', JSON.stringify(locationData))
    } catch (err) {
      console.warn('Failed to cache location:', err)
    }
  }

  const requestLocation = async (): Promise<LocationData | null> => {
    if (!isSupported) {
      setError('Geolocation is not supported by this browser')
      toast.error('Location access is not supported on this device')
      return null
    }

    setIsLoading(true)
    setError(null)

    return new Promise((resolve) => {
      const options: PositionOptions = {
        enableHighAccuracy: true, // Try GPS first
        timeout: 15000, // 15 seconds timeout
        maximumAge: 300000 // 5 minutes cache
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const locationData: LocationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: Date.now(),
            source: 'gps'
          }

          setLocation(locationData)
          cacheLocation(locationData)
          setIsLoading(false)
          
          toast.success('Location accessed successfully!')
          resolve(locationData)
        },
        (err) => {
          setIsLoading(false)
          
          let errorMessage = 'Unable to access location'
          
          switch (err.code) {
            case err.PERMISSION_DENIED:
              errorMessage = 'Location access denied by user'
              toast.error('Please enable location access in your browser settings')
              break
            case err.POSITION_UNAVAILABLE:
              errorMessage = 'Location information unavailable'
              // Try network-based location as fallback
              requestNetworkLocation().then(resolve)
              return
            case err.TIMEOUT:
              errorMessage = 'Location request timed out'
              // Try network-based location as fallback
              requestNetworkLocation().then(resolve)
              return
            default:
              errorMessage = `Location error: ${err.message}`
          }
          
          setError(errorMessage)
          console.warn('Geolocation error:', err)
          resolve(null)
        },
        options
      )
    })
  }

  const requestNetworkLocation = async (): Promise<LocationData | null> => {
    try {
      // Try to get location from IP-based services as fallback
      const response = await fetch('https://ipapi.co/json/')
      if (response.ok) {
        const data = await response.json()
        const locationData: LocationData = {
          latitude: data.latitude,
          longitude: data.longitude,
          accuracy: null, // IP-based location has low accuracy
          timestamp: Date.now(),
          source: 'network'
        }
        
        setLocation(locationData)
        cacheLocation(locationData)
        
        toast.success('Location approximated from network')
        return locationData
      }
    } catch (err) {
      console.warn('Network location failed:', err)
    }
    
    return null
  }

  const clearLocation = () => {
    setLocation(null)
    setError(null)
    localStorage.removeItem('cached_location')
  }

  const handleSetLocation = (locationData: LocationData) => {
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
