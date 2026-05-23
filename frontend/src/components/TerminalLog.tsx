import type { GestureLog } from '../types'
import { useEffect, useRef } from 'react'

type TerminalLogProps = {
  logs: GestureLog[]
  onClear?: () => void
}

export default function TerminalLog({ logs, onClear }: TerminalLogProps) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  return (
    <div className="glass-panel flex h-full min-h-[220px] flex-col rounded-2xl">
      <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
        <h2 className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-300">Gesture log</h2>
        <button onClick={onClear} className="rounded-lg border border-cyan-300/20 px-3 py-1 text-xs text-cyan-200">
          Clear
        </button>
      </div>
      <div className="flex-1 space-y-2 overflow-auto p-5 font-mono text-sm">
        {logs.map((log) => (
          <div
            key={`${log.time}-${log.message}`}
            className={`grid grid-cols-[78px_1fr] gap-3 rounded-lg px-2 py-1 sm:grid-cols-[90px_1fr] sm:gap-4 ${
              log.type === 'gesture' ? 'border-l-2 border-cyan-300 bg-cyan-300/5 text-cyan-100' : 'text-slate-300'
            }`}
          >
            <span className="text-slate-500">{log.time}</span>
            <span className="break-words">{log.message}</span>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  )
}
