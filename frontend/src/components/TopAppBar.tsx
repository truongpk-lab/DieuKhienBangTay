import { Activity, Bell, CircleHelp } from 'lucide-react'
import type { RuntimeStatus } from '../types'

type TopAppBarProps = {
  title: string
  runtime: RuntimeStatus
  backendOnline: boolean
}

export default function TopAppBar({ title, runtime, backendOnline }: TopAppBarProps) {
  return (
    <header className="glass-inner flex min-h-20 shrink-0 items-center justify-between gap-3 border-x-0 border-t-0 px-4 py-3 sm:px-5">
      <div className="min-w-0">
        <div className="text-xs uppercase tracking-[0.28em] text-brand-cyan glow-text">ACV Gesture Control</div>
        <h1 className="truncate text-xl font-semibold text-white sm:text-2xl">{title}</h1>
      </div>

      <div className="flex shrink-0 items-center gap-2 sm:gap-3">
        <div className="hidden items-center gap-2 rounded-full border border-brand-cyan/20 bg-brand-cyan/10 px-3 py-2 text-sm text-cyan-100 md:flex">
          <Activity className="h-4 w-4" />
          <span>{runtime.trackingStatus}</span>
        </div>
        <div className="hidden rounded-full border border-brand-blue/25 bg-brand-blue/10 px-3 py-2 text-sm font-medium text-blue-100 sm:block">
          {runtime.currentProfile}
        </div>
        <div className={`hidden rounded-full border px-3 py-2 text-sm font-medium lg:block ${backendOnline ? 'border-emerald-300/25 bg-emerald-300/10 text-emerald-100' : 'border-amber-300/25 bg-amber-300/10 text-amber-100'}`}>
          {backendOnline ? 'Backend online' : 'Backend offline'}
        </div>
        <button type="button" className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-white/[0.03] text-slate-300">
          <Bell className="h-4 w-4" />
        </button>
        <button type="button" className="grid h-10 w-10 place-items-center rounded-xl border border-white/10 bg-white/[0.03] text-slate-300">
          <CircleHelp className="h-4 w-4" />
        </button>
      </div>
    </header>
  )
}
