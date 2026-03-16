'use client'

import { useContext } from 'react'
import { FiX, FiPlus, FiMessageSquare } from 'react-icons/fi'
import ChatContext from '../Chat/chatContext'
import { useMapContext } from './MapContext'
import type { Chat, ChatMessage } from '../Chat/interface'

interface HistoryDrawerProps {
  open: boolean
  onClose: () => void
}

function syncMessagesToMap(
  messages: ChatMessage[],
  ctx: ReturnType<typeof useMapContext>
) {
  // Find the last assistant message with places
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i]
    if (msg.role === 'assistant') {
      ctx.setAiResponse(msg.content)
      ctx.setActivePlaces(msg.places || [])
      ctx.setActiveUserLocation(msg.userLocation || null)
      ctx.setSelectedPlaceId(null)
      ctx.setMobileMapRatio(50)
      return
    }
  }
  // No assistant message found — clear
  ctx.setAiResponse(null)
  ctx.setActivePlaces([])
  ctx.setSelectedPlaceId(null)
  ctx.setMobileMapRatio(50)
}

export default function HistoryDrawer({ open, onClose }: HistoryDrawerProps) {
  const {
    currentChatRef,
    chatList,
    DefaultPersonas,
    onDeleteChat,
    onChangeChat,
    onCreateChat,
  } = useContext(ChatContext)
  const mapCtx = useMapContext()

  if (!open) return null

  const handleChangeChat = async (chat: Chat) => {
    const msgs = await onChangeChat?.(chat)
    if (msgs && msgs.length > 0) {
      syncMessagesToMap(msgs, mapCtx)
    } else {
      // New or empty chat — clear panels
      mapCtx.setAiResponse(null)
      mapCtx.setActivePlaces([])
      mapCtx.setSelectedPlaceId(null)
      mapCtx.setMobileMapRatio(50)
    }
    onClose()
  }

  const handleNewSearch = async () => {
    onCreateChat?.(DefaultPersonas[0])
    mapCtx.setAiResponse(null)
    mapCtx.setActivePlaces([])
    mapCtx.setSelectedPlaceId(null)
    mapCtx.setMobileMapRatio(50)
    onClose()
  }

  return (
    <>
      {/* Backdrop */}
      <div className="absolute inset-0 z-35 bg-black/40" onClick={onClose} />

      {/* Drawer */}
      <div className="absolute top-0 left-0 bottom-0 w-72 z-40 animate-slide-in-left">
        <div className="h-full bg-white/95 dark:bg-surface/95 backdrop-blur-xl border-r border-gray-200 dark:border-white/10 flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-white/5">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Search History</span>
            <button
              onClick={onClose}
              className="text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            >
              <FiX className="size-4" />
            </button>
          </div>

          {/* New Search */}
          <button
            onClick={handleNewSearch}
            className="flex items-center gap-2 mx-3 mt-3 px-3 py-2.5 rounded-xl bg-blue-50 dark:bg-neon-cyan/10 border border-blue-200 dark:border-neon-cyan/20 text-blue-600 dark:text-neon-cyan text-sm hover:bg-blue-100 dark:hover:bg-neon-cyan/20 transition-all"
          >
            <FiPlus className="size-4" />
            New Search
          </button>

          {/* Chat list */}
          <div className="flex-1 overflow-y-auto dark-scrollbar mt-3 px-3 space-y-1">
            {chatList.map((chat) => {
              const isActive = currentChatRef?.current?.id === chat.id
              return (
                <div
                  key={chat.id}
                  onClick={() => handleChangeChat(chat)}
                  className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all text-sm ${
                    isActive
                      ? 'bg-gray-100 dark:bg-white/10 text-gray-800 dark:text-gray-200'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-white/5 hover:text-gray-800 dark:hover:text-gray-300'
                  }`}
                >
                  <FiMessageSquare className="size-3.5 flex-shrink-0" />
                  <span className="truncate flex-1">{chat.title || chat.persona?.name || 'New Search'}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteChat?.(chat)
                    }}
                    className="hidden group-hover:block text-gray-400 dark:text-gray-600 hover:text-red-500 dark:hover:text-neon-red transition-colors"
                  >
                    <FiX className="size-3.5" />
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </>
  )
}
