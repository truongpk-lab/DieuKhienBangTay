import { requestJson } from './http'

export type ModelType = 'static' | 'dynamic'

export type ModelRecord = {
  model_id: string
  type: ModelType
  path: string
  created_at: string
  profiles: string[]
  labels: string[]
  metrics: Record<string, number>
  dataset: {
    sample_count: number
  }
}

export type ActiveModelsResponse = {
  static: ModelRecord | null
  dynamic: ModelRecord | null
}

export function getModels() {
  return requestJson<ModelRecord[]>('/api/models')
}

export function getActiveModels() {
  return requestJson<ActiveModelsResponse>('/api/models/active')
}

export function activateModel(modelId: string) {
  return requestJson<{ active: ModelRecord }>(`/api/models/${encodeURIComponent(modelId)}/activate`, {
    method: 'POST',
  })
}

export function rollbackModel(modelId: string) {
  return requestJson<{ active: ModelRecord | null }>(`/api/models/${encodeURIComponent(modelId)}/rollback`, {
    method: 'POST',
  })
}
