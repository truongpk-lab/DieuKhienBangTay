import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { AlertTriangle, Briefcase, Camera, CheckCircle2, Gamepad2, Loader2, Play, RefreshCw, Sparkles, VideoOff } from 'lucide-react'
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
import HandSkeleton from '../components/HandSkeleton'
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
  const previewVideoRef = useRef<HTMLVideoElement>(null)
  const previewStreamRef = useRef<MediaStream | null>(null)
  const [settings, setSettings] = useState<AppSettings>(mockSettings)
  const [cameras, setCameras] = useState<CameraDevice[]>([])
  const [browserCameras, setBrowserCameras] = useState<MediaDeviceInfo[]>([])
  const [selectedBrowserCameraId, setSelectedBrowserCameraId] = useState('')
  const [microphones, setMicrophones] = useState<MicrophoneDevice[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState<'start' | 'skip' | null>(null)
  const [savingProfile, setSavingProfile] = useState(false)
  const [backendReady, setBackendReady] = useState(false)
  const [notice, setNotice] = useState('Đang tải thiết lập từ backend...')
  const [error, setError] = useState<string | null>(null)
  const [loadErrors, setLoadErrors] = useState<Partial<Record<'settings' | 'cameras' | 'microphones', string>>>({})
  const [previewStatus, setPreviewStatus] = useState<'idle' | 'requesting' | 'ready' | 'blocked' | 'unsupported'>('idle')
  const [previewError, setPreviewError] = useState<string | null>(null)

  const runtimeCameras = useMemo(() => {
    if (cameras.length > 0) {
      return cameras
    }

    if (browserCameras.length > 0 || loadErrors.cameras) {
      return [
        {
          id: '0',
          label: 'Camera 0 (OpenCV runtime)',
          status: 'pending_backend_probe',
          mock: false,
        },
      ]
    }

    return []
  }, [browserCameras.length, cameras, loadErrors.cameras])

  const stopPreview = useCallback(() => {
    previewStreamRef.current?.getTracks().forEach((track) => track.stop())
    previewStreamRef.current = null
    if (previewVideoRef.current) {
      previewVideoRef.current.srcObject = null
    }
  }, [])

  const startBrowserPreview = useCallback(
    async (deviceId = '') => {
      if (!navigator.mediaDevices?.getUserMedia) {
        setPreviewStatus('unsupported')
        setPreviewError('Trình duyệt không hỗ trợ camera trong phiên hiện tại.')
        return
      }

      setPreviewStatus('requesting')
      setPreviewError(null)
      stopPreview()

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: deviceId ? { deviceId: { exact: deviceId } } : true,
        })
        previewStreamRef.current = stream
        if (previewVideoRef.current) {
          previewVideoRef.current.srcObject = stream
          await previewVideoRef.current.play().catch(() => undefined)
        }

        const devices = await navigator.mediaDevices.enumerateDevices()
        const videoInputs = devices.filter((device) => device.kind === 'videoinput')
        setBrowserCameras(videoInputs)
        if (!deviceId && videoInputs[0]?.deviceId) {
          setSelectedBrowserCameraId(videoInputs[0].deviceId)
        }
        setPreviewStatus('ready')
      } catch (err) {
        setPreviewStatus('blocked')
        setPreviewError(mediaErrorMessage(err))
      }
    },
    [stopPreview],
  )

  useEffect(() => {
    let canceled = false

    async function loadOnboardingState() {
      setLoading(true)
      setError(null)
      setNotice('Đang tải thiết lập từ backend...')

      const [settingsResult, cameraResult, microphoneResult] = await Promise.allSettled([
        getSettings(),
        getCameras(),
        getMicrophones(),
      ])

      if (canceled) {
        return
      }

      const nextErrors: Partial<Record<'settings' | 'cameras' | 'microphones', string>> = {}

      if (settingsResult.status === 'fulfilled') {
        setSettings(settingsResult.value)
      } else {
        nextErrors.settings = errorMessage(settingsResult.reason)
      }

      if (cameraResult.status === 'fulfilled') {
        setCameras(cameraResult.value)
        if (cameraResult.value[0] && !cameraResult.value.some((camera) => camera.id === settings.camera_id)) {
          setSettings((current) => ({ ...current, camera_id: cameraResult.value[0].id }))
        }
      } else {
        nextErrors.cameras = errorMessage(cameraResult.reason)
      }

      if (microphoneResult.status === 'fulfilled') {
        setMicrophones(microphoneResult.value)
      } else {
        nextErrors.microphones = errorMessage(microphoneResult.reason)
      }

      const online = settingsResult.status === 'fulfilled'
      setBackendReady(online)
      setLoadErrors(nextErrors)
      setNotice(
        online
          ? 'Backend online: cấu hình thật đã sẵn sàng.'
          : 'Camera preview đang chạy bằng trình duyệt; backend API 127.0.0.1:8000 chưa online nên chưa thể lưu cấu hình thật.',
      )
      setLoading(false)
    }

    loadOnboardingState()
    startBrowserPreview()
    return () => {
      canceled = true
      stopPreview()
    }
  }, [startBrowserPreview, stopPreview])

  useEffect(() => {
    if (runtimeCameras.length > 0 && !runtimeCameras.some((camera) => camera.id === settings.camera_id)) {
      setSettings((current) => ({ ...current, camera_id: runtimeCameras[0].id }))
    }
  }, [runtimeCameras, settings.camera_id])

  const activeProfile = useMemo(
    () => profiles.find((profile) => profile.id === settings.active_profile_id) ?? profiles[0],
    [profiles, settings.active_profile_id],
  )

  const selectedCamera = runtimeCameras.find((camera) => camera.id === settings.camera_id)
  const selectedMicrophone = microphones.find((microphone) => microphone.id === settings.microphone_id)
  const noRuntimeCameraAvailable = !loading && runtimeCameras.length === 0
  const previewReady = previewStatus === 'ready'

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
    if (!backendReady) {
      setError('Backend chưa online nên chưa thể lưu cấu hình thật. Hãy chạy .\\start_acv.bat hoặc kiểm tra cổng 8000.')
      return
    }

    if (noRuntimeCameraAvailable) {
      setError('Không tìm thấy camera runtime. Hãy cắm camera hoặc kiểm tra quyền camera trước khi tiếp tục.')
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
          <div className={`flex gap-3 rounded-xl border p-4 text-sm ${backendReady ? 'border-emerald-300/20 bg-emerald-300/10 text-emerald-100' : 'border-amber-300/25 bg-amber-300/10 text-amber-100'}`}>
            {backendReady ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" /> : <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />}
            <span>{notice}</span>
          </div>
          {error && (
            <div className="flex gap-3 rounded-xl border border-amber-300/25 bg-amber-300/10 p-4 text-sm text-amber-100">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          {Object.keys(loadErrors).length > 0 && (
            <div className="rounded-xl border border-amber-300/20 bg-amber-300/5 p-4 text-sm text-amber-50">
              <div className="mb-2 flex items-center justify-between gap-3">
                <span>{Object.keys(loadErrors).length >= 3 ? 'Backend API chưa phản hồi.' : 'Một số API chưa phản hồi ổn định.'}</span>
                <button
                  className="inline-flex items-center gap-2 rounded-lg border border-amber-200/20 px-3 py-1.5 text-xs text-amber-100 transition hover:border-amber-100/40"
                  onClick={() => window.location.reload()}
                  type="button"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Thử lại
                </button>
              </div>
              <div className="space-y-1 text-xs text-amber-100/80">
                {loadErrors.settings && <div>Settings API: {loadErrors.settings}</div>}
                {loadErrors.cameras && <div>Camera API: {loadErrors.cameras}</div>}
                {loadErrors.microphones && <div>Microphone API: {loadErrors.microphones}</div>}
              </div>
            </div>
          )}
          {noRuntimeCameraAvailable && (
            <div className="rounded-xl border border-red-300/25 bg-red-400/10 px-4 py-3 text-sm text-red-100">
              Không có camera runtime khả dụng.
            </div>
          )}
          <select
            className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading || noRuntimeCameraAvailable}
            value={settings.camera_id}
            onChange={(event) => updateSettings({ camera_id: event.target.value })}
          >
            {runtimeCameras.map((camera) => (
              <option key={camera.id} value={camera.id}>
                {camera.label}
              </option>
            ))}
          </select>
          <div className="overflow-hidden rounded-2xl border border-cyan-300/15 bg-[#0e0e10]">
            <div className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-3 text-sm">
              <div className="flex items-center gap-2 text-cyan-100">
                <Camera className="h-4 w-4" />
                Xem camera
              </div>
              <button
                className="inline-flex items-center gap-2 rounded-lg border border-cyan-300/25 px-3 py-1.5 text-xs text-cyan-100 transition hover:border-cyan-200/50 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={previewStatus === 'requesting'}
                onClick={() => startBrowserPreview(selectedBrowserCameraId)}
                type="button"
              >
                {previewStatus === 'requesting' ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
                Kiểm tra
              </button>
            </div>
            <div className="relative aspect-video bg-black">
              <video ref={previewVideoRef} className={`h-full w-full object-cover ${previewReady ? 'opacity-100' : 'opacity-20'}`} muted playsInline />
              {previewReady && (
                <div className="pointer-events-none absolute inset-0 grid place-items-center opacity-95 mix-blend-screen">
                  <div className="h-[72%] w-[38%] min-w-40">
                    <HandSkeleton />
                  </div>
                </div>
              )}
              {!previewReady && (
                <div className="absolute inset-0 grid place-items-center px-5 text-center text-sm text-slate-300">
                  <div>
                    {previewStatus === 'requesting' ? (
                      <Loader2 className="mx-auto mb-3 h-7 w-7 animate-spin text-cyan-200" />
                    ) : (
                      <VideoOff className="mx-auto mb-3 h-7 w-7 text-slate-400" />
                    )}
                    <div>{previewError ?? 'Đang chờ quyền camera thật.'}</div>
                  </div>
                </div>
              )}
            </div>
            {browserCameras.length > 1 && (
              <select
                className="w-full border-t border-white/10 bg-[#1c1b1d] px-4 py-3 text-sm text-white"
                value={selectedBrowserCameraId}
                onChange={(event) => {
                  setSelectedBrowserCameraId(event.target.value)
                  startBrowserPreview(event.target.value)
                }}
              >
                {browserCameras.map((camera, index) => (
                  <option key={camera.deviceId} value={camera.deviceId}>
                    {camera.label || `Camera trình duyệt ${index + 1}`}
                  </option>
                ))}
              </select>
            )}
          </div>
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
              disabled={loading || submitting !== null || !backendReady}
              onClick={() => submitOnboarding('start')}
              type="button"
            >
              {submitting === 'start' && <Loader2 className="h-4 w-4 animate-spin" />}
              Bắt đầu hiệu chỉnh
            </button>
            <button
              className="flex items-center justify-center gap-2 rounded-xl border border-cyan-300/30 px-5 py-3 text-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={loading || submitting !== null || !backendReady}
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
  if (!(error instanceof Error)) {
    return 'Không thể kết nối backend.'
  }
  if (error.message === 'Failed to fetch') {
    return 'Không kết nối được backend tại 127.0.0.1:8000.'
  }
  return error.message
}

function mediaErrorMessage(error: unknown) {
  if (error instanceof DOMException) {
    if (error.name === 'NotAllowedError') {
      return 'Quyền camera bị từ chối trong trình duyệt.'
    }
    if (error.name === 'NotFoundError') {
      return 'Không tìm thấy thiết bị camera.'
    }
    if (error.name === 'NotReadableError') {
      return 'Camera đang bận bởi ứng dụng khác.'
    }
  }
  return error instanceof Error ? error.message : 'Không mở được camera.'
}
