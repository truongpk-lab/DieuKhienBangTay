import type { GestureLog, Profile, RuntimeStatus } from '../types'

const API_BASE = (import.meta.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '')

async function requestJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 1200)

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
    })
    if (!response.ok) {
      throw new Error(`Backend request failed: ${response.status}`)
    }
    return (await response.json()) as T
  } finally {
    window.clearTimeout(timeout)
  }
}

export function getRuntimeStatus() {
  return requestJson<RuntimeStatus>('/api/runtime/status')
}

export function startRuntime() {
  return requestJson<RuntimeStatus>('/api/runtime/start', { method: 'POST' })
}

export function stopRuntime() {
  return requestJson<RuntimeStatus>('/api/runtime/stop', { method: 'POST' })
}

export function getProfiles() {
  return requestJson<Profile[]>('/api/profiles')
}

export function getGestureLogs() {
  return requestJson<GestureLog[]>('/api/gestures/logs')
}

export function createRuntimeSocket() {
  const wsBase = API_BASE.replace(/^http/, 'ws')
  return new WebSocket(`${wsBase}/ws/runtime`)
}
