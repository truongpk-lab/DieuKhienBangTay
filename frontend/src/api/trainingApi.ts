import { requestJson } from './http'

export type TrainingMode = 'image' | 'video'

export type TrainingStatus = {
  sessionId?: string | null
  active: boolean
  profileId: string
  functionId: string
  mode: TrainingMode | string
  samples: number
  targetSamples: number
  progress: number
  lastError?: string | null
  preview?: TrainingSamplePreview[]
}

export type TrainingSamplePreview = {
  sampleId: string
  path: string
  profileId: string
  functionId: string
  mode: string
}

export type StartTrainingSessionRequest = {
  profile_id: string
  function_id: string
  mode: TrainingMode
  target_samples: number
}

export type CaptureTrainingSampleRequest = {
  session_id?: string
}

export type TrainingJobResponse = TrainingStatus & {
  jobId?: string
  modelId?: string
  metrics?: Record<string, number>
}

export function getTrainingStatus() {
  return requestJson<TrainingStatus>('/api/training/status')
}

export function startTrainingSession(request: StartTrainingSessionRequest) {
  return requestJson<TrainingStatus>('/api/training/session/start', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export function stopTrainingSession() {
  return requestJson<TrainingStatus>('/api/training/session/stop', { method: 'POST' })
}

export function captureTrainingSample(request: CaptureTrainingSampleRequest = {}) {
  return requestJson<TrainingStatus>('/api/training/sample/capture', {
    method: 'POST',
    body: JSON.stringify(request),
  })
}

export function getTrainingSamplePreview() {
  return requestJson<TrainingSamplePreview[]>('/api/training/samples/preview')
}

export function trainGestureModel() {
  return requestJson<TrainingJobResponse>('/api/training/train', { method: 'POST' })
}

export function saveTrainingModel() {
  return requestJson<TrainingStatus>('/api/training/save', { method: 'POST' })
}

export function saveTrainingSession() {
  return requestJson<TrainingStatus>('/api/training/session/save', { method: 'POST' })
}

export function cancelTrainingSession() {
  return requestJson<TrainingStatus>('/api/training/session/cancel', { method: 'POST' })
}
