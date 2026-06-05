import {
  ChevronRight,
  Copy,
  Edit3,
  Gamepad2,
  Hand,
  Keyboard,
  Maximize2,
  Mouse,
  MousePointerClick,
  Music2,
  PanelTop,
  Plus,
  Save,
  ScrollText,
  Trash2,
  X,
  Zap,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { getProfile, saveProfile, type ProfileDetail } from '../api/profileApi'
import {
  actionOptions,
  allGestureEvents,
  configProfiles,
  getLocalProfileDetail,
  isConfigProfileId,
  mergeCatalogFunctions,
  type ConfigProfileId,
} from '../config/actionCatalog'
import type { FunctionMapping, GestureSuggestion, Profile } from '../types'

const categoryIcons = {
  Pointer: MousePointerClick,
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
} satisfies Record<string, typeof Mouse>

export default function ConfigView({ profiles = [] }: { profiles?: Profile[] }) {
  const profileOptions = useMemo(
    () =>
      configProfiles.map((item) => ({
        ...item,
        description: profiles.find((profile) => profile.id === item.id)?.description ?? item.description,
      })),
    [profiles],
  )
  const [profileId, setProfileId] = useState<ConfigProfileId>('office')
  const [profile, setProfile] = useState<ProfileDetail>(getLocalProfileDetail('office'))
  const [draft, setDraft] = useState<FunctionMapping[]>(getLocalProfileDetail('office').functions ?? [])
  const [editing, setEditing] = useState<FunctionMapping | null>(null)
  const [selectedMappingId, setSelectedMappingId] = useState<string | null>(null)
  const [status, setStatus] = useState('Đang tải cấu hình...')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let canceled = false
    const local = getLocalProfileDetail(profileId)
    setProfile(local)
    setDraft(local.functions ?? [])
    setSelectedMappingId(null)
    setStatus('Đang tải cấu hình...')
    setBusy(true)

    getProfile(profileId)
      .then((data) => {
        if (canceled) return
        const mergedFunctions = mergeCatalogFunctions(profileId, data.functions)
        setProfile({ ...data, functions: mergedFunctions })
        setDraft(mergedFunctions)
        setStatus((data.functions?.length ?? 0) < mergedFunctions.length ? 'Saved + catalog bổ sung' : 'Saved')
      })
      .catch(() => {
        if (canceled) return
        setProfile(local)
        setDraft(local.functions ?? [])
        setStatus('Backend offline; dùng catalog local.')
      })
      .finally(() => !canceled && setBusy(false))

    return () => {
      canceled = true
    }
  }, [profileId])

  const validation = useMemo(() => validateMappings(draft), [draft])
  const selectedMapping = useMemo(
    () => draft.find((mapping) => mapping.id === selectedMappingId) ?? null,
    [draft, selectedMappingId],
  )

  function openNewMapping() {
    const next: FunctionMapping = {
      id: `custom_${Date.now()}`,
      label: 'Tác vụ mới',
      description: 'Tác vụ tùy chỉnh cho profile hiện tại.',
      category: 'System',
      gesture: 'Custom Gesture',
      gesture_event: 'custom_gesture',
      action: 'keyboard.press',
      enabled: true,
      payload: { key: 'space' },
      gesture_options: [
        {
          id: 'custom_gesture',
          label: 'Custom Gesture',
          gesture_event: 'custom_gesture',
          gesture: 'Custom Gesture',
          description: 'Cử chỉ cá nhân sẽ được huấn luyện sau.',
          fit: 'Dùng cho nhu cầu riêng khi catalog chưa đủ.',
        },
      ],
    }
    setEditing(next)
    setSelectedMappingId(next.id)
  }

  function commitEdit(next: FunctionMapping) {
    setDraft((items) => {
      const exists = items.some((item) => item.id === next.id)
      return exists ? items.map((item) => (item.id === next.id ? next : item)) : [...items, next]
    })
    setEditing(null)
    setSelectedMappingId(next.id)
    setStatus('Unsaved')
  }

  function removeMapping(id: string) {
    setDraft((items) => items.filter((item) => item.id !== id))
    setSelectedMappingId((current) => (current === id ? null : current))
    setStatus('Unsaved')
  }

  function applyGesture(mappingId: string, suggestion: GestureSuggestion) {
    setDraft((items) =>
      items.map((item) =>
        item.id === mappingId
          ? { ...item, gesture: suggestion.gesture, gesture_event: suggestion.gesture_event }
          : item,
      ),
    )
    setStatus('Unsaved')
  }

  async function saveConfig() {
    const error = validateMappings(draft)
    if (error) {
      setStatus(error)
      return
    }
    setBusy(true)
    try {
      const saved = await saveProfile(profile.id, { ...profile, functions: draft })
      const mergedFunctions = mergeCatalogFunctions(profileId, saved.functions ?? draft)
      setProfile({ ...saved, functions: mergedFunctions })
      setDraft(mergedFunctions)
      setStatus('Saved')
    } catch {
      setStatus('Backend offline; chưa lưu được lên API.')
    } finally {
      setBusy(false)
    }
  }

  function changeProfile(value: string) {
    if (isConfigProfileId(value)) {
      setProfileId(value)
    }
  }

  return (
    <div className="space-y-5 py-5">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <p className="max-w-2xl text-slate-400">
          Chọn mục đích sử dụng để nạp catalog action tương ứng, sau đó chọn từng card để gán gesture nhanh.
        </p>
        <select
          value={profileId}
          onChange={(event) => changeProfile(event.target.value)}
          className="rounded-xl border border-cyan-300/30 bg-[#1c1b1d] px-4 py-3 text-white shadow-[0_0_24px_rgba(0,242,255,0.08)]"
        >
          {profileOptions.map((item) => (
            <option key={item.id} value={item.id}>{item.name}</option>
          ))}
        </select>
      </div>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_380px]">
        <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
          {draft.map((mapping) => (
            <ActionCard
              key={mapping.id}
              mapping={mapping}
              active={mapping.id === selectedMappingId}
              onSelect={() => setSelectedMappingId(mapping.id)}
              onEdit={() => setEditing(mapping)}
              onRemove={() => removeMapping(mapping.id)}
            />
          ))}
          <button
            onClick={openNewMapping}
            className="grid min-h-56 place-items-center rounded-2xl border border-dashed border-cyan-300/30 bg-cyan-300/5 text-cyan-100 transition hover:border-cyan-200 hover:bg-cyan-300/10"
            type="button"
          >
            <span className="grid place-items-center gap-3">
              <Plus className="h-10 w-10" />
              Thêm mới
            </span>
          </button>
        </div>

        {selectedMapping && (
          <GestureSuggestionPanel
            mapping={selectedMapping}
            onApply={(suggestion) => applyGesture(selectedMapping.id, suggestion)}
            onClose={() => setSelectedMappingId(null)}
            onEdit={() => setEditing(selectedMapping)}
          />
        )}
      </div>

      {editing && <MappingEditor mapping={editing} onCancel={() => setEditing(null)} onSave={commitEdit} />}

      <div className="sticky bottom-4 flex flex-wrap justify-end gap-3 rounded-2xl border border-white/10 bg-black/55 p-4 backdrop-blur">
        <span className={`mr-auto self-center text-sm ${validation ? 'text-red-200' : status === 'Saved' ? 'text-emerald-200' : 'text-amber-200'}`}>
          {validation || status}
        </span>
        <span className="self-center rounded-full border border-cyan-300/20 px-3 py-1 text-xs text-cyan-100">
          {draft.length} action
        </span>
        <button
          onClick={() => {
            setDraft(profile.functions ?? [])
            setStatus('Saved')
          }}
          className="rounded-xl border border-white/10 px-5 py-3 text-slate-300"
          type="button"
        >
          Hủy
        </button>
        <button
          disabled={busy || Boolean(validation)}
          onClick={saveConfig}
          className="inline-flex items-center gap-2 rounded-xl bg-cyan-300 px-5 py-3 font-semibold text-black disabled:opacity-50"
          type="button"
        >
          <Save className="h-4 w-4" />
          LƯU CẤU HÌNH
        </button>
      </div>
    </div>
  )
}

