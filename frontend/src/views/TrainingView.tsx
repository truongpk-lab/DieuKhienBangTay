import { Circle, Play, Save, Square } from 'lucide-react'
import HandCameraHUD from '../components/HandCameraHUD'

export default function TrainingView() {
  return (
    <div className="grid gap-5 py-5 xl:grid-cols-[420px_1fr]">
      <div className="glass-panel rounded-2xl p-5">
        <div className="space-y-4">
          <select className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white">
            <option>Văn phòng</option>
          </select>
          <select className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white">
            <option>Kéo thả</option>
            <option>Click đơn</option>
          </select>
          <div className="grid grid-cols-2 gap-2 rounded-xl bg-white/5 p-1">
            <button className="rounded-lg bg-cyan-300 py-3 font-semibold text-black">Chụp ảnh</button>
            <button className="rounded-lg py-3 text-slate-300">Quay video</button>
          </div>
          <input className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white" defaultValue={30} type="number" />
          <div className="rounded-2xl bg-white/[0.03] p-5">
            <div className="mb-3 flex justify-between">
              <span>24 / 30 mẫu</span>
              <span className="text-cyan-200">80%</span>
            </div>
            <div className="h-3 rounded-full bg-white/10">
              <div className="h-full w-4/5 rounded-full bg-cyan-300" />
            </div>
          </div>
        </div>
      </div>
      <div className="glass-panel rounded-2xl p-5">
        <div className="mb-4 rounded-xl border-l-4 border-cyan-300 bg-cyan-300/5 p-4 text-cyan-50">
          Kẹp ngón tay để giữ, di chuyển tay, sau đó thả ngón để bỏ.
        </div>
        <HandCameraHUD compact />
        <div className="mt-5 flex flex-wrap gap-3">
          <button className="inline-flex items-center gap-2 rounded-xl border border-red-300/30 bg-red-400/10 px-4 py-3 text-red-100">
            <Circle className="h-4 w-4 fill-current" />
            Ghi hình
          </button>
          <button className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-slate-200">
            <Square className="h-4 w-4" />
            Dừng
          </button>
          <button className="rounded-xl border border-white/10 px-4 py-3 text-slate-200">Xem trước mẫu</button>
          <button className="ml-auto inline-flex items-center gap-2 rounded-xl bg-cyan-300 px-4 py-3 font-semibold text-black">
            <Play className="h-4 w-4" />
            Huấn luyện
          </button>
          <button className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/30 px-4 py-3 text-cyan-100">
            <Save className="h-4 w-4" />
            Lưu
          </button>
          <button className="rounded-xl border border-white/10 px-4 py-3 text-slate-300">Hủy</button>
        </div>
      </div>
    </div>
  )
}
