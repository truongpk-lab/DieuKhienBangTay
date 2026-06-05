import { mockLogs, mockRuntime, type GestureLog, type RuntimeStatus, type WorkflowState } from '../types'
import { requestJson, withApiFallback } from './http'

export type HealthResponse = {
  status: string
  service: string
  version: string
}

export function getHealth() {
  return requestJson<HealthResponse>('/api/health')
}

export function getRuntimeStatus() {
  return requestJson<RuntimeStatus>('/api/runtime/status')
}

export function getRuntimeStatusWithFallback() {
  return withApiFallback(getRuntimeStatus, mockRuntime)
}

export function startRuntime() {
  return requestJson<RuntimeStatus>('/api/runtime/start', { method: 'POST', timeoutMs: 30000 })
}

export function stopRuntime() {
  return requestJson<RuntimeStatus>('/api/runtime/stop', { method: 'POST', timeoutMs: 15000 })
}

export function pauseRuntime() {
  return requestJson<RuntimeStatus>('/api/runtime/pause', { method: 'POST', timeoutMs: 15000 })
}

export function resumeRuntime() {
  return requestJson<RuntimeStatus>('/api/runtime/resume', { method: 'POST', timeoutMs: 30000 })
}

export function recenterRuntime() {
  return requestJson<RuntimeStatus>('/api/runtime/recenter', { method: 'POST' })
}

export function getGestureLogs() {
  return requestJson<GestureLog[]>('/api/gestures/logs')
}

export function getGestureLogsWithFallback() {
  return withApiFallback(getGestureLogs, mockLogs)
}

export function clearGestureLogs() {
  return requestJson<GestureLog[]>('/api/gestures/logs', { method: 'DELETE' })
}

export function getWorkflowState() {
  return requestJson<WorkflowState>('/api/runtime/workflow')
}

export function testWorkflowState(request: {
  state: WorkflowState['state']
  event?: string
  pinch_distance?: number
  confidence?: number
}) {
  return requestJson<WorkflowState>('/api/runtime/workflow/test', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export function resetWorkflowState() {
  return requestJson<WorkflowState>('/api/runtime/workflow/reset', { method: 'POST' })
}
