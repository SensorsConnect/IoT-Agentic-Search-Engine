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
      <div className="absolute inset-0 z-35 bg-black/40 md:backdrop-blur-[2px] md:bg-black/30" onClick={onClose} />

      {/* Floating panel — matches PlaceDetailSheet pattern */}
      <div className="absolute top-4 left-4 bottom-4 w-72 z-40 animate-slide-in-left overflow-hidden rounded-2xl">
        <div className="h-full bg-white/95 dark:bg-surface/95 md:backdrop-blur-xl border border-gray-200 dark:border-white/10 flex flex-col rounded-2xl">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-white/5 flex-shrink-0">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500 dark:bg-neon-cyan animate-live-pulse" />
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Search History</span>
            </div>
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-full bg-gray-100 dark:bg-white/5 border border-gray-200 dark:border-white/10 flex items-center justify-center text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-200 dark:hover:bg-white/10 transition-all"
            >
              <FiX className="size-3.5" />
            </button>
          </div>

          {/* New Search */}
          <div className="px-3 pt-3 flex-shrink-0">
            <button
              onClick={handleNewSearch}
              className="flex items-center gap-2 w-full px-3 py-2.5 rounded-xl bg-blue-50 dark:bg-neon-cyan/10 border border-blue-200 dark:border-neon-cyan/20 text-blue-600 dark:text-neon-cyan text-sm hover:bg-blue-100 dark:hover:bg-neon-cyan/20 transition-all"
            >
              <FiPlus className="size-4" />
              New Search
            </button>
          </div>

          {/* Chat list */}
          <div className="flex-1 overflow-y-auto dark-scrollbar mt-2 px-3 pb-3 space-y-1 min-h-0">
            {chatList.map((chat) => {
              const isActive = currentChatRef?.current?.id === chat.id
              return (
                <div
                  key={chat.id}
                  onClick={() => handleChangeChat(chat)}
                  className={`group flex items-center gap-2 px-3 py-2.5 rounded-xl cursor-pointer transition-all text-sm ${
                    isActive
                      ? 'bg-blue-50 dark:bg-white/10 text-blue-700 dark:text-gray-200 border border-blue-200/50 dark:border-white/10'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-white/5 hover:text-gray-800 dark:hover:text-gray-300 border border-transparent'
                  }`}
                >
                  <FiMessageSquare className="size-3.5 flex-shrink-0 text-gray-400 dark:text-gray-500" />
                  <span className="truncate flex-1">{chat.title || chat.persona?.name || 'New Search'}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteChat?.(chat)
                    }}
                    className="hidden group-hover:flex w-5 h-5 rounded-full items-center justify-center text-gray-400 dark:text-gray-600 hover:text-red-500 dark:hover:text-neon-red hover:bg-red-50 dark:hover:bg-red-500/10 transition-all"
                  >
                    <FiX className="size-3" />
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
