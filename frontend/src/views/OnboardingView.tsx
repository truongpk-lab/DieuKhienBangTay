import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, Briefcase, Gamepad2, Loader2, Play, Sparkles } from 'lucide-react'
import { activateProfile } from '../api/profileApi'
import {
  getCameras,
  getMicrophones,
  getSettings,
  mockSettings,
  saveSettings,
  skipCalibration,
  startCalibration,
  type AppSettings,
  type CameraDevice,
  type HandMode,
  type MicrophoneDevice,
} from '../api/settingsApi'
import type { Profile } from '../types'

const profileIcons = {
  office: Briefcase,
  entertainment: Play,
  game_2d: Gamepad2,
  custom: Sparkles,
}

type OnboardingViewProps = {
  profiles: Profile[]
  onComplete: () => void
}

export default function OnboardingView({ profiles, onComplete }: OnboardingViewProps) {
  const [settings, setSettings] = useState<AppSettings>(mockSettings)
  const [cameras, setCameras] = useState<CameraDevice[]>([])
  const [microphones, setMicrophones] = useState<MicrophoneDevice[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState<'start' | 'skip' | null>(null)
  const [savingProfile, setSavingProfile] = useState(false)
  const [notice, setNotice] = useState('Đang tải thiết lập từ backend...')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let canceled = false

    async function loadOnboardingState() {
      try {
        const [settingsResult, cameraResult, microphoneResult] = await Promise.all([
          getSettings(),
          getCameras(),
          getMicrophones(),
        ])

        if (canceled) {
          return
        }

        setSettings(settingsResult)
        setCameras(cameraResult)
        setMicrophones(microphoneResult)
        setNotice('Backend online: cấu hình thật đã sẵn sàng.')
      } catch (err) {
        if (!canceled) {
          setError(errorMessage(err))
          setNotice('Không kết nối được backend; các bước lưu/hiệu chỉnh đang bị khóa.')
        }
      } finally {
        if (!canceled) {
          setLoading(false)
        }
      }
    }

    loadOnboardingState()
    return () => {
      canceled = true
    }
  }, [])

  const activeProfile = useMemo(
    () => profiles.find((profile) => profile.id === settings.active_profile_id) ?? profiles[0],
    [profiles, settings.active_profile_id],
  )

  const selectedCamera = cameras.find((camera) => camera.id === settings.camera_id)
  const selectedMicrophone = microphones.find((microphone) => microphone.id === settings.microphone_id)
  const noCameraAvailable = !loading && cameras.length === 0

  function updateSettings(next: Partial<AppSettings>) {
    setSettings((current) => ({ ...current, ...next }))
    setError(null)
  }

  async function handleProfileSelect(profileId: string) {
    const nextSettings = { ...settings, active_profile_id: profileId }
    setSettings(nextSettings)
    setSavingProfile(true)
    setError(null)

    try {
      await activateProfile(profileId)
      await saveSettings(nextSettings)
      setNotice('Đã lưu profile đang dùng.')
    } catch (err) {
      setError(`${errorMessage(err)} Không thể lưu profile khi backend lỗi.`)
    } finally {
      setSavingProfile(false)
    }
  }

  async function submitOnboarding(action: 'start' | 'skip') {
    if (noCameraAvailable) {
      setError('Không tìm thấy camera. Hãy cắm camera hoặc kiểm tra quyền truy cập trước khi tiếp tục.')
      return
    }

    setSubmitting(action)
    setError(null)

    try {
      await saveSettings(settings)
      await activateProfile(settings.active_profile_id)
      if (action === 'start') {
        await startCalibration(settings)
        setNotice('Đã bắt đầu hiệu chỉnh. Chuyển sang Dashboard.')
      } else {
        await skipCalibration(settings)
        setNotice('Đã lưu cấu hình mặc định. Chuyển sang Dashboard.')
      }
      onComplete()
    } catch (err) {
      setError(`${errorMessage(err)} Không chuyển Dashboard vì cấu hình chưa được lưu thật.`)
    } finally {
      setSubmitting(null)
    }
  }

  return (
    <div className="grid min-h-[calc(100vh-100px)] place-items-center py-5">
      <div className="glass-panel grid w-full max-w-4xl gap-6 rounded-3xl p-6 md:grid-cols-[0.85fr_1.4fr]">
        <div className="rounded-2xl bg-cyan-300/5 p-6">
          <div className="mb-8 text-sm uppercase tracking-[0.24em] text-cyan-200">ACV Gesture Control</div>
          <h2 className="glow-text text-4xl font-semibold">Thiết lập ban đầu</h2>
          <p className="mt-4 text-slate-400">Chọn thiết bị, tay điều khiển và profile trước khi vào dashboard.</p>
          <div className="mt-8 flex items-center gap-3 rounded-xl border border-cyan-300/15 bg-cyan-300/5 p-4 text-cyan-100">
            <span className="relative flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-300 opacity-60" />
              <span className="relative inline-flex h-3 w-3 rounded-full bg-cyan-300 shadow-[0_0_16px_#00f2ff]" />
            </span>
            {loading ? 'Đang đồng bộ thiết lập' : 'Sẵn sàng hiệu chỉnh'}
          </div>
          <div className="mt-4 rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-300">
            <div className="text-cyan-100">{notice}</div>
            <div className="mt-2 text-slate-500">
              Camera: {selectedCamera?.label ?? 'Chưa chọn'} · Mic: {selectedMicrophone?.label ?? 'Không dùng'} · Profile: {activeProfile?.name ?? 'Chưa chọn'}
            </div>
          </div>
        </div>
        <div className="space-y-5">
          {error && (
            <div className="flex gap-3 rounded-xl border border-amber-300/25 bg-amber-300/10 p-4 text-sm text-amber-100">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          {noCameraAvailable && (
            <div className="rounded-xl border border-red-300/25 bg-red-400/10 px-4 py-3 text-sm text-red-100">
              Không có camera khả dụng từ backend.
            </div>
          )}
          <select
            className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading || noCameraAvailable}
            value={settings.camera_id}
            onChange={(event) => updateSettings({ camera_id: event.target.value })}
          >
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.id}>
                {camera.label}
              </option>
            ))}
          </select>
          <select
            className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading || microphones.length === 0}
            value={settings.microphone_id ?? ''}
            onChange={(event) => updateSettings({ microphone_id: event.target.value || null })}
          >
            <option value="">Không dùng mic</option>
            {microphones.map((microphone) => (
              <option key={microphone.id} value={microphone.id}>
                {microphone.label}
              </option>
            ))}
          </select>
          <label className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-slate-200">
            <span>Lệnh giọng nói Gemini</span>
            <input
              type="checkbox"
              className="h-5 w-5 accent-cyan-300"
              checked={settings.voice_commands_enabled}
              onChange={(event) => updateSettings({ voice_commands_enabled: event.target.checked })}
            />
          </label>
          <div className="grid grid-cols-3 gap-2 rounded-xl bg-white/5 p-1">
            {[
              { id: 'left', label: 'Tay trái' },
              { id: 'right', label: 'Tay phải' },
              { id: 'auto', label: 'Tự động' },
            ].map((item) => (
              <button
                key={item.id}
                className={`rounded-lg py-3 ${settings.hand_mode === item.id ? 'bg-cyan-300 text-black' : 'text-slate-300'}`}
                onClick={() => updateSettings({ hand_mode: item.id as HandMode })}
                type="button"
              >
                {item.label}
              </button>
            ))}
          </div>
          <Slider
            label="Tốc độ chuột"
            value={`${settings.speed.toFixed(1)}x`}
            min={0.1}
            max={3}
            step={0.1}
            numericValue={settings.speed}
            onChange={(value) => updateSettings({ speed: value })}
          />
          <Slider
            label="Sensitivity"
            value={`${settings.sensitivity}%`}
            min={0}
            max={100}
            step={1}
            numericValue={settings.sensitivity}
            onChange={(value) => updateSettings({ sensitivity: value })}
          />
          <Slider
            label="Smoothing"
            value={`Mức ${settings.smoothing}`}
            min={1}
            max={5}
            step={1}
            numericValue={settings.smoothing}
            onChange={(value) => updateSettings({ smoothing: value })}
          />
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {profiles.map((profile) => {
              const Icon = profileIcons[profile.id as keyof typeof profileIcons] ?? Sparkles
              const active = settings.active_profile_id === profile.id
              return (
                <button
                  key={profile.id}
                  className={`rounded-xl border p-4 text-left transition ${active ? 'border-cyan-300/60 bg-cyan-300/10' : 'border-white/10 bg-white/[0.03] hover:border-cyan-300/25'}`}
                  disabled={savingProfile || submitting !== null}
                  onClick={() => handleProfileSelect(profile.id)}
                  type="button"
                >
                  <Icon className="mb-3 h-5 w-5 text-cyan-200" />
                  <div>{profile.name}</div>
                  <div className="mt-1 line-clamp-2 text-xs text-slate-500">{profile.description}</div>
                </button>
              )
            })}
          </div>
          <div className="flex gap-3">
            <button
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-cyan-300 px-5 py-3 font-semibold text-black disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading || submitting !== null}
              onClick={() => submitOnboarding('start')}
              type="button"
            >
              {submitting === 'start' && <Loader2 className="h-4 w-4 animate-spin" />}
              Bắt đầu hiệu chỉnh
            </button>
            <button
              className="flex items-center justify-center gap-2 rounded-xl border border-cyan-300/30 px-5 py-3 text-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading || submitting !== null}
              onClick={() => submitOnboarding('skip')}
              type="button"
            >
              {submitting === 'skip' && <Loader2 className="h-4 w-4 animate-spin" />}
              Bỏ qua
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function Slider({
  label,
  value,
  min,
  max,
  step,
  numericValue,
  onChange,
}: {
  label: string
  value: string
  min: number
  max: number
  step: number
  numericValue: number
  onChange: (value: number) => void
}) {
  return (
    <label className="block">
      <div className="mb-2 flex justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="text-cyan-200">{value}</span>
      </div>
      <input
        className="w-full accent-cyan-300"
        type="range"
        min={min}
        max={max}
        step={step}
        value={numericValue}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  )
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Không thể kết nối backend.'
}
