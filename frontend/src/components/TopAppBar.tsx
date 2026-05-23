import { Activity, Bell, CircleHelp } from 'lucide-react'
import type { RuntimeStatus } from '../types'

type TopAppBarProps = {
  title: string
  runtime: RuntimeStatus
}

export default function TopAppBar({ title, runtime }: TopAppBarProps) {
  return (
    <header className="glass-inner flex h-20 shrink-0 items-center justify-between border-x-0 border-t-0 px-5">
      <div>
        <div className="text-xs uppercase tracking-[0.28em] text-brand-cyan glow-text">ACV Gesture Control</div>
        <h1 className="text-2xl font-semibold text-white">{title}</h1>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden items-center gap-2 rounded-full border border-brand-cyan/20 bg-brand-cyan/10 px-3 py-2 text-sm text-cyan-100 md:flex">
          <Activity className="h-4 w-4" />
          <span>{runtime.trackingStatus}</span>
        </div>
        <div className="rounded-full border border-brand-blue/25 bg-brand-blue/10 px-3 py-2 text-sm font-medium text-blue-100">
          {runtime.currentProfile}
        </div>
        <button className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-white/[0.03] text-slate-300">
          <Bell className="h-4 w-4" />
        </button>
        <button className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-white/[0.03] text-slate-300">
          <CircleHelp className="h-4 w-4" />
        </button>
      </div>
    </header>
  )
}
