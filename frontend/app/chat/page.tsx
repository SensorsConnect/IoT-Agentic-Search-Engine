'use client'

import { Suspense, useState, useCallback } from 'react'
import { ChatContext, useChatHook, LocationProvider } from '@/components'
import { MapProvider } from '@/components/Explorer'
import { ExplorerLayout } from '@/components/Explorer'
import { AppTour, TourProvider } from '@/components/Tour'
import PersonaModal from './PersonaModal'

const TOUR_STORAGE_KEY = 'localelive_tour_done'

const ChatProvider = () => {
  const provider = useChatHook()

  const [tourRun, setTourRun] = useState(() => {
    if (typeof window === 'undefined') return false
    return localStorage.getItem(TOUR_STORAGE_KEY) !== '1'
  })

  const startTour = useCallback(() => {
    localStorage.removeItem(TOUR_STORAGE_KEY)
    setTourRun(true)
  }, [])

  return (
    <TourProvider startTour={startTour}>
      <LocationProvider>
        <ChatContext.Provider value={provider}>
          <MapProvider>
            <div className="relative">
              <ExplorerLayout />
            </div>
            {/* AppTour is inside MapProvider so it can access MapContext */}
            <AppTour run={tourRun} onStop={() => setTourRun(false)} />
          </MapProvider>
          <PersonaModal />
        </ChatContext.Provider>
      </LocationProvider>
    </TourProvider>
  )
}

const ChatPage = () => {
  return (
    <Suspense>
      <ChatProvider />
    </Suspense>
  )
}

export default ChatPage
