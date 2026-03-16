'use client'

import { useState, useCallback, useContext, useRef, useEffect } from 'react'
import { FiSearch, FiSend, FiMenu } from 'react-icons/fi'
import { AiOutlineLoading3Quarters } from 'react-icons/ai'
import toast from 'react-hot-toast'
import { useAuth } from '@clerk/nextjs'
import { useMapContext } from './MapContext'
import ChatContext from '../Chat/chatContext'
import { useLocation } from '@/components/Location'
import { config } from '@/utils/environment'
import PlaceCard from '../PlaceCard/PlaceCard'
import { Markdown } from '@/components'

interface MobileSearchSheetProps {
  onToggleHistory: () => void
}

export default function MobileSearchSheet({ onToggleHistory }: MobileSearchSheetProps) {
  const [input, setInput] = useState('')
  const { getToken } = useAuth()
  const { location: contextLocation } = useLocation()
  const {
    activePlaces, aiResponse, isQuerying, selectedPlaceId, mobileMapRatio,
    activeUserLocation, setActivePlaces, setActiveUserLocation, setAiResponse,
    setIsQuerying, setSelectedPlaceId, setMobileMapRatio
  } = useMapContext()
  const { currentChatRef } = useContext(ChatContext)

  // Sync GPS location into MapContext so the map centers on the user before any query
  useEffect(() => {
    if (contextLocation && contextLocation.latitude !== null && contextLocation.longitude !== null) {
      if (!activeUserLocation ||
          activeUserLocation.latitude !== contextLocation.latitude ||
          activeUserLocation.longitude !== contextLocation.longitude) {
        setActiveUserLocation({ latitude: contextLocation.latitude, longitude: contextLocation.longitude })
      }
    }
  }, [contextLocation, activeUserLocation, setActiveUserLocation])
  const containerRef = useRef<HTMLDivElement>(null)
  const cardRefs = useRef<Map<string, HTMLDivElement>>(new Map())

  const hasResults = !!(aiResponse || activePlaces.length > 0)

  // Auto-scroll to the selected card when a pin is tapped
  useEffect(() => {
    if (!selectedPlaceId) return
    const el = cardRefs.current.get(selectedPlaceId)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }, [selectedPlaceId])

  const handleSubmit = useCallback(async () => {
    const query = input.trim()
    if (!query || isQuerying) return

    setIsQuerying(true)
    setInput('')
    setActivePlaces([])
    setAiResponse(null)
    setSelectedPlaceId(null)
    setMobileMapRatio(50)

    const effectiveLocation = contextLocation && contextLocation.latitude !== null && contextLocation.longitude !== null
      ? { latitude: contextLocation.latitude, longitude: contextLocation.longitude }
      : null

    try {
      const token = await getToken()
      const response = await fetch(`${config.apiUrl}/api/v1/query`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          threadId: currentChatRef?.current?.id,
          text: query,
          location: effectiveLocation,
        }),
      })

      if (response.ok) {
        const reader = response.body?.getReader()
        if (!reader) throw new Error('No data')
        const decoder = new TextDecoder('utf-8')
        let done = false
        let resultContent = ''
        while (!done) {
          const { value, done: readerDone } = await reader.read()
          if (value) resultContent += decoder.decode(value)
          done = readerDone
        }
        const parsed = JSON.parse(resultContent)
        setAiResponse(parsed.answer || '')
        setActivePlaces(parsed.places || [])
        if (parsed.userLocation) setActiveUserLocation(parsed.userLocation)
      } else {
        const result = await response.json()
        toast.error(result.error || 'An error occurred')
      }
    } catch (error: any) {
      toast.error(error.message || 'An error occurred')
    } finally {
      setIsQuerying(false)
    }
  }, [input, isQuerying, contextLocation, getToken, currentChatRef, setActivePlaces, setActiveUserLocation, setAiResponse, setIsQuerying, setSelectedPlaceId, setMobileMapRatio])

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    e.preventDefault()
  }, [])

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    const parent = containerRef.current?.parentElement
    if (!parent) return
    const touch = e.touches[0]
    const parentRect = parent.getBoundingClientRect()
    const ratio = ((touch.clientY - parentRect.top) / parentRect.height) * 100
    setMobileMapRatio(Math.min(85, Math.max(25, ratio)))
  }, [setMobileMapRatio])

  return (
    <div
      ref={containerRef}
      className="flex flex-col min-h-0 md:hidden bg-surface/95 backdrop-blur-xl border-t border-white/10"
      style={{ height: hasResults ? `${100 - mobileMapRatio}%` : '56px' }}
    >
      {/* Drag handle — only when results are showing */}
      {hasResults && (
        <div
          className="flex justify-center py-1.5 cursor-row-resize touch-none flex-shrink-0"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
        >
          <div className="w-10 h-1 rounded-full bg-white/20" />
        </div>
      )}

      {/* Search input */}
      <div className="flex items-center gap-2 px-4 py-2 flex-shrink-0">
        <button onClick={onToggleHistory} className="text-gray-400">
          <FiMenu className="size-5" />
        </button>
        <div className="flex-1 flex items-center gap-2 px-3 py-2 rounded-xl bg-white/5 border border-white/10">
          <FiSearch className="size-4 text-gray-500" />
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder="Search places..."
            className="flex-1 bg-transparent text-gray-200 placeholder-gray-500 outline-none text-sm"
          />
          <button onClick={handleSubmit} disabled={isQuerying} className="text-neon-cyan">
            {isQuerying ? (
              <AiOutlineLoading3Quarters className="size-4 animate-spin" />
            ) : (
              <FiSend className="size-4" />
            )}
          </button>
        </div>
      </div>

      {/* Scrollable content area */}
      {hasResults && (
        <div className="flex-1 overflow-y-auto dark-scrollbar px-4 pb-4 min-h-0">
          {/* AI Response */}
          {aiResponse && (
            <div className="mb-3 p-3 rounded-xl bg-white/[0.03] border border-white/5">
              <div className="flex items-center gap-2 mb-2">
                <span className="w-2 h-2 rounded-full bg-neon-cyan animate-live-pulse" />
                <span className="text-xs text-gray-500 uppercase tracking-wider">AI Response</span>
              </div>
              <div className="text-sm text-gray-300">
                <Markdown>{aiResponse}</Markdown>
              </div>
            </div>
          )}

          {/* Place cards — all listed, clicking zooms map */}
          {activePlaces.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs text-gray-500 uppercase tracking-wider">
                {activePlaces.length} place{activePlaces.length !== 1 ? 's' : ''} found
              </span>
              {activePlaces.map((place, i) => (
                <div
                  key={place.id}
                  ref={(el) => {
                    if (el) cardRefs.current.set(place.id, el)
                    else cardRefs.current.delete(place.id)
                  }}
                  className={`transition-all duration-300 rounded-xl ${
                    selectedPlaceId === place.id
                      ? 'ring-1 ring-neon-cyan/50 shadow-[0_0_12px_rgba(34,211,238,0.15)]'
                      : ''
                  }`}
                  style={{ animation: `cardEntrance 0.4s ease-out ${i * 75}ms both` }}
                >
                  <PlaceCard
                    place={place}
                    isSelected={selectedPlaceId === place.id}
                    onClick={() => setSelectedPlaceId(
                      selectedPlaceId === place.id ? null : place.id
                    )}
                    variant="dark"
                    index={i + 1}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
