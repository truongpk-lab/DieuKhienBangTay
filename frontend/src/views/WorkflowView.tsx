import { motion } from 'motion/react'
import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  AlertTriangle,
  BookOpen,
  Briefcase,
  Camera,
  CheckCircle2,
  CircleDot,
  Copy,
  Gamepad2,
  Gauge,
  Hand,
  Keyboard,
  Maximize2,
  Mouse,
  MousePointer2,
  Music2,
  PanelTop,
  Play,
  ScrollText,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Zap,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { getProfile, type ProfileDetail } from '../api/profileApi'
import HandSkeleton from '../components/HandSkeleton'
import {
  configProfiles,
  getLocalProfileDetail,
  mergeCatalogFunctions,
  type ConfigProfileId,
} from '../config/actionCatalog'
import type { FunctionMapping, GestureLog, Profile, RuntimeStatus } from '../types'

type GuideModeMeta = {
  icon: LucideIcon
  highlight: string
  difficulty: string
  latency: string
  practice: string[]
}

type GuideFunction = {
  title: string
  gesture: string
  description: string
  icon: LucideIcon
  tone?: 'cyan' | 'blue' | 'amber' | 'red'
  action: string
  gestureEvent?: string
}

const guideModeMeta: Record<ConfigProfileId, GuideModeMeta> = {
  office: {
    icon: Briefcase,
    highlight: 'Tối ưu cho thao tác chính xác',
    difficulty: 'Dễ',
    latency: '12ms',
    practice: ['Đặt tay cách camera 40-70cm.', 'Giữ cổ tay ổn định trước khi click.', 'Kẹp và thả dứt khoát khi kéo file.'],
  },
  entertainment: {
    icon: Play,
    highlight: 'Tối ưu cho thao tác nhanh',
    difficulty: 'Dễ',
    latency: '14ms',
    practice: ['Dùng cử chỉ lớn hơn khi ngồi xa màn hình.', 'Tránh che khuất đầu ngón tay khi vuốt.', 'Chờ badge phản hồi sáng trước khi lặp thao tác.'],
  },
  game_2d: {
    icon: Gamepad2,
    highlight: 'Tối ưu cho phản hồi nhanh',
    difficulty: 'Trung bình',
    latency: '10ms',
    practice: ['Ưu tiên nền sáng đều phía sau tay.', 'Giữ cử chỉ ngắn, rõ và có điểm dừng.', 'Tập riêng từng hành động trước khi chơi thật.'],
  },
  custom: {
    icon: SlidersHorizontal,
    highlight: 'Tối ưu cho cá nhân hóa',
    difficulty: 'Nâng cao',
    latency: 'Tùy cấu hình',
    practice: ['Đặt tên gesture rõ ràng trong cấu hình.', 'Train tối thiểu 30-50 mẫu cho mỗi tác vụ.', 'Kiểm thử bằng ứng dụng ít rủi ro trước.'],
  },
}

const categoryIcons: Record<string, LucideIcon> = {
  Pointer: MousePointer2,
  Navigation: ScrollText,
  Tabs: PanelTop,
  Clipboard: Copy,
  System: Keyboard,
  Playback: Music2,
  Timeline: ScrollText,
  Audio: Music2,
  View: Maximize2,
  Movement: Gamepad2,
  Combat: Zap,
}

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

