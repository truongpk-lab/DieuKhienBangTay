import { motion } from 'motion/react'
import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  AlertTriangle,
  BookOpen,
  Briefcase,
  Camera,
  CheckCircle2,
  CircleDot,
  Gamepad2,
  Gauge,
  Hand,
  Keyboard,
  Mouse,
  MousePointer2,
  Play,
  ScrollText,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Zap,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import HandSkeleton from '../components/HandSkeleton'
import type { GestureLog, RuntimeStatus } from '../types'

type GuideMode = {
  id: string
  label: string
  subtitle: string
  icon: LucideIcon
  highlight: string
  difficulty: string
  latency: string
  activeGesture: string
  actionPreview: string
  functions: GuideFunction[]
  practice: string[]
}

type GuideFunction = {
  title: string
  gesture: string
  description: string
  icon: LucideIcon
  tone?: 'cyan' | 'blue' | 'amber' | 'red'
}

const guideModes: GuideMode[] = [
  {
    id: 'office',
    label: 'Văn phòng',
    subtitle: 'Điều hướng tài liệu, cửa sổ và kéo thả file hằng ngày.',
    icon: Briefcase,
    highlight: 'Tối ưu cho thao tác chính xác',
    difficulty: 'Dễ',
    latency: '12ms',
    activeGesture: 'Pinch Index',
    actionPreview: 'Kéo thả file/thư mục',
    functions: [
      { title: 'Di chuyển chuột', gesture: 'Xòe bàn tay', description: 'Giữ lòng bàn tay hướng camera và di chuyển nhẹ để điều khiển con trỏ.', icon: MousePointer2 },
      { title: 'Click trái', gesture: 'Kẹp ngón trỏ', description: 'Chạm ngón cái với ngón trỏ trong một nhịp ngắn để chọn mục.', icon: Mouse },
      { title: 'Kéo thả file', gesture: 'Kẹp giữ rồi thả', description: 'Kẹp để giữ, di chuyển tay tới vị trí đích, sau đó mở ngón để thả.', icon: Hand, tone: 'blue' },
      { title: 'Cuộn trang', gesture: 'Vuốt hai ngón', description: 'Đưa hai ngón lên hoặc xuống để cuộn tài liệu, trình duyệt và bảng dữ liệu.', icon: ScrollText },
    ],
    practice: ['Đặt tay cách camera 40-70cm.', 'Giữ cổ tay ổn định trước khi click.', 'Kẹp và thả dứt khoát khi kéo file.'],
  },
  {
    id: 'entertainment',
    label: 'Giải trí',
    subtitle: 'Điều khiển video, nhạc, tab phát media và âm lượng.',
    icon: Play,
    highlight: 'Tối ưu cho thao tác nhanh',
    difficulty: 'Dễ',
    latency: '14ms',
    activeGesture: 'Open Close Palm',
    actionPreview: 'Play/Pause',
    functions: [
      { title: 'Play/Pause', gesture: 'Đóng mở bàn tay', description: 'Mở rồi nắm nhẹ bàn tay để dừng hoặc tiếp tục phát nội dung.', icon: Play },
      { title: 'Bài tiếp theo', gesture: 'Vuốt phải', description: 'Vuốt tay sang phải để chuyển bài, video hoặc nội dung kế tiếp.', icon: Zap, tone: 'blue' },
      { title: 'Bài trước đó', gesture: 'Vuốt trái', description: 'Vuốt tay sang trái khi muốn quay lại nội dung trước.', icon: Keyboard },
      { title: 'Tăng/giảm âm lượng', gesture: 'Vuốt lên/xuống', description: 'Di chuyển hai ngón theo trục dọc để tinh chỉnh âm lượng.', icon: SlidersHorizontal },
    ],
    practice: ['Dùng cử chỉ lớn hơn khi ngồi xa màn hình.', 'Tránh che khuất đầu ngón tay khi vuốt.', 'Chờ badge phản hồi sáng trước khi lặp thao tác.'],
  },
  {
    id: 'game_2d',
    label: 'Game 2D',
    subtitle: 'Ánh xạ hành động nhanh cho platformer, arcade và game luyện phản xạ.',
    icon: Gamepad2,
    highlight: 'Tối ưu cho phản hồi nhanh',
    difficulty: 'Trung bình',
    latency: '10ms',
    activeGesture: 'Rapid Punch',
    actionPreview: 'Tấn công trong game',
    functions: [
      { title: 'Di chuyển trái/phải', gesture: 'Nghiêng tay', description: 'Nghiêng bàn tay theo hướng cần di chuyển để giữ nhịp điều khiển.', icon: Gamepad2, tone: 'blue' },
      { title: 'Nhảy', gesture: 'Bật ngón trỏ lên', description: 'Nâng ngón trỏ nhanh để kích hoạt hành động nhảy.', icon: Zap },
      { title: 'Tấn công', gesture: 'Đấm nhanh', description: 'Đưa nắm tay về trước trong vùng nhận diện để gửi lệnh tấn công.', icon: ShieldCheck, tone: 'red' },
      { title: 'Dash', gesture: 'Vuốt ngang nhanh', description: 'Vuốt cổ tay sang trái hoặc phải để lướt ngắn trong game.', icon: Gauge, tone: 'amber' },
    ],
    practice: ['Ưu tiên nền sáng đều phía sau tay.', 'Giữ cử chỉ ngắn, rõ và có điểm dừng.', 'Tập riêng từng hành động trước khi chơi thật.'],
  },
  {
    id: 'custom',
    label: 'Tùy chỉnh',
    subtitle: 'Bộ thao tác cá nhân cho workflow riêng, macro và phím tắt đặc biệt.',
    icon: SlidersHorizontal,
    highlight: 'Tối ưu cho cá nhân hóa',
    difficulty: 'Nâng cao',
    latency: 'Tùy cấu hình',
    activeGesture: 'Custom Gesture',
    actionPreview: 'Tác vụ tự định nghĩa',
    functions: [
      { title: 'Macro cá nhân', gesture: 'Gesture tự train', description: 'Gán một cử chỉ đã huấn luyện với chuỗi phím hoặc hành động riêng.', icon: Sparkles },
      { title: 'Phím tắt ứng dụng', gesture: 'Ba ngón trái/phải', description: 'Kích hoạt hotkey như chuyển workspace, bật công cụ hoặc mở menu.', icon: Keyboard, tone: 'blue' },
      { title: 'Điều khiển cửa sổ', gesture: 'Kẹp giữ', description: 'Dùng thao tác giữ để kéo cửa sổ hoặc chọn vùng làm việc.', icon: MousePointer2 },
      { title: 'Quy tắc an toàn', gesture: 'Confidence cao', description: 'Chỉ chạy lệnh khi độ tin cậy vượt ngưỡng để tránh thao tác nhầm.', icon: ShieldCheck, tone: 'amber' },
    ],
    practice: ['Đặt tên gesture rõ ràng trong cấu hình.', 'Train tối thiểu 30-50 mẫu cho mỗi tác vụ.', 'Kiểm thử bằng ứng dụng ít rủi ro trước.'],
  },
]