function ActionCard({
  mapping,
  active,
  onSelect,
  onEdit,
  onRemove,
}: {
  mapping: FunctionMapping
  active: boolean
  onSelect: () => void
  onEdit: () => void
  onRemove: () => void
}) {
  const Icon = mapping.tone === 'red' ? Zap : categoryIcons[mapping.category as keyof typeof categoryIcons] ?? Hand

  return (
    <button
      onClick={onSelect}
      className={`glass-panel min-h-56 rounded-2xl p-5 text-left transition ${
        active ? 'border-cyan-200/60 shadow-[0_0_28px_rgba(0,242,255,0.18)]' : ''
      } ${mapping.enabled === false ? 'opacity-50' : ''}`}
      type="button"
    >
      <div className="flex items-start justify-between gap-3">
        <div className={`mb-5 grid h-12 w-12 place-items-center rounded-xl ${mapping.tone === 'red' ? 'bg-red-300/10 text-red-100' : 'bg-cyan-300/10 text-cyan-200'}`}>
          <Icon className="h-6 w-6" />
        </div>
        <button
          onClick={(event) => {
            event.stopPropagation()
            onRemove()
          }}
          className="rounded-lg border border-red-300/20 p-2 text-red-100 transition hover:bg-red-400/10"
          type="button"
          aria-label={`Xóa ${mapping.label}`}
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
      <div>
        <div className="flex items-center gap-2">
          {mapping.category && (
            <span className="rounded-full border border-cyan-300/15 px-2 py-1 text-[11px] uppercase tracking-[0.18em] text-cyan-100">
              {mapping.category}
            </span>
          )}
        </div>
        <h2 className="mt-3 text-lg font-semibold text-white">{mapping.label}</h2>
        {mapping.description && <p className="mt-2 line-clamp-2 text-sm text-slate-400">{mapping.description}</p>}
        <p className="mt-3 text-sm text-slate-300">{mapping.gesture}</p>
        <p className="mt-2 break-all font-mono text-xs text-cyan-100">{mapping.gesture_event}{' -> '}{mapping.action}</p>
      </div>
      <div className="mt-5 flex flex-wrap gap-2">
        <button
          onClick={(event) => {
            event.stopPropagation()
            onEdit()
          }}
          className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 transition hover:border-cyan-300/30"
          type="button"
        >
          <Edit3 className="h-4 w-4" />
          Chỉnh sửa
        </button>
        <span className="inline-flex items-center gap-1 rounded-xl border border-cyan-300/15 px-3 py-2 text-sm text-cyan-100">
          Gợi ý <ChevronRight className="h-4 w-4" />
        </span>
      </div>
    </button>
  )
}

