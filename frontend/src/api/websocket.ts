import type { GestureLog, RuntimeStatus } from '../types'
import { getApiBaseUrl } from './http'

export type RuntimeSocketMessage = {
  type?: 'runtime_update' | 'gesture_event' | 'training_progress' | 'error' | 'warning'
  runtime?: RuntimeStatus
  logs?: GestureLog[]
  event?: string
  message?: string
  training?: unknown
}

export function createRuntimeSocket() {
  const wsBase = getApiBaseUrl().replace(/^http/, 'ws')
  return new WebSocket(`${wsBase}/ws/runtime`)
}
