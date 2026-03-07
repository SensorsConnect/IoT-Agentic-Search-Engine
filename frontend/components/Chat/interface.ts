export interface ChatMessage {
  content: string
  role: ChatRole
}

export interface Persona {
  id?: string
  role: ChatRole
  avatar?: string
  name?: string
  prompt?: string
  key?: string
  isDefault?: boolean
}

export interface Chat {
  id: string
  persona?: Persona
  messages?: ChatMessage[]
  title?: string
  conversationId?: string
  created_at?: string
  updated_at?: string
}

export type ChatRole = 'assistant' | 'user' | 'system'
