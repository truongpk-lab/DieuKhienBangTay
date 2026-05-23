import { Brain, Gauge, Hand, Layers, MousePointer2, Settings } from 'lucide-react'
import type { AppView } from '../types'

const items: Array<{ id: AppView; label: string; icon: typeof Gauge }> = [
  { id: 'dashboard', label: 'Dashboard', icon: Gauge },
  { id: 'onboarding', label: 'Thiết lập ban đầu', icon: Hand },
  { id: 'config', label: 'Cấu hình', icon: Settings },
  { id: 'training', label: 'Huấn luyện cử chỉ', icon: Brain },
  { id: 'workflow', label: 'Quy trình kéo thả', icon: Layers },
]

type SideNavBarProps = {
  activeView: AppView
  onChange: (view: AppView) => void
}

export default function SideNavBar({ activeView, onChange }: SideNavBarProps) {
  return (
    <aside className="glass-panel hidden w-72 shrink-0 rounded-none border-y-0 border-l-0 p-4 lg:block">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="grid h-11 w-11 place-items-center rounded-2xl bg-brand-cyan/10 text-brand-cyan glow-btn-active">
          <MousePointer2 className="h-5 w-5" />
        </div>
        <div>
          <div className="font-semibold text-white glow-text">ACV Gesture</div>
          <div className="text-xs text-slate-500">Desktop Control UI</div>
        </div>
      </div>

      <nav className="space-y-2">
        {items.map((item) => {
          const Icon = item.icon
          const active = activeView === item.id

          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onChange(item.id)}
              className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-left transition ${
                active
                  ? 'border border-brand-cyan/30 bg-brand-cyan/10 text-cyan-100 glow-btn-active'
                  : 'border border-transparent text-slate-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <Icon className="h-5 w-5" />
              <span>{item.label}</span>
            </button>
          )
        })}
      </nav>
    </aside>
  )
}
