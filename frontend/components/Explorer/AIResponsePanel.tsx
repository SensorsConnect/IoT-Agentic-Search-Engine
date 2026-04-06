'use client'

import { useState } from 'react'
import { FiChevronDown, FiChevronUp } from 'react-icons/fi'
import { Markdown } from '@/components'
import { useMapContext } from './MapContext'

export default function AIResponsePanel() {
  const { aiResponse, activePlaces, isQuerying } = useMapContext()
  const [collapsed, setCollapsed] = useState(false)

  if (!aiResponse && !isQuerying) return null

  const iotCount = activePlaces.filter((p) => p.source === 'iot_engine').length
  const hasIoT = iotCount > 0

  if (collapsed) {
    return (
      <button
        onClick={() => setCollapsed(false)}
        className="hidden md:flex absolute top-32 left-4 z-10 glass-panel px-4 py-2 items-center gap-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-gray-100 transition-colors cursor-pointer md:w-[340px] lg:w-[420px]"
      >
        <span className="w-2 h-2 rounded-full bg-neon-cyan animate-live-pulse" />
        AI Response
        <FiChevronDown className="size-3" />
      </button>
    )
  }

  return (
    <div className="hidden md:block absolute top-40 left-4 md:w-[340px] lg:w-[420px] z-10 animate-slide-in-top">
      <div className="glass-panel p-4 max-h-[calc(100dvh-460px)] min-h-0 overflow-y-auto dark-scrollbar">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500 dark:bg-neon-cyan animate-live-pulse" />
            <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">AI Recommendation</span>
          </div>
          <button
            onClick={() => setCollapsed(true)}
            className="text-gray-400 dark:text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            <FiChevronUp className="size-4" />
          </button>
        </div>

        {/* Loading state */}
        {isQuerying && !aiResponse && (
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-sm">
            <div className="w-4 h-4 border-2 border-neon-cyan/30 border-t-neon-cyan rounded-full animate-spin" />
            Analyzing your query...
          </div>
        )}

        {/* Response text */}
        {aiResponse && (
          <div className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
            <Markdown>{aiResponse}</Markdown>
          </div>
        )}

        {/* Footer stats */}
        {activePlaces.length > 0 && (
          <div className="flex items-center gap-3 mt-3 pt-3 border-t border-gray-200 dark:border-white/5">
            <span className="text-xs text-gray-500">
              {activePlaces.length} place{activePlaces.length !== 1 ? 's' : ''} found
            </span>
            {hasIoT && (
              <span className="flex items-center gap-1.5 text-xs text-neon-green">
                <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-live-pulse" />
                Live Updates ({iotCount})
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
