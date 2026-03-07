export interface Place {
  id: string
  name: string
  address: string | null
  latitude: number
  longitude: number
  rating: number | null
  about?: string | null
  opening_hours?: string | null
  open_now?: boolean | null
  photo_url?: string | null
  phone?: string | null
  website?: string | null
  google_maps_url?: string | null
  travel_time_min: number | null
  occupancy?: number | null
  overall_service_time_min?: number | null
  source: 'iot_engine' | 'google_maps'
}

export interface ChatMessage {
  content: string
  role: ChatRole
  places?: Place[]
  userLocation?: { latitude: number; longitude: number } | null
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
