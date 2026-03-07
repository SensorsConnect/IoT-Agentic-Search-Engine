'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@clerk/nextjs'
import { apiJson } from '@/lib/api'

export interface ConversationSummary {
  id: string
  title: string | null
  thread_id: string
  created_at: string
  updated_at: string
}

export interface ConversationMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ConversationDetail extends ConversationSummary {
  messages: ConversationMessage[]
}

export function useConversations() {
  const { getToken } = useAuth()
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [loading, setLoading] = useState(true)

  const fetchConversations = useCallback(async () => {
    try {
      const token = await getToken()
      const data = await apiJson<ConversationSummary[]>('/conversations', {}, token)
      setConversations(data)
    } catch (e) {
      console.error('Failed to fetch conversations:', e)
    } finally {
      setLoading(false)
    }
  }, [getToken])

  useEffect(() => {
    fetchConversations()
  }, [fetchConversations])

  return { conversations, loading, refetch: fetchConversations, setConversations }
}

export function useConversation(id: string | null) {
  const { getToken } = useAuth()
  const [conversation, setConversation] = useState<ConversationDetail | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchConversation = useCallback(async () => {
    if (!id) {
      setConversation(null)
      return
    }
    setLoading(true)
    try {
      const token = await getToken()
      const data = await apiJson<ConversationDetail>(`/conversations/${id}`, {}, token)
      setConversation(data)
    } catch (e) {
      console.error('Failed to fetch conversation:', e)
    } finally {
      setLoading(false)
    }
  }, [id, getToken])

  useEffect(() => {
    fetchConversation()
  }, [fetchConversation])

  return { conversation, loading, refetch: fetchConversation }
}

export async function deleteConversation(id: string, getToken: () => Promise<string | null>) {
  const token = await getToken()
  await apiJson(`/conversations/${id}`, { method: 'DELETE' }, token)
}

export async function renameConversation(id: string, title: string, getToken: () => Promise<string | null>) {
  const token = await getToken()
  await apiJson(`/conversations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ title }),
  }, token)
}