function GestureSuggestionPanel({
  mapping,
  onApply,
  onClose,
  onEdit,
}: {
  mapping: FunctionMapping
  onApply: (suggestion: GestureSuggestion) => void
  onClose: () => void
  onEdit: () => void
}) {
  const suggestions = mapping.gesture_options?.length ? mapping.gesture_options : fallbackSuggestions(mapping)

  return (
    <aside className="glass-panel sticky top-5 h-fit rounded-2xl p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-cyan-200">Gesture phù hợp</p>
          <h3 className="mt-2 text-xl font-semibold text-white">{mapping.label}</h3>
          <p className="mt-2 text-sm text-slate-400">{mapping.description ?? 'Chọn gesture thuận tiện để gán cho action này.'}</p>
        </div>
        <button onClick={onClose} className="rounded-lg border border-white/10 p-2 text-slate-300" type="button" aria-label="Đóng gợi ý">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-5 space-y-3">
        {suggestions.map((suggestion) => {
          const selected = suggestion.gesture_event === mapping.gesture_event
          return (
            <div key={suggestion.id} className={`rounded-2xl border p-4 ${selected ? 'border-cyan-300/50 bg-cyan-300/10' : 'border-white/10 bg-white/[0.03]'}`}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="font-semibold text-white">{suggestion.label}</h4>
                  <p className="mt-1 font-mono text-xs text-cyan-100">{suggestion.gesture_event}</p>
                </div>
                <button
                  onClick={() => onApply(suggestion)}
                  className="rounded-xl bg-cyan-300 px-3 py-2 text-xs font-semibold text-black disabled:opacity-50"
                  disabled={selected}
                  type="button"
                >
                  {selected ? 'Đang dùng' : 'Áp dụng'}
                </button>
              </div>
              <p className="mt-3 text-sm text-slate-300">{suggestion.description}</p>
              <p className="mt-2 text-xs text-slate-500">{suggestion.fit}</p>
            </div>
          )
        })}
      </div>

      <button onClick={onEdit} className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-sm text-slate-200" type="button">
        <Edit3 className="h-4 w-4" />
        Chỉnh sửa chi tiết mapping
      </button>
    </aside>
  )
}

