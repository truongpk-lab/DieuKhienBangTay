import {
  AlertTriangle,
  Eye,
  EyeOff,
  Loader2,
  Mic,
  MicOff,
  Pause,
  Play,
  Power,
  Radio,
  RotateCcw,
  Settings,
  ShieldAlert,
  Target,
  type LucideIcon,
} from 'lucide-react'
import { motion } from 'motion/react'
import { useState } from 'react'
import { sendVoiceCommand } from '../api/aiApi'
import { emergencyStopApp, minimizeAppWithFallback, showAppWithFallback } from '../api/appControlApi'
import { activateProfile } from '../api/profileApi'
import { clearGestureLogs, getRuntimeStatus, pauseRuntime, recenterRuntime, resumeRuntime, startRuntime, stopRuntime } from '../api/runtimeApi'
import { startMicrophone, stopMicrophone } from '../api/settingsApi'
import HandCameraHUD from '../components/HandCameraHUD'
import TerminalLog from '../components/TerminalLog'
import type { GestureLog, Profile, RuntimeStatus } from '../types'

type DashboardViewProps = {
  runtime: RuntimeStatus
  logs: GestureLog[]
  profiles: Profile[]
  onRuntimeChange: (runtime: RuntimeStatus) => void
  onLogsChange: (logs: GestureLog[]) => void
  onOpenSettings: () => void
}

type DashboardAction = 'runtime' | 'clearLogs' | 'pause' | 'recenter' | 'visibility' | 'emergency' | 'profile' | 'mic' | 'voice' | null

