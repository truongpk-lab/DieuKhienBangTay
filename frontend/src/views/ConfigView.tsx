import { Edit3, Mouse, MousePointerClick, Plus, Save, ScrollText, Swords, Tv } from 'lucide-react'
import type { FunctionMapping } from '../types'

const mappings: FunctionMapping[] = [
  { id: 'move', label: 'Di chuyển chuột', gesture: 'Open Palm Move' },
  { id: 'left', label: 'Click trái', gesture: 'Pinch Index' },
  { id: 'right', label: 'Click phải', gesture: 'Pinch Middle' },
  { id: 'drag', label: 'Kéo thả file/thư mục', gesture: 'Closed Fist Hold' },
  { id: 'scroll', label: 'Cuộn trang', gesture: 'Two Finger Swipe' },
  { id: 'tab', label: 'Chuyển tab', gesture: 'Three Finger Left/Right' },
  { id: 'play', label: 'Play/Pause', gesture: 'Open Close Palm' },
  { id: 'attack', label: 'Tấn công trong game', gesture: 'Rapid Punch', tone: 'red' },
]

const icons = [Mouse, MousePointerClick, MousePointerClick, Mouse, ScrollText, Tv, Tv, Swords]

export default function ConfigView() {
  return (
    <div className="space-y-5 py-5">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <p className="max-w-2xl text-slate-400">Gán chức năng máy tính với gesture/action theo từng mục đích sử dụng.</p>
        <select className="rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white">
          <option>Desktop Navigation</option>
          <option>Game 2D (Platformer)</option>
          <option>Presentation Mode</option>
        </select>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {mappings.map((mapping, index) => {
          const Icon = icons[index]
          const red = mapping.tone === 'red'
          return (
            <div key={mapping.id} className={`glass-panel rounded-2xl p-5 ${red ? 'border-red-300/25' : ''}`}>
              <div className={`mb-5 grid h-12 w-12 place-items-center rounded-xl ${red ? 'bg-red-400/10 text-red-200' : 'bg-cyan-300/10 text-cyan-200'}`}>
                <Icon className="h-6 w-6" />
              </div>
              <h2 className="text-lg font-semibold">{mapping.label}</h2>
              <p className="mt-2 text-sm text-slate-400">{mapping.gesture}</p>
              <button className="mt-5 inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200">
                <Edit3 className="h-4 w-4" />
                Chỉnh sửa
              </button>
            </div>
          )
        })}
        <button className="grid min-h-52 place-items-center rounded-2xl border border-dashed border-cyan-300/30 bg-cyan-300/5 text-cyan-100">
          <span className="grid place-items-center gap-3">
            <Plus className="h-10 w-10" />
            Thêm mới
          </span>
        </button>
      </div>
      <div className="sticky bottom-4 flex justify-end gap-3 rounded-2xl border border-white/10 bg-black/55 p-4 backdrop-blur">
        <button className="rounded-xl border border-white/10 px-5 py-3 text-slate-300">Hủy</button>
        <button className="inline-flex items-center gap-2 rounded-xl bg-cyan-300 px-5 py-3 font-semibold text-black">
          <Save className="h-4 w-4" />
          LƯU CẤU HÌNH
        </button>
      </div>
    </div>
  )
}