const quickChecklist = [
  'Camera nhìn rõ cổ tay và đầu ngón tay.',
  'Ánh sáng đều, không ngược sáng mạnh.',
  'Tay nằm trong vùng HUD trước khi thao tác.',
  'Chọn đúng chế độ theo mục đích sử dụng.',
]

const commonIssues = [
  { title: 'Con trỏ rung', detail: 'Tăng smoothing hoặc giảm tốc độ chuột trong phần cấu hình.', icon: Gauge },
  { title: 'Click nhầm', detail: 'Kẹp ngón ngắn hơn và giữ tay ổn định trước khi chạm.', icon: AlertTriangle },
  { title: 'Mất tracking', detail: 'Đưa tay về giữa khung hình và tránh che các điểm khớp.', icon: Camera },
]

export default function WorkflowView({ runtime, logs = [] }: { runtime?: RuntimeStatus; logs?: GestureLog[] }) {
  const [activeModeId, setActiveModeId] = useState(guideModes[0].id)
  const activeMode = guideModes.find((mode) => mode.id === activeModeId) ?? guideModes[0]
  const ActiveIcon = activeMode.icon
  const recentGuideLogs = useMemo(
    () => logs.filter((log) => /pinch|drag|gesture|hand|tracking/i.test(log.message)).slice(-3),
    [logs],
  )

  return (
    <div className="space-y-5 py-5">
      <section className="glass-panel overflow-hidden rounded-3xl p-5 sm:p-6">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-brand-cyan/20 bg-brand-cyan/10 px-3 py-1 text-xs uppercase tracking-[0.24em] text-cyan-100">
              <BookOpen className="h-4 w-4" />
              Trung tâm hướng dẫn
            </div>
            <h2 className="glow-text mt-4 text-3xl font-semibold text-white sm:text-4xl">Hướng dẫn thao tác</h2>
            <p className="mt-3 text-sm leading-6 text-slate-400 sm:text-base">
              Chọn chế độ, xem cử chỉ mẫu và luyện theo từng bước để dùng ACV Gesture Control ổn định hơn trong công việc, giải trí và game.
            </p>
          </div>

          <div className="grid gap-2 sm:grid-cols-2 xl:min-w-[420px]">
            {guideModes.map((mode) => {
              const Icon = mode.icon
              const active = mode.id === activeMode.id
              return (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setActiveModeId(mode.id)}
                  className={`flex items-center gap-3 rounded-2xl border px-4 py-3 text-left transition ${
                    active
                      ? 'border-brand-cyan/40 bg-brand-cyan/15 text-cyan-100 glow-btn-active'
                      : 'border-white/10 bg-white/[0.03] text-slate-300 hover:border-brand-cyan/25 hover:bg-white/[0.06]'
                  }`}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  <span className="font-medium">{mode.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="glass-panel rounded-3xl p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-brand-cyan/10 text-brand-cyan glow-btn-active">
                  <ActiveIcon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="text-2xl font-semibold text-white">{activeMode.label}</h3>
                  <p className="text-sm text-slate-400">{activeMode.highlight}</p>
                </div>
              </div>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300">{activeMode.subtitle}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge label={`Độ khó: ${activeMode.difficulty}`} />
              <Badge label={`Latency: ${runtime?.latency ?? activeMode.latency}${typeof runtime?.latency === 'number' ? 'ms' : ''}`} />
              <Badge label={runtime?.trackingStatus ?? 'Sensor: Sẵn sàng'} />
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {activeMode.functions.map((item) => (
              <FunctionCard key={item.title} item={item} />
            ))}
          </div>
        </div>

        <div className="glass-panel relative overflow-hidden rounded-3xl p-5 sm:p-6">
          <div className="absolute inset-0 obsidian-grid opacity-50" />
          <div className="relative">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-xs uppercase tracking-[0.24em] text-brand-cyan">Mô phỏng bàn tay</div>
                <h3 className="mt-2 text-xl font-semibold text-white">{activeMode.actionPreview}</h3>
              </div>
              <div className="rounded-full border border-emerald-300/25 bg-emerald-300/10 px-3 py-1 text-sm text-emerald-100">Sensor: Active</div>
            </div>

            <div className="relative mx-auto mt-8 aspect-square max-w-[360px]">
              <motion.div
                className="absolute inset-8 rounded-full border border-brand-cyan/20"
                animate={{ scale: [0.92, 1.12], opacity: [0.75, 0] }}
                transition={{ duration: 1.8, repeat: Infinity }}
              />
              <motion.div
                className="absolute inset-0 rounded-full border border-brand-blue/10"
                animate={{ rotate: 360 }}
                transition={{ duration: 18, repeat: Infinity, ease: 'linear' }}
              />
              <div className="absolute inset-10">
                <HandSkeleton />
              </div>
              <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 items-center gap-2 rounded-full border border-brand-cyan/20 bg-black/50 px-3 py-2 text-xs text-cyan-100 backdrop-blur">
                <CircleDot className="h-4 w-4" />
                {activeMode.activeGesture}
              </div>
            </div>

            <div className="mt-5 grid gap-2 rounded-2xl border border-white/10 bg-black/25 p-4">
              {activeMode.practice.map((step, index) => (
                <div key={step} className="flex items-start gap-3 text-sm text-slate-300">
                  <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full border border-brand-cyan/25 bg-brand-cyan/10 text-xs text-cyan-100">{index + 1}</span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <InfoPanel title="Checklist trước khi dùng" icon={CheckCircle2}>
          <div className="grid gap-3">
            {quickChecklist.map((item) => (
              <div key={item} className="flex items-start gap-3 text-sm text-slate-300">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-cyan-200" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </InfoPanel>

        <InfoPanel title="Lỗi thường gặp" icon={AlertTriangle}>
          <div className="grid gap-3">
            {commonIssues.map((issue) => {
              const Icon = issue.icon
              return (
                <div key={issue.title} className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
                  <div className="flex items-center gap-2 text-sm font-medium text-white">
                    <Icon className="h-4 w-4 text-amber-200" />
                    {issue.title}
                  </div>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{issue.detail}</p>
                </div>
              )
            })}
          </div>
        </InfoPanel>

        <InfoPanel title="Tín hiệu gần đây" icon={Sparkles}>
          <div className="grid gap-2 font-mono text-xs text-slate-300">
            {(recentGuideLogs.length ? recentGuideLogs : [{ time: 'demo', message: 'Sẵn sàng nhận diện cử chỉ trong chế độ hướng dẫn.' }]).map((log) => (
              <div key={`${log.time}-${log.message}`} className="rounded-xl border border-brand-cyan/10 bg-brand-cyan/5 px-3 py-2">
                <span className="text-cyan-200">{log.time}</span>
                <span className="ml-2">{log.message}</span>
              </div>
            ))}
          </div>
        </InfoPanel>
      </section>
    </div>
  )
}

function Badge({ label }: { label: string }) {
  return <span className="rounded-full border border-brand-cyan/20 bg-brand-cyan/10 px-3 py-1 text-sm text-cyan-100">{label}</span>
}

function FunctionCard({ item }: { item: GuideFunction }) {
  const Icon = item.icon
  const toneClass =
    item.tone === 'red'
      ? 'border-red-300/20 bg-red-300/10 text-red-100'
      : item.tone === 'amber'
        ? 'border-amber-300/20 bg-amber-300/10 text-amber-100'
        : item.tone === 'blue'
          ? 'border-brand-blue/25 bg-brand-blue/10 text-blue-100'
          : 'border-brand-cyan/20 bg-brand-cyan/10 text-cyan-100'

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 transition hover:border-brand-cyan/25 hover:bg-white/[0.06]">
      <div className={`grid h-11 w-11 place-items-center rounded-xl border ${toneClass}`}>
        <Icon className="h-5 w-5" />
      </div>
      <h4 className="mt-4 text-base font-semibold text-white">{item.title}</h4>
      <div className="mt-2 inline-flex rounded-full border border-white/10 bg-black/25 px-2 py-1 font-mono text-xs text-cyan-100">{item.gesture}</div>
      <p className="mt-3 text-sm leading-6 text-slate-400">{item.description}</p>
    </div>
  )
}

function InfoPanel({ title, icon: Icon, children }: { title: string; icon: LucideIcon; children: ReactNode }) {
  return (
    <div className="glass-panel rounded-3xl p-5">
      <div className="mb-4 flex items-center gap-3">
        <div className="grid h-10 w-10 place-items-center rounded-xl bg-brand-cyan/10 text-brand-cyan">
          <Icon className="h-5 w-5" />
        </div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      {children}
    </div>
  )
}