export default function DashboardView({
  runtime,
  logs,
  profiles,
  onRuntimeChange,
  onLogsChange,
  onOpenSettings,
}: DashboardViewProps) {
  const [activeAction, setActiveAction] = useState<DashboardAction>(null)
  const [appHidden, setAppHidden] = useState(false)
  const [statusMessage, setStatusMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [voiceText, setVoiceText] = useState('')
  const isBusy = activeAction !== null
  const runtimeActive = Boolean(runtime.active)
  const runtimePaused = runtime.mode === 'paused'
  const micActive = runtime.micStatus === 'Microphone active'

  const visibleLogs = logs

  function syncLogs(nextLogs: GestureLog[]) {
    onLogsChange(nextLogs)
  }

  function appendLocalLog(message: string) {
    const log: GestureLog = {
      time: new Date().toLocaleTimeString('en-GB', { hour12: false }),
      type: 'system',
      message,
    }
    syncLogs([...visibleLogs, log])
  }

  async function runAction(action: Exclude<DashboardAction, null>, handler: () => Promise<void>) {
    if (isBusy) {
      return
    }

    setActiveAction(action)
    setStatusMessage(null)
    setErrorMessage(null)

    try {
      await handler()
    } finally {
      setActiveAction(null)
    }
  }

  async function toggleRuntime() {
    await runAction('runtime', async () => {
      try {
        const nextRuntime = runtimeActive ? await stopRuntime() : await startRuntime()
        onRuntimeChange(nextRuntime)

        const visibilityResult = nextRuntime.active ? await minimizeAppWithFallback() : await showAppWithFallback()
        setAppHidden(Boolean(nextRuntime.active && visibilityResult.data.success))
        setStatusMessage(visibilityResult.data.message)
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'Backend/runtime lỗi; không bật trạng thái giả.')
      }
    })
  }

  async function clearLogs() {
    await runAction('clearLogs', async () => {
      try {
        syncLogs(await clearGestureLogs())
        setStatusMessage('Đã xóa nhật ký cử chỉ trên backend.')
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'Backend chưa kết nối; không xóa log giả trên UI.')
      }
    })
  }

  async function togglePause() {
    await runAction('pause', async () => {
      try {
        const nextRuntime = runtimePaused ? await resumeRuntime() : await pauseRuntime()
        onRuntimeChange(nextRuntime)
        setStatusMessage(runtimePaused ? 'Đã tiếp tục runtime.' : 'Đã tạm dừng runtime.')
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'Backend chưa kết nối; tạm dừng/tiếp tục cần API thật.')
      }
    })
  }

  async function recenter() {
    await runAction('recenter', async () => {
      try {
        onRuntimeChange(await recenterRuntime())
        setStatusMessage('Đã gửi lệnh căn lại/hiệu chỉnh tới backend.')
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'Backend chưa kết nối; căn lại cần API thật.')
      }
    })
  }

  async function toggleVisibility() {
    await runAction('visibility', async () => {
      const result = appHidden ? await showAppWithFallback() : await minimizeAppWithFallback()
      setAppHidden(!appHidden && result.data.success)
      setStatusMessage(result.data.message)
      if (result.fromFallback) {
        setErrorMessage('Không có desktop shell; hãy thao tác cửa sổ thủ công.')
      }
    })
  }

  async function emergencyStop() {
    await runAction('emergency', async () => {
      try {
        const result = await emergencyStopApp()
        if (!result.ok) {
          throw new Error('Dừng khẩn cấp thất bại')
        }
        onRuntimeChange(await stopRuntime())
        await showAppWithFallback()
        setAppHidden(false)
        setStatusMessage('Đã dừng runtime và hiện lại ứng dụng.')
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'Backend chưa kết nối; dừng khẩn cấp cần backend thật.')
      }
    })
  }

  async function switchProfile(profileId: string) {
    await runAction('profile', async () => {
      const selectedProfile = profiles.find((profile) => profile.id === profileId)
      try {
        const profile = await activateProfile(profileId)
        onRuntimeChange({
          ...runtime,
          currentProfileId: profile.id,
          currentProfile: profile.name,
        })
        setStatusMessage(`Đã kích hoạt hồ sơ ${profile.name}.`)
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : `Không thể đổi hồ sơ ${selectedProfile?.name ?? profileId}.`)
      }
    })
  }

  async function toggleMic() {
    await runAction('mic', async () => {
      try {
        const status = micActive ? await stopMicrophone() : await startMicrophone()
        setStatusMessage(status.status)
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'Không thể điều khiển microphone.')
      }
    })
  }

  async function runVoiceCommand() {
    if (!voiceText.trim()) {
      setErrorMessage('Nhập lệnh giọng nói dạng text để gửi Gemini, hoặc bật mic cho pipeline voice.')
      return
    }
    await runAction('voice', async () => {
      try {
        const result = await sendVoiceCommand(voiceText.trim(), true)
        setStatusMessage(result.message)
        appendLocalLog(`Gemini: ${result.intent ?? 'unknown'} (${result.confidence.toFixed(2)})`)
        const nextRuntime = result.executed ? await getRuntimeStatus() : runtime
        onRuntimeChange(nextRuntime)
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : 'Lệnh Gemini thất bại.')
      }
    })
  }

  return (
    <div className="grid gap-5 py-5 xl:grid-cols-[minmax(0,2fr)_420px]">
      <div className="glass-panel rounded-2xl p-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Nguồn Video</h2>
          <span className="rounded-full bg-red-500/15 px-3 py-1 text-xs font-semibold text-red-200">LIVE</span>
        </div>
        <HandCameraHUD landmarks={runtime.handLandmarks} />
      </div>
      <div className="space-y-5">
        <div className="glass-panel rounded-2xl p-5">
          <div className="mb-5 flex items-center gap-2 text-cyan-100">
            <Radio className="h-5 w-5" />
            <span>{runtime.trackingStatus}</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Metric label="FPS" value={runtime.fps} suffix="" />
            <Metric label="Độ chính xác" value={runtime.accuracy} suffix="%" />
          </div>
        </div>
        <div className="glass-panel rounded-2xl p-5">
          <Info label="Hồ sơ" value={runtime.currentProfile} />
          <Info label="Cử chỉ" value={runtime.currentGesture} />
          <Info label="Hành động" value={runtime.currentAction} />
          <Info label="Mic" value={runtime.micStatus ?? 'Micro đang nghỉ'} />
          <Info label="AI" value={runtime.aiStatus ?? 'Gemini đang tắt'} />
          <label className="mt-4 block text-xs font-semibold uppercase text-slate-500">Đổi hồ sơ nhanh</label>
          <select
            value={runtime.currentProfileId ?? profiles[0]?.id ?? 'office'}
            onChange={(event) => switchProfile(event.target.value)}
            disabled={isBusy}
            className="mt-2 w-full rounded-xl border border-cyan-300/15 bg-white/5 px-3 py-3 text-sm text-slate-100 outline-none disabled:cursor-wait disabled:opacity-60"
          >
            {profiles.map((profile) => (
              <option key={profile.id} value={profile.id} className="bg-[#131315]">
                {profile.name}
              </option>
            ))}
          </select>
          <div className="mt-4 grid grid-cols-3 gap-2 text-center text-xs font-semibold">
            <span className="rounded-xl border border-cyan-300/20 bg-cyan-300/10 px-2 py-2 text-cyan-100">{runtime.handStatus ?? 'Tay đang nghỉ'}</span>
            <span className="rounded-xl border border-blue-300/20 bg-blue-300/10 px-2 py-2 text-blue-100">{runtime.cameraStatus ?? 'Camera đang nghỉ'}</span>
            <span className="rounded-xl border border-emerald-300/20 bg-emerald-300/10 px-2 py-2 text-emerald-100">{runtime.commandConfidence ? `${Math.round(runtime.commandConfidence * 100)}% giọng nói` : 'Sẵn sàng nhận giọng nói'}</span>
          </div>
          {(statusMessage || errorMessage) && (
            <div className="mt-4 flex gap-3 rounded-xl border border-cyan-300/15 bg-cyan-300/10 p-3 text-sm text-cyan-50">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-cyan-200" />
              <span>{errorMessage ?? statusMessage}</span>
            </div>
          )}
          <motion.button
            type="button"
            onClick={toggleRuntime}
            disabled={isBusy}
            aria-label={runtime.active ? 'Dừng runtime' : 'Bật runtime'}
            animate={{ boxShadow: ['0 0 0 0 rgba(239,68,68,0.25)', '0 0 0 22px rgba(239,68,68,0)'] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className={`mx-auto mt-6 grid h-28 w-28 place-items-center rounded-full ring-8 transition disabled:cursor-wait disabled:opacity-60 ${runtimeActive ? 'bg-red-500/15 text-red-100 ring-red-500/5' : 'bg-cyan-300/15 text-cyan-100 ring-cyan-300/5'}`}
          >
            {activeAction === 'runtime' ? <Loader2 className="h-10 w-10 animate-spin" /> : <Power className="h-10 w-10" />}
          </motion.button>
          <div className="mt-5 grid grid-cols-2 gap-2">
            <ActionButton
              label={runtimePaused ? 'Tiếp tục' : 'Tạm dừng'}
              icon={runtimePaused ? Play : Pause}
              onClick={togglePause}
              loading={activeAction === 'pause'}
              disabled={!runtimeActive || isBusy}
            />
            <ActionButton
              label="Căn lại"
              icon={RotateCcw}
              onClick={recenter}
              loading={activeAction === 'recenter'}
              disabled={!runtimeActive || isBusy}
            />
            <ActionButton
              label={appHidden ? 'Hiện app' : 'Ẩn app'}
              icon={appHidden ? Eye : EyeOff}
              onClick={toggleVisibility}
              loading={activeAction === 'visibility'}
              disabled={isBusy}
            />
            <ActionButton
              label={micActive ? 'Tắt mic' : 'Bật mic'}
              icon={micActive ? MicOff : Mic}
              onClick={toggleMic}
              loading={activeAction === 'mic'}
              disabled={isBusy}
            />
            <ActionButton label="Cài đặt" icon={Settings} onClick={onOpenSettings} disabled={isBusy} />
            <div className="col-span-2 grid gap-2 sm:grid-cols-[1fr_auto]">
              <input
                value={voiceText}
                onChange={(event) => setVoiceText(event.target.value)}
                placeholder='Ví dụ: "dừng điều khiển"'
                className="min-h-11 rounded-xl border border-cyan-300/15 bg-white/5 px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-500"
              />
              <button
                type="button"
                disabled={isBusy || !voiceText.trim()}
                onClick={runVoiceCommand}
                className="rounded-xl bg-cyan-300 px-4 py-2 text-sm font-semibold text-black disabled:cursor-not-allowed disabled:opacity-50"
              >
                {activeAction === 'voice' ? 'Đang gửi' : 'Gemini'}
              </button>
            </div>
            <button
              type="button"
              onClick={emergencyStop}
              disabled={isBusy}
              className="col-span-2 flex items-center justify-center gap-2 rounded-xl border border-red-300/25 bg-red-500/10 px-3 py-3 text-sm font-semibold text-red-100 transition hover:bg-red-500/15 disabled:cursor-wait disabled:opacity-60"
            >
              {activeAction === 'emergency' ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldAlert className="h-4 w-4" />}
              Dừng khẩn cấp
            </button>
          </div>
        </div>
      </div>
      <div className="xl:col-span-2">
        <TerminalLog
          logs={visibleLogs}
          onClear={clearLogs}
          clearDisabled={isBusy}
          clearLabel={activeAction === 'clearLogs' ? 'Đang xóa' : 'Xóa'}
        />
      </div>
    </div>
  )
}

function Metric({ label, value, suffix }: { label: string; value: number; suffix: string }) {
  return (
    <div className="glass-inner rounded-xl p-4">
      <div className="mb-3 flex items-center gap-2 text-slate-400">
        <Target className="h-4 w-4" />
        <span className="text-sm">{label}</span>
      </div>
      <div className="text-3xl font-semibold text-cyan-100">
        {value}
        {suffix}
      </div>
      <div className="mt-3 h-2 rounded-full bg-white/10">
        <div className="h-full rounded-full bg-cyan-300" style={{ width: `${Math.min(value, 100)}%` }} />
      </div>
    </div>
  )
}

function Info({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-white/10 py-3">
      <span className="text-slate-400">{label}</span>
      <span className="font-semibold text-white">{value}</span>
    </div>
  )
}

function ActionButton({
  label,
  icon: Icon,
  onClick,
  loading = false,
  disabled = false,
}: {
  label: string
  icon: LucideIcon
  onClick: () => void
  loading?: boolean
  disabled?: boolean
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className="flex min-h-11 items-center justify-center gap-2 rounded-xl border border-cyan-300/15 bg-white/5 px-3 py-2 text-sm font-semibold text-slate-100 transition hover:border-cyan-300/35 hover:bg-cyan-300/10 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Icon className="h-4 w-4" />}
      <span>{label}</span>
    </button>
  )
}
