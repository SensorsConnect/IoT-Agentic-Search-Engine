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
  ctx.setActiveUserLocation(null)
  ctx.setSelectedPlaceId(null)
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
      mapCtx.setActiveUserLocation(null)
      mapCtx.setSelectedPlaceId(null)
    }
    onClose()
  }

  const handleNewSearch = async () => {
    onCreateChat?.(DefaultPersonas[0])
    mapCtx.setAiResponse(null)
    mapCtx.setActivePlaces([])
    mapCtx.setActiveUserLocation(null)
    mapCtx.setSelectedPlaceId(null)
    onClose()
  }

  return (
    <>
      {/* Backdrop */}
      <div className="absolute inset-0 z-35 bg-black/40" onClick={onClose} />

      {/* Drawer */}
      <div className="absolute top-0 left-0 bottom-0 w-72 z-40 animate-slide-in-left">
        <div className="h-full bg-surface/95 backdrop-blur-xl border-r border-white/10 flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/5">
            <span className="text-sm font-medium text-gray-300">Search History</span>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-300 transition-colors"
            >
              <FiX className="size-4" />
            </button>
          </div>

          {/* New Search */}
          <button
            onClick={handleNewSearch}
            className="flex items-center gap-2 mx-3 mt-3 px-3 py-2.5 rounded-xl bg-neon-cyan/10 border border-neon-cyan/20 text-neon-cyan text-sm hover:bg-neon-cyan/20 transition-all"
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
                      ? 'bg-white/10 text-gray-200'
                      : 'text-gray-400 hover:bg-white/5 hover:text-gray-300'
                  }`}
                >
                  <FiMessageSquare className="size-3.5 flex-shrink-0" />
                  <span className="truncate flex-1">{chat.title || chat.persona?.name || 'New Search'}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteChat?.(chat)
                    }}
                    className="hidden group-hover:block text-gray-600 hover:text-neon-red transition-colors"
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
