'use client'

import { useState, useCallback, useRef, useContext, useEffect } from 'react'
import { FiSearch, FiSend, FiMenu } from 'react-icons/fi'
import { AiOutlineLoading3Quarters } from 'react-icons/ai'
import toast from 'react-hot-toast'
import { useAuth } from '@clerk/nextjs'
import { useMapContext } from './MapContext'
import ChatContext from '../Chat/chatContext'
import { useLocation } from '@/components/Location'
import { config } from '@/utils/environment'

const SUGGESTIONS = [
  'Restaurants nearby',
  'Pharmacies open now',
  'Parking with low occupancy',
  'Coffee shops',
]

interface SearchBarProps {
  onToggleHistory: () => void
}

export default function SearchBar({ onToggleHistory }: SearchBarProps) {
  const [input, setInput] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const { getToken } = useAuth()
  const { location: contextLocation } = useLocation()
  const { activeUserLocation, setActivePlaces, setActiveUserLocation, setAiResponse, isQuerying, setIsQuerying, setSelectedPlaceId } = useMapContext()
  const { currentChatRef } = useContext(ChatContext)

  useEffect(() => {
    console.log(`[SearchBar] mount, apiUrl="${config.apiUrl}"`)
  }, [])

  // Sync GPS location into MapContext so the map centers on the user before any query
  useEffect(() => {
    if (contextLocation && contextLocation.latitude !== null && contextLocation.longitude !== null) {
      if (!activeUserLocation ||
          activeUserLocation.latitude !== contextLocation.latitude ||
          activeUserLocation.longitude !== contextLocation.longitude) {
        setActiveUserLocation({ latitude: contextLocation.latitude, longitude: contextLocation.longitude })
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [contextLocation])

  const handleSubmit = useCallback(async (text?: string) => {
    const query = text || input.trim()
    if (!query || isQuerying) return

    setIsQuerying(true)
    setInput('')
    setActivePlaces([])
    setAiResponse(null)
    setSelectedPlaceId(null)

    const effectiveLocation = contextLocation && contextLocation.latitude !== null && contextLocation.longitude !== null
      ? { latitude: contextLocation.latitude, longitude: contextLocation.longitude }
      : null

    console.log(`[SearchBar] query="${query.slice(0, 60)}" hasLocation=${!!effectiveLocation}`)

    try {
      const token = await getToken()
      const data: any = {
        threadId: currentChatRef?.current?.id,
        text: query,
        location: effectiveLocation,
      }

      const response = await fetch(`${config.apiUrl}/api/v1/query`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(data),
      })

      if (response.ok) {
        const parsed = await response.json()
        const answer = parsed.answer || ''
        const places = parsed.places || []
        const userLoc = parsed.userLocation || null

        console.log(`[SearchBar] response ok, places=${places.length}`)
        setAiResponse(answer)
        setActivePlaces(places)
        if (userLoc) setActiveUserLocation(userLoc)
      } else {
        const result = await response.json()
        console.log(`[SearchBar] error ${response.status}: ${result.error}`)
        toast.error(result.error || 'An error occurred')
      }
    } catch (error: any) {
      console.error('[SearchBar] fetch error:', error.message)
      toast.error(error.message || 'An error occurred')
    } finally {
      setIsQuerying(false)
    }
  }, [input, isQuerying, contextLocation, getToken, currentChatRef, setActivePlaces, setActiveUserLocation, setAiResponse, setIsQuerying, setSelectedPlaceId])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }, [handleSubmit])

  return (
    <div className="hidden md:block absolute top-4 left-4 md:w-[340px] lg:w-[420px] z-20">
      {/* Search input */}
      <div className="glass-panel flex items-center gap-3 px-4 py-3 focus-within:border-blue-400/50 dark:focus-within:border-neon-cyan/50 focus-within:shadow-[0_0_15px_rgba(59,130,246,0.15)] dark:focus-within:shadow-[0_0_15px_rgba(34,211,238,0.15)] transition-all">
        <button
          onClick={onToggleHistory}
          className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors flex-shrink-0"
        >
          <FiMenu className="size-5" />
        </button>
        <FiSearch className="size-4 text-gray-400 dark:text-gray-500 flex-shrink-0" />
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search for places, services..."
          disabled={isQuerying}
          className="flex-1 bg-transparent text-gray-800 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 outline-none text-sm"
        />
        <button
          onClick={() => handleSubmit()}
          disabled={isQuerying || !input.trim()}
          className="text-blue-600 dark:text-neon-cyan hover:text-blue-500 dark:hover:text-cyan-300 disabled:text-gray-400 dark:disabled:text-gray-600 transition-colors flex-shrink-0"
        >
          {isQuerying ? (
            <AiOutlineLoading3Quarters className="size-4 animate-spin" />
          ) : (
            <FiSend className="size-4" />
          )}
        </button>
      </div>

      {/* Suggestion chips */}
      <div className="flex gap-2 mt-2 flex-wrap">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => {
              setInput(s)
              handleSubmit(s)
            }}
            disabled={isQuerying}
            className="px-3 py-1.5 rounded-full text-xs text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-white/10 bg-white/80 dark:bg-surface/80 backdrop-blur-sm hover:border-blue-400/30 dark:hover:border-neon-cyan/30 hover:text-gray-800 dark:hover:text-gray-200 transition-all disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}
