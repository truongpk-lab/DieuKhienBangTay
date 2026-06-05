import { requestJson } from './http'

export type VoiceCommandResponse = {
  ok: boolean
  intent?: string | null
  target?: string | null
  profile_id?: string | null
  action?: string | null
  confidence: number
  requires_confirmation: boolean
  transcript?: string | null
  executed: boolean
  message: string
}

export function sendVoiceCommand(text: string, execute = true) {
  return requestJson<VoiceCommandResponse>('/api/ai/command', {
    method: 'POST',
    body: JSON.stringify({ text, execute }),
    timeoutMs: 15000,
  })
}
