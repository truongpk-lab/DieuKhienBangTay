import { Briefcase, Gamepad2, Play, Sparkles } from 'lucide-react'

const profiles = [
  { label: 'Văn phòng', icon: Briefcase },
  { label: 'Giải trí', icon: Play },
  { label: 'Game 2D', icon: Gamepad2 },
  { label: 'Tùy chỉnh', icon: Sparkles },
]

export default function OnboardingView() {
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
            Sẵn sàng hiệu chỉnh
          </div>
        </div>
        <div className="space-y-5">
          <select className="w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-4 py-3 text-white">
            <option>Webcam HD Camera</option>
          </select>
          <div className="grid grid-cols-3 gap-2 rounded-xl bg-white/5 p-1">
            {['Tay trái', 'Tay phải', 'Tự động'].map((item, index) => (
              <button key={item} className={`rounded-lg py-3 ${index === 1 ? 'bg-cyan-300 text-black' : 'text-slate-300'}`}>
                {item}
              </button>
            ))}
          </div>
          <Slider label="Tốc độ chuột" value="1.5x" min={0.1} max={3} step={0.1} defaultValue={1.5} />
          <Slider label="Sensitivity" value="75%" min={0} max={100} step={1} defaultValue={75} />
          <Slider label="Smoothing" value="Mức 3" min={1} max={5} step={1} defaultValue={3} />
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {profiles.map((profile, index) => {
              const Icon = profile.icon
              return (
                <button key={profile.label} className={`rounded-xl border p-4 text-left ${index === 0 ? 'border-cyan-300/60 bg-cyan-300/10' : 'border-white/10 bg-white/[0.03]'}`}>
                  <Icon className="mb-3 h-5 w-5 text-cyan-200" />
                  {profile.label}
                </button>
              )
            })}
          </div>
          <div className="flex gap-3">
            <button className="flex-1 rounded-xl bg-cyan-300 px-5 py-3 font-semibold text-black">Bắt đầu hiệu chỉnh</button>
            <button className="rounded-xl border border-cyan-300/30 px-5 py-3 text-cyan-100">Bỏ qua</button>
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
  defaultValue,
}: {
  label: string
  value: string
  min: number
  max: number
  step: number
  defaultValue: number
}) {
  return (
    <label className="block">
      <div className="mb-2 flex justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="text-cyan-200">{value}</span>
      </div>
      <input className="w-full accent-cyan-300" type="range" min={min} max={max} step={step} defaultValue={defaultValue} />
    </label>
  )
}
