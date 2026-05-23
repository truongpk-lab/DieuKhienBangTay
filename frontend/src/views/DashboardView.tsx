import { Power, Radio, Target } from 'lucide-react'
import { motion } from 'motion/react'
import { useState } from 'react'
import HandCameraHUD from '../components/HandCameraHUD'
import TerminalLog from '../components/TerminalLog'
import type { GestureLog, Profile, RuntimeStatus } from '../types'

const mockProfiles: Profile[] = [
  { id: 'office', name: 'Văn phòng', description: 'Điều hướng desktop và kéo thả' },
  { id: 'entertainment', name: 'Giải trí', description: 'Media control' },
  { id: 'game_2d', name: 'Game 2D', description: 'Action mapping' },
  { id: 'custom', name: 'Tùy chỉnh', description: 'User-defined profile' },
]

const runtime: RuntimeStatus = {
  currentProfile: mockProfiles[0].name,
  currentGesture: 'Pinch',
  currentAction: 'Kéo thả',
  fps: 60,
  accuracy: 98.5,
  trackingStatus: 'Active Tracking',
  latency: 12,
}

const logs: GestureLog[] = [
  { time: '10:42:01', type: 'system', message: 'Camera initialized' },
  { time: '10:42:03', type: 'detection', message: 'Hand detected: Right' },
  { time: '10:42:05', type: 'gesture', message: 'Pinch detected -> drag_start' },
]

export default function DashboardView() {
  const [visibleLogs, setVisibleLogs] = useState(logs)

  return (
    <div className="grid gap-5 py-5 xl:grid-cols-[minmax(0,2fr)_420px]">
      <div className="glass-panel rounded-2xl p-4">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Nguồn Video</h2>
          <span className="rounded-full bg-red-500/15 px-3 py-1 text-xs font-semibold text-red-200">LIVE</span>
        </div>
        <HandCameraHUD />
      </div>
      <div className="space-y-5">
        <div className="glass-panel rounded-2xl p-5">
          <div className="mb-5 flex items-center gap-2 text-cyan-100">
            <Radio className="h-5 w-5" />
            <span>{runtime.trackingStatus}</span>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Metric label="FPS" value={runtime.fps} suffix="" />
            <Metric label="Accuracy" value={runtime.accuracy} suffix="%" />
          </div>
        </div>
        <div className="glass-panel rounded-2xl p-5">
          <Info label="Hồ sơ" value={runtime.currentProfile} />
          <Info label="Cử chỉ" value={runtime.currentGesture} />
          <Info label="Hành động" value={runtime.currentAction} />
          <motion.button
            animate={{ boxShadow: ['0 0 0 0 rgba(239,68,68,0.25)', '0 0 0 22px rgba(239,68,68,0)'] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="mx-auto mt-6 grid h-28 w-28 place-items-center rounded-full bg-red-500/15 text-red-100 ring-8 ring-red-500/5"
          >
            <Power className="h-10 w-10" />
          </motion.button>
        </div>
      </div>
      <div className="xl:col-span-2">
        <TerminalLog logs={visibleLogs} onClear={() => setVisibleLogs([])} />
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
