import { config } from '@/utils/environment'

const API_BASE = `${config.apiUrl}/api/v1`

export async function apiFetch(path: string, options: RequestInit = {}, token?: string | null) {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 401) {
    window.location.href = '/sign-in'
    throw new Error('Unauthorized')
  }

  return res
}

export async function apiJson<T>(path: string, options: RequestInit = {}, token?: string | null): Promise<T> {
  const res = await apiFetch(path, options, token)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || body.error || `API error ${res.status}`)
  }
  return res.json()
}
