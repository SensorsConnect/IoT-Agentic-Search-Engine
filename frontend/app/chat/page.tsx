'use client'
import { Suspense } from 'react'
import { ChatContext, useChatHook, LocationProvider } from '@/components'
import { MapProvider } from '@/components/Explorer'
import { ExplorerLayout } from '@/components/Explorer'
import PersonaModal from './PersonaModal'

const ChatProvider = () => {
  const provider = useChatHook()

  return (
    <LocationProvider>
      <ChatContext.Provider value={provider}>
        <MapProvider>
          <div className="relative">
            <ExplorerLayout />
          </div>
        </MapProvider>
        <PersonaModal />
      </ChatContext.Provider>
    </LocationProvider>
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
