import { Circle, Play, Save, Square } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { getProfile } from '../api/profileApi'
import {
  cancelTrainingSession,
  captureTrainingSample,
  getTrainingSamplePreview,
  getTrainingStatus,
  saveTrainingModel,
  startTrainingSession,
  stopTrainingSession,
  trainGestureModel,
  type TrainingMode,
  type TrainingSamplePreview,
  type TrainingStatus,
} from '../api/trainingApi'
import HandCameraHUD from '../components/HandCameraHUD'
import type { FunctionMapping, Profile } from '../types'

const emptyStatus: TrainingStatus = {
  sessionId: null,
  active: false,
  profileId: 'office',
  functionId: 'drag_drop',
  mode: 'image',
  samples: 0,
  targetSamples: 30,
  progress: 0,
  lastError: null,
  preview: [],
}

export default function TrainingView({ profiles = [] }: { profiles?: Profile[] }) {
  const profileOptions = profiles.length ? profiles : [{ id: 'office', name: 'Văn phòng', description: '' }]
  const [profileId, setProfileId] = useState(profileOptions[0]?.id ?? 'office')
  const [functions, setFunctions] = useState<FunctionMapping[]>([])
  const [functionId, setFunctionId] = useState('drag_drop')
  const [mode, setMode] = useState<TrainingMode>('image')
  const [targetSamples, setTargetSamples] = useState(30)
  const [status, setStatus] = useState<TrainingStatus>(emptyStatus)
  const [preview, setPreview] = useState<TrainingSamplePreview[]>([])
  const [notice, setNotice] = useState('Sẵn sàng thu mẫu.')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    getTrainingStatus().then(setStatus).catch(() => setNotice('Backend chưa kết nối; API huấn luyện chưa sẵn sàng.'))
  }, [])

  useEffect(() => {
    getProfile(profileId)
      .then((profile) => {
        const enabled = (profile.functions ?? []).filter((item) => item.enabled !== false)
        setFunctions(enabled)
        setFunctionId(enabled[0]?.id ?? 'drag_drop')
      })
      .catch(() => setFunctions([]))
  }, [profileId])

  const progress = useMemo(() => Math.min(status.progress || 0, 100), [status.progress])

  async function run(action: () => Promise<TrainingStatus>, message: string) {
    setBusy(true)
    try {
      const next = await action()
      setStatus(next)
      setNotice(next.lastError || message)
      if (next.preview) setPreview(next.preview)
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Yêu cầu huấn luyện thất bại.')
    } finally {
      setBusy(false)
    }
  }

  async function refreshPreview() {
    try {
      const items = await getTrainingSamplePreview()
      setPreview(items)
      setNotice(`Đã tải ${items.length} mẫu xem trước.`)
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Không tải được mẫu xem trước.')
    }
  }

  return (
    <div className="grid gap-5 py-5 xl:grid-cols-[420px_1fr]">
      <div className="glass-panel rounded-2xl p-5">
        <div className="space-y-4">
          <select value={profileId} onChange={(event) => setProfileId(event.target.value)} className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white">
            {profileOptions.map((profile) => (
              <option key={profile.id} value={profile.id}>{profile.name}</option>
            ))}
          </select>
          <select value={functionId} onChange={(event) => setFunctionId(event.target.value)} className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white">
            {(functions.length ? functions : [{ id: 'drag_drop', label: 'Kéo thả', gesture: 'Kẹp kéo-thả', action: 'mouse.drag' }]).map((item) => (
              <option key={item.id} value={item.id}>{item.label}</option>
            ))}
          </select>
          <div className="grid grid-cols-2 gap-2 rounded-xl bg-white/5 p-1">
            <button onClick={() => setMode('image')} className={`rounded-lg py-3 font-semibold ${mode === 'image' ? 'bg-cyan-300 text-black' : 'text-slate-300'}`} type="button">Chụp ảnh</button>
            <button onClick={() => setMode('video')} className={`rounded-lg py-3 font-semibold ${mode === 'video' ? 'bg-cyan-300 text-black' : 'text-slate-300'}`} type="button">Quay video</button>
          </div>
          <input value={targetSamples} onChange={(event) => setTargetSamples(Number(event.target.value))} className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white" min={1} type="number" />
          <div className="rounded-2xl bg-white/[0.03] p-5">
            <div className="mb-3 flex justify-between">
              <span>{status.samples} / {status.targetSamples} mẫu</span>
              <span className="text-cyan-200">{progress}%</span>
            </div>
            <div className="h-3 rounded-full bg-white/10">
              <div className="h-full rounded-full bg-cyan-300 transition-all" style={{ width: `${progress}%` }} />
            </div>
          </div>
          {status.lastError && <div className="rounded-2xl border border-red-300/20 bg-red-400/10 p-4 text-sm text-red-100">{status.lastError}</div>}
          <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 p-4 text-sm text-cyan-100">{notice}</div>
          <div className="max-h-40 overflow-auto rounded-2xl border border-white/10 bg-black/20 p-3 font-mono text-xs text-slate-300">
            {preview.length ? preview.map((sample) => <div key={sample.sampleId}>{sample.sampleId}</div>) : 'Chưa có mẫu xem trước.'}
          </div>
        </div>
      </div>
      <div className="glass-panel rounded-2xl p-5">
        <div className="mb-4 rounded-xl border-l-4 border-cyan-300 bg-cyan-300/5 p-4 text-cyan-50">
          Kẹp ngón tay để giữ, di chuyển tay, sau đó thả ngón để bỏ.
        </div>
        <HandCameraHUD compact showWarnings />
        <div className="mt-5 flex flex-wrap gap-3">
          <button disabled={busy} onClick={() => run(() => startTrainingSession({ profile_id: profileId, function_id: functionId, mode, target_samples: targetSamples }), 'Phiên huấn luyện đã bắt đầu.')} className="inline-flex items-center gap-2 rounded-xl border border-red-300/30 bg-red-400/10 px-4 py-3 text-red-100 disabled:opacity-50" type="button">
            <Circle className="h-4 w-4 fill-current" />
            Ghi hình
          </button>
          <button disabled={busy} onClick={() => run(stopTrainingSession, 'Phiên huấn luyện đã dừng.')} className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-slate-200 disabled:opacity-50" type="button">
            <Square className="h-4 w-4" />
            Dừng
          </button>
          <button disabled={busy || !status.active} onClick={() => run(() => captureTrainingSample({ session_id: status.sessionId ?? undefined }), 'Đã chụp mẫu.')} className="rounded-xl border border-white/10 px-4 py-3 text-slate-200 disabled:opacity-50" type="button">Chụp mẫu</button>
          <button onClick={refreshPreview} className="rounded-xl border border-white/10 px-4 py-3 text-slate-200" type="button">Xem trước mẫu</button>
          <button disabled={busy} onClick={() => run(trainGestureModel, 'Huấn luyện hoàn tất và model đã được ghi vào registry.')} className="inline-flex items-center gap-2 rounded-xl bg-cyan-300 px-4 py-3 font-semibold text-black disabled:opacity-50 sm:ml-auto" type="button">
            <Play className="h-4 w-4" />
            Huấn luyện
          </button>
          <button disabled={busy} onClick={() => run(saveTrainingModel, 'Đã lưu phiên/model.')} className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/30 px-4 py-3 text-cyan-100 disabled:opacity-50" type="button">
            <Save className="h-4 w-4" />
            Lưu
          </button>
          <button disabled={busy} onClick={() => window.confirm('Hủy phiên huấn luyện hiện tại?') && run(cancelTrainingSession, 'Đã hủy phiên huấn luyện.')} className="rounded-xl border border-white/10 px-4 py-3 text-slate-300 disabled:opacity-50" type="button">Hủy</button>
        </div>
      </div>
    </div>
  )
}