export default function WorkflowView({
  runtime,
  logs = [],
  profiles = [],
}: {
  runtime?: RuntimeStatus
  logs?: GestureLog[]
  profiles?: Profile[]
}) {
  const [activeModeId, setActiveModeId] = useState<ConfigProfileId>('office')
  const [activeProfile, setActiveProfile] = useState<ProfileDetail>(getLocalProfileDetail('office'))
  const [profileStatus, setProfileStatus] = useState('Catalog local')
  const activeModeMeta = guideModeMeta[activeModeId]
  const ActiveIcon = activeModeMeta.icon

  const guideModes = useMemo(
    () =>
      configProfiles.map((item) => ({
        ...item,
        description: profiles.find((profile) => profile.id === item.id)?.description ?? item.description,
      })),
    [profiles],
  )

  useEffect(() => {
    let canceled = false
    const local = getLocalProfileDetail(activeModeId)

    setActiveProfile(local)
    setProfileStatus('Đang tải hướng dẫn...')

    getProfile(activeModeId)
      .then((data) => {
        if (canceled) return
        const mergedFunctions = mergeCatalogFunctions(activeModeId, data.functions)
        setActiveProfile({ ...data, functions: mergedFunctions })
        setProfileStatus((data.functions?.length ?? 0) < mergedFunctions.length ? 'Saved + catalog bổ sung' : 'Saved')
      })
      .catch(() => {
        if (canceled) return
        setActiveProfile(local)
        setProfileStatus('Backend offline; dùng catalog local.')
      })

    return () => {
      canceled = true
    }
  }, [activeModeId])

  const guideFunctions = useMemo(
    () => (activeProfile.functions ?? []).filter((mapping) => mapping.enabled !== false).map(mappingToGuideFunction),
    [activeProfile.functions],
  )
  const recentGuideLogs = useMemo(
    () => logs.filter((log) => /pinch|drag|gesture|hand|tracking/i.test(log.message)).slice(-3),
    [logs],
  )
  const primaryFunction = guideFunctions[0]
  const activeGesture = primaryFunction?.gesture ?? runtime?.currentGesture ?? 'Custom Gesture'
  const actionPreview = primaryFunction?.title ?? runtime?.currentAction ?? 'Tác vụ đang cấu hình'

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
              const Icon = guideModeMeta[mode.id as ConfigProfileId].icon
              const active = mode.id === activeModeId
              return (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setActiveModeId(mode.id as ConfigProfileId)}
                  className={`flex items-center gap-3 rounded-2xl border px-4 py-3 text-left transition ${
                    active
                      ? 'border-brand-cyan/40 bg-brand-cyan/15 text-cyan-100 glow-btn-active'
                      : 'border-white/10 bg-white/[0.03] text-slate-300 hover:border-brand-cyan/25 hover:bg-white/[0.06]'
                  }`}
                >
                  <Icon className="h-5 w-5 shrink-0" />
                  <span className="font-medium">{mode.name}</span>
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
                  <h3 className="text-2xl font-semibold text-white">{activeProfile.name}</h3>
                  <p className="text-sm text-slate-400">{activeModeMeta.highlight}</p>
                </div>
              </div>
              <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300">{activeProfile.description}</p>
            </div>

            <div className="flex flex-wrap gap-2">
              <Badge label={`Độ khó: ${activeModeMeta.difficulty}`} />
              <Badge label={`Latency: ${runtime?.latency ?? activeModeMeta.latency}${typeof runtime?.latency === 'number' ? 'ms' : ''}`} />
              <Badge label={runtime?.trackingStatus ?? 'Sensor: Sẵn sàng'} />
              <Badge label={profileStatus} />
            </div>
          </div>

          <div className="mt-6 grid gap-4 md:grid-cols-2">
            {guideFunctions.length ? (
              guideFunctions.map((item) => <FunctionCard key={`${item.action}-${item.gestureEvent ?? item.title}`} item={item} />)
            ) : (
              <div className="rounded-2xl border border-dashed border-brand-cyan/25 bg-brand-cyan/5 p-4 text-sm text-slate-300">
                Chưa có thao tác đang bật trong cấu hình này.
              </div>
            )}
          </div>
        </div>

        <div className="glass-panel relative overflow-hidden rounded-3xl p-5 sm:p-6">
          <div className="absolute inset-0 obsidian-grid opacity-50" />
          <div className="relative">
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-xs uppercase tracking-[0.24em] text-brand-cyan">Mô phỏng bàn tay</div>
                <h3 className="mt-2 text-xl font-semibold text-white">{actionPreview}</h3>
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
                {activeGesture}
              </div>
            </div>

            <div className="mt-5 grid gap-2 rounded-2xl border border-white/10 bg-black/25 p-4">
              {activeModeMeta.practice.map((step, index) => (
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

function mappingToGuideFunction(mapping: FunctionMapping): GuideFunction {
  return {
    title: mapping.label,
    gesture: mapping.gesture,
    description: mapping.description || fallbackDescription(mapping.action),
    icon: resolveGuideIcon(mapping),
    tone: mapping.tone ?? toneFromMapping(mapping),
    action: mapping.action,
    gestureEvent: mapping.gesture_event,
  }
}

function resolveGuideIcon(mapping: FunctionMapping): LucideIcon {
  if (mapping.category && categoryIcons[mapping.category]) return categoryIcons[mapping.category]
  if (mapping.action.startsWith('mouse.move')) return MousePointer2
  if (mapping.action.includes('click')) return Mouse
  if (mapping.action.includes('scroll')) return ScrollText
  if (mapping.action.includes('drag') || mapping.action === 'mouse.down' || mapping.action === 'mouse.up') return Hand
  if (mapping.action.startsWith('media.volume')) return SlidersHorizontal
  if (mapping.action.startsWith('media.')) return Play
  if (mapping.action.startsWith('game.attack') || mapping.action.startsWith('game.skill')) return ShieldCheck
  if (mapping.action.startsWith('game.')) return Gamepad2
  if (mapping.action.startsWith('keyboard.')) return Keyboard
  return Sparkles
}

function toneFromMapping(mapping: FunctionMapping): GuideFunction['tone'] {
  if (mapping.category === 'Combat' || mapping.action.includes('attack')) return 'red'
  if (mapping.category === 'System' || mapping.action.includes('hotkey')) return 'amber'
  if (mapping.action.startsWith('media.') || mapping.action.startsWith('game.') || mapping.category === 'Tabs') return 'blue'
  return 'cyan'
}

function fallbackDescription(action: string) {
  if (action === 'mouse.move') return 'Dùng cử chỉ đã gán để điều khiển con trỏ theo chuyển động tay.'
  if (action === 'mouse.left_click') return 'Thực hiện cử chỉ đã gán một nhịp ngắn để chọn mục đang trỏ.'
  if (action === 'mouse.right_click') return 'Thực hiện cử chỉ đã gán để mở menu ngữ cảnh.'
  if (action === 'mouse.scroll') return 'Di chuyển tay theo hướng đã gán để cuộn nội dung.'
  if (action.includes('drag')) return 'Giữ cử chỉ, di chuyển tay tới vị trí đích, sau đó thả để hoàn tất.'
  if (action.startsWith('media.')) return 'Dùng cử chỉ đã gán để điều khiển nội dung đang phát.'
  if (action.startsWith('game.')) return 'Dùng cử chỉ đã gán để gửi lệnh nhanh trong game.'
  if (action.startsWith('keyboard.')) return 'Kích hoạt phím hoặc phím tắt đã cấu hình.'
  return `Thao tác được ánh xạ tới ${action}.`
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
      <p className="mt-3 break-all font-mono text-xs text-slate-500">
        {item.gestureEvent ?? 'custom_gesture'} {'->'} {item.action}
      </p>
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
