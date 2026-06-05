import type { AppVisibilityStatus } from '../types'
import { requestJson, withApiFallback } from './http'

const browserFallback: AppVisibilityStatus = {
  action: 'status',
  mode: 'browser',
  supported: false,
  success: false,
  visible: true,
  message: 'Đang chạy trong trình duyệt nên hãy thu nhỏ cửa sổ thủ công sau khi runtime hoạt động.',
  lastError: 'Chế độ trình duyệt fallback',
}

export function getAppStatus() {
  return requestJson<AppVisibilityStatus>('/api/app/status')
}

export function minimizeApp() {
  return requestJson<AppVisibilityStatus>('/api/app/minimize', { method: 'POST' })
}

export function hideApp() {
  return requestJson<AppVisibilityStatus>('/api/app/hide', { method: 'POST' })
}

export function showApp() {
  return requestJson<AppVisibilityStatus>('/api/app/show', { method: 'POST' })
}

export function toggleAppVisibility() {
  return requestJson<AppVisibilityStatus>('/api/app/toggle', { method: 'POST' })
}

export function emergencyStopApp() {
  return requestJson<{ ok: boolean }>('/api/app/emergency-stop', { method: 'POST' })
}

export function startTray() {
  return requestJson<Record<string, unknown>>('/api/app/tray/start', { method: 'POST' })
}

export function startHotkey() {
  return requestJson<Record<string, unknown>>('/api/app/hotkey/start', { method: 'POST' })
}

export function minimizeAppWithFallback() {
  return withApiFallback(minimizeApp, browserFallback)
}

export function showAppWithFallback() {
  return withApiFallback(showApp, { ...browserFallback, action: 'show', success: true })
}
