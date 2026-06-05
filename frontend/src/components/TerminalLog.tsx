import type { GestureLog } from '../types'
import { useEffect, useMemo, useRef, useState } from 'react'

type TerminalLogProps = {
  logs: GestureLog[]
  onClear?: () => void
  clearDisabled?: boolean
  clearLabel?: string
}

export default function TerminalLog({ logs, onClear, clearDisabled = false, clearLabel = 'Xóa' }: TerminalLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const shouldStickToBottomRef = useRef(true)
  const [isInspecting, setIsInspecting] = useState(false)
  const visibleLogs = useMemo(() => logs.slice(-30), [logs])

  useEffect(() => {
    const container = scrollRef.current
    if (!container || isInspecting || !shouldStickToBottomRef.current) {
      return
    }

    container.scrollTop = container.scrollHeight
  }, [isInspecting, visibleLogs])

  function handleScroll() {
    const container = scrollRef.current
    if (!container) return
    const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight
    const nextIsInspecting = distanceFromBottom > 12
    shouldStickToBottomRef.current = !nextIsInspecting
    setIsInspecting(nextIsInspecting)
  }

  function resumeLatestLogs() {
    const container = scrollRef.current
    shouldStickToBottomRef.current = true
    setIsInspecting(false)
    window.requestAnimationFrame(() => {
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    })
  }

  return (
    <div className="glass-panel flex h-full min-h-[150px] flex-col rounded-2xl">
      <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
        <h2 className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-300">Nhật ký cử chỉ</h2>
        <button
          onClick={onClear}
          disabled={clearDisabled}
          className="rounded-lg border border-cyan-300/20 px-3 py-1 text-xs text-cyan-200 disabled:cursor-wait disabled:opacity-50"
        >
          {clearLabel}
        </button>
      </div>
      <div className="relative">
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-7 bg-gradient-to-b from-[#131315] to-transparent" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-7 bg-gradient-to-t from-[#131315] to-transparent" />
        <div
          ref={scrollRef}
          onMouseEnter={() => setIsInspecting(true)}
          onMouseLeave={resumeLatestLogs}
          onScroll={handleScroll}
          className="max-h-[116px] min-h-[92px] space-y-2 overflow-y-auto overflow-x-hidden px-5 py-4 pr-3 font-mono text-sm [scrollbar-color:rgba(0,242,255,0.35)_rgba(255,255,255,0.06)] [scrollbar-width:thin]"
        >
          {visibleLogs.map((log, index) => (
            <div
              key={`${log.time}-${index}-${log.message}`}
              className={`grid grid-cols-[78px_1fr] gap-3 rounded-lg px-2 py-1 sm:grid-cols-[90px_1fr] sm:gap-4 ${
                log.type === 'gesture' ? 'border-l-2 border-cyan-300 bg-cyan-300/5 text-cyan-100' : 'text-slate-300'
              }`}
            >
              <span className="text-slate-500">{log.time}</span>
              <span className="break-words">{log.message}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
