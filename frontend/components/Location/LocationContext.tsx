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
    console.log('🔍 Checking geolocation support:', supported)
    setIsSupported(supported)
    
    const init = async () => {
      if (supported) {
        await checkPermissions()
      }
      // Try to load cached location
      loadCachedLocation()
      
      // If no cached location, auto-request
      const cachedLocation = localStorage.getItem('cached_location')
      if (!cachedLocation) {
        console.log('🌍 No cached location, auto-requesting...')
        // Use setTimeout to avoid blocking render
        setTimeout(async () => {
          if (!location) { // Double check location is still null
            await requestLocation()
          }
        }, 500)
      }
    }
    
    init()
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
          console.log('📦 Loaded cached location:', locationData)
          setLocation(locationData)
        } else {
          console.log('🕐 Cached location expired, removing...')
          localStorage.removeItem('cached_location')
        }
      } else {
        console.log('📦 No cached location found')
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
    console.log('=== REQUEST LOCATION CALLED ===')
    console.log('Is supported:', isSupported)
    console.log('Current permission:', permission)

    if (!isSupported) {
      setError('Geolocation is not supported by this browser')
      console.log('❌ Geolocation not supported, trying network-based location...')
      return await requestNetworkLocation()
    }

    setIsLoading(true)
    setError(null)
    console.log('📍 Starting geolocation watch...')

    return new Promise((resolve) => {
      let bestReading: LocationData | null = null
      let settled = false

      const finish = (result: LocationData | null) => {
        if (settled) return
        settled = true
        navigator.geolocation.clearWatch(watchId)
        clearTimeout(timerId)
        if (result) {
          console.log('✅ Best GPS reading:', result)
          setLocation(result)
          cacheLocation(result)
        }
        setIsLoading(false)
        resolve(result)
      }

      const watchId = navigator.geolocation.watchPosition(
        (position) => {
          const reading: LocationData = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: Date.now(),
            source: 'gps'
          }
          console.log(`📍 GPS reading: accuracy=${position.coords.accuracy}m`)

          if (!bestReading || (reading.accuracy !== null && (bestReading.accuracy === null || reading.accuracy < bestReading.accuracy))) {
            bestReading = reading
          }

          // Good enough GPS fix — stop early
          if (reading.accuracy !== null && reading.accuracy <= 20) {
            finish(bestReading)
          }
        },
        (err) => {
          console.log('❌ Watch error:', { code: err.code, message: err.message })

          if (err.code === err.PERMISSION_DENIED) {
            setError('Location access denied by user')
            finish(null)
          }
          // TIMEOUT and POSITION_UNAVAILABLE: keep waiting for more readings
        },
        {
          enableHighAccuracy: true,
          maximumAge: 0, // Force fresh hardware readings
          timeout: 10000,
        }
      )

      // After 10 seconds, use best reading or fall back to IP
      const timerId = setTimeout(() => {
        if (settled) return
        if (bestReading) {
          finish(bestReading)
        } else {
          navigator.geolocation.clearWatch(watchId)
          console.log('🔄 No GPS readings, trying network-based location...')
          requestNetworkLocation().then((networkResult) => {
            if (!settled) {
              settled = true
              setIsLoading(false)
              resolve(networkResult)
            }
          })
        }
      }, 10000)
    })
  }

  const requestNetworkLocation = async (): Promise<LocationData | null> => {
    setIsLoading(true)
    try {
      console.log('🌐 Fetching location from IP address...')
      // Try to get location from IP-based services as fallback
      const response = await fetch('https://ipapi.co/json/')
      if (response.ok) {
        const data = await response.json()
        console.log('✅ IP-based location data:', data)
        
        const locationData: LocationData = {
          latitude: data.latitude,
          longitude: data.longitude,
          accuracy: null, // IP-based location has low accuracy
          timestamp: Date.now(),
          source: 'network'
        }
        
        setLocation(locationData)
        cacheLocation(locationData)
        setIsLoading(false)
        
        // toast.success(`Location detected: ${data.city}, ${data.region}`)
        return locationData
      } else {
        console.warn('❌ Network location API returned error:', response.status)
      }
    } catch (err) {
      console.warn('❌ Network location failed:', err)
      // toast.error('Could not detect location from network')
    }
    
    setIsLoading(false)
    return null
  }

  const clearLocation = () => {
    console.log('🗑️ Clearing location from context')
    setLocation(null)
    setError(null)
    localStorage.removeItem('cached_location')
  }

  const handleSetLocation = (locationData: LocationData) => {
    console.log('📍 Setting location in context:', locationData)
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

