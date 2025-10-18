'use client'
import { Suspense } from 'react'
import { Flex } from '@radix-ui/themes'
import { Chat, ChatContext, ChatSideBar, useChatHook, LocationProvider } from '@/components'
import PersonaModal from './PersonaModal'
import PersonaPanel from './PersonaPanel'

const ChatProvider = () => {
  const provider = useChatHook()

  return (
    <LocationProvider>
      <ChatContext.Provider value={provider}>
        <Flex style={{ height: 'calc(100% - 56px)' }} className="relative">
          <ChatSideBar />
          <div className="flex-1 relative">
            <Chat ref={provider.chatRef} />
            <PersonaPanel />
          </div>
        </Flex>
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