function MappingEditor({ mapping, onCancel, onSave }: { mapping: FunctionMapping; onCancel: () => void; onSave: (mapping: FunctionMapping) => void }) {
  const [draft, setDraft] = useState<FunctionMapping>(mapping)
  const [payloadText, setPayloadText] = useState(JSON.stringify(mapping.payload ?? {}, null, 2))
  const [error, setError] = useState('')

  function save() {
    try {
      onSave({ ...draft, payload: JSON.parse(payloadText || '{}') })
    } catch {
      setError('Payload phải là JSON object hợp lệ.')
    }
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4">
      <div className="glass-panel w-full max-w-2xl rounded-2xl p-5">
        <h3 className="text-xl font-semibold">Chỉnh sửa mapping</h3>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          <Field label="Label" value={draft.label} onChange={(value) => setDraft({ ...draft, label: value })} />
          <Field label="Nhóm" value={draft.category ?? ''} onChange={(value) => setDraft({ ...draft, category: value })} />
          <Field label="Gesture" value={draft.gesture} onChange={(value) => setDraft({ ...draft, gesture: value })} />
          <Select label="Gesture event" value={draft.gesture_event ?? ''} options={allGestureEvents} onChange={(value) => setDraft({ ...draft, gesture_event: value })} />
          <Select label="Action" value={draft.action} options={actionOptions} onChange={(value) => setDraft({ ...draft, action: value })} />
          <label className="flex items-center gap-3 rounded-xl border border-white/10 p-3 text-sm text-slate-200">
            <input checked={draft.enabled !== false} onChange={(event) => setDraft({ ...draft, enabled: event.target.checked })} type="checkbox" />
            Enable function
          </label>
        </div>
        <Field label="Mô tả" value={draft.description ?? ''} onChange={(value) => setDraft({ ...draft, description: value })} />
        <label className="mt-3 block text-sm text-slate-300">
          Payload JSON
          <textarea value={payloadText} onChange={(event) => setPayloadText(event.target.value)} className="mt-2 h-32 w-full rounded-xl border border-white/10 bg-[#1c1b1d] p-3 font-mono text-xs text-white" />
        </label>
        {error && <p className="mt-3 text-sm text-red-200">{error}</p>}
        <div className="mt-5 flex justify-end gap-3">
          <button onClick={onCancel} className="rounded-xl border border-white/10 px-4 py-2 text-slate-300" type="button">Hủy</button>
          <button onClick={save} className="rounded-xl bg-cyan-300 px-4 py-2 font-semibold text-black" type="button">Lưu mapping</button>
        </div>
      </div>
    </div>
  )
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="mt-3 block text-sm text-slate-300">
      {label}
      <input value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-3 py-2 text-white" />
    </label>
  )
}

function Select({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (value: string) => void }) {
  return (
    <label className="block text-sm text-slate-300">
      {label}
      <select value={value} onChange={(event) => onChange(event.target.value)} className="mt-2 w-full rounded-xl border border-white/10 bg-[#1c1b1d] px-3 py-2 text-white">
        {options.map((item) => <option key={item}>{item}</option>)}
      </select>
    </label>
  )
}

function validateMappings(items: FunctionMapping[]) {
  const seen = new Set<string>()
  for (const item of items) {
    if (!item.label || !item.gesture || !item.gesture_event || !item.action) return 'Thiếu label/gesture/action.'
    if (!actionOptions.includes(item.action)) return `Action không hợp lệ: ${item.action}`
    if (item.enabled !== false) {
      if (seen.has(item.gesture_event)) return `Trùng gesture_event: ${item.gesture_event}`
      seen.add(item.gesture_event)
    }
  }
  return ''
}

function fallbackSuggestions(mapping: FunctionMapping): GestureSuggestion[] {
  return [
    {
      id: `${mapping.id}_current`,
      label: mapping.gesture,
      gesture_event: mapping.gesture_event ?? 'custom_gesture',
      gesture: mapping.gesture,
      description: 'Gesture hiện tại của action này.',
      fit: 'Giữ nguyên nếu mapping đang hoạt động ổn.',
    },
    {
      id: `${mapping.id}_pinch`,
      label: 'Pinch Tap',
      gesture_event: 'pinch_tap',
      gesture: 'Pinch Tap',
      description: 'Kẹp nhanh ngón cái-ngón trỏ để xác nhận.',
      fit: 'Lựa chọn phổ biến cho action dạng chọn.',
    },
    {
      id: `${mapping.id}_pose`,
      label: 'Finger Pose Shortcut',
      gesture_event: 'finger_count_shortcut',
      gesture: 'Finger Pose Shortcut',
      description: 'Giữ số ngón cụ thể để gọi shortcut.',
      fit: 'Hợp tác vụ tùy chỉnh cần học qua hướng dẫn.',
    },
  ]
}
