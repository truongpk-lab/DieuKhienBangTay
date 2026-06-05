import { mockProfiles, type FunctionMapping, type Profile } from '../types'
import { requestJson, withApiFallback } from './http'

export type ProfileDetail = Profile & {
  is_active?: boolean
  mouse?: Record<string, number>
  gesture_filter?: Record<string, unknown>
  functions?: FunctionMapping[]
}

export type SaveProfileRequest = ProfileDetail

export type CreateProfileRequest = {
  id: string
  name: string
  description: string
  functions?: FunctionMapping[]
}

export function getProfiles() {
  return requestJson<Profile[]>('/api/profiles')
}

export function getProfilesWithFallback() {
  return withApiFallback(getProfiles, mockProfiles)
}

export function getProfile(profileId: string) {
  return requestJson<ProfileDetail>(`/api/profiles/${encodeURIComponent(profileId)}`)
}

export function saveProfile(profileId: string, profile: SaveProfileRequest) {
  return requestJson<ProfileDetail>(`/api/profiles/${encodeURIComponent(profileId)}`, {
    method: 'PUT',
    body: JSON.stringify(profile),
  })
}

export function activateProfile(profileId: string) {
  return requestJson<ProfileDetail>(`/api/profiles/${encodeURIComponent(profileId)}/activate`, {
    method: 'POST',
  })
}

export function createProfile(profile: CreateProfileRequest) {
  return requestJson<ProfileDetail>('/api/profiles', {
    method: 'POST',
    body: JSON.stringify(profile),
  })
}

export function deleteProfile(profileId: string) {
  return requestJson<{ ok: boolean }>(`/api/profiles/${encodeURIComponent(profileId)}`, {
    method: 'DELETE',
  })
}
