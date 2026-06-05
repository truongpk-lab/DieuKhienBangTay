import { requestJson } from './http'

export type HandMode = 'left' | 'right' | 'auto'

export type AppSettings = {
  camera_id: string
  microphone_id: string | null
  hand_mode: HandMode
  speed: number
  sensitivity: number
  smoothing: number
  active_profile_id: string
  auto_hide_on_start: boolean
  ai_provider: 'gemini'
  voice_commands_enabled: boolean
}

export type CameraDevice = {
  id: string
  label: string
  status: string
  mock: boolean
}

export type MicrophoneDevice = CameraDevice

export type CalibrationResponse = {
  ok: boolean
  status: 'calibrating' | 'skipped' | string
  message: string
  settings: AppSettings
}

export const mockSettings: AppSettings = {
  camera_id: '0',
  microphone_id: null,
  hand_mode: 'right',
  speed: 1.5,
  sensitivity: 75,
  smoothing: 3,
  active_profile_id: 'office',
  auto_hide_on_start: true,
  ai_provider: 'gemini',
  voice_commands_enabled: false,
}

export const mockCameras: CameraDevice[] = [
  {
    id: 'mock-camera-0',
    label: 'Webcam HD Camera',
    status: 'available',
    mock: true,
  },
]

export function getSettings() {
  return requestJson<AppSettings>('/api/settings')
}

export function getSettingsWithFallback() {
  return getSettings()
}

export function saveSettings(settings: AppSettings) {
  return requestJson<AppSettings>('/api/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  })
}

export function getCameras() {
  return requestJson<CameraDevice[]>('/api/cameras', { timeoutMs: 15000 })
}

export function getCamerasWithFallback() {
  return getCameras()
}

export function getMicrophones() {
  return requestJson<MicrophoneDevice[]>('/api/mic/devices', { timeoutMs: 15000 })
}

export function getMicrophoneStatus() {
  return requestJson<{ active: boolean; status: string; deviceId?: string | null; lastError?: string | null }>('/api/mic/status')
}

export function startMicrophone() {
  return requestJson<{ active: boolean; status: string; deviceId?: string | null; lastError?: string | null }>('/api/mic/start', { method: 'POST', timeoutMs: 15000 })
}

export function stopMicrophone() {
  return requestJson<{ active: boolean; status: string; deviceId?: string | null; lastError?: string | null }>('/api/mic/stop', { method: 'POST', timeoutMs: 15000 })
}

export function startCalibration(settings: AppSettings) {
  return requestJson<CalibrationResponse>('/api/calibration/start', {
    method: 'POST',
    body: JSON.stringify(settings),
  })
}

export function skipCalibration(settings: AppSettings) {
  return requestJson<CalibrationResponse>('/api/calibration/skip', {
    method: 'POST',
    body: JSON.stringify(settings),
  })
}
