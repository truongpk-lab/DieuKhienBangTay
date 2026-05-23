import { motion } from 'motion/react'

const steps = ['Kẹp ngón', 'Giữ', 'Di chuyển tay', 'Thả ngón', 'Hoàn thành']

export default function WorkflowView() {
  return (
    <div className="grid min-h-[calc(100vh-100px)] place-items-center py-5">
      <div className="glass-panel w-full max-w-6xl rounded-3xl p-8">
        <div className="text-center">
          <div className="text-sm uppercase tracking-[0.28em] text-cyan-200">PINCH DRAG DROP</div>
          <h2 className="glow-text mt-3 text-4xl font-semibold">QUY TRÌNH KÉO THẢ (PINCH DRAG DROP)</h2>
        </div>
        <div className="relative mt-16 grid grid-cols-5 gap-3">
          <div className="absolute left-[10%] right-[10%] top-8 h-1 rounded-full bg-white/10" />
          <div className="absolute left-[10%] top-8 h-1 w-[40%] rounded-full bg-cyan-300 shadow-[0_0_18px_#00f2ff]" />
          {steps.map((step, index) => {
            const active = index === 2
            const done = index < 2
            return (
              <div key={step} className="relative z-10 text-center">
                <div className={`mx-auto grid h-16 w-16 place-items-center rounded-full border ${done || active ? 'border-cyan-300 bg-cyan-300/15 text-cyan-100' : 'border-white/10 bg-white/5 text-slate-500'}`}>
                  {active && (
                    <motion.span
                      className="absolute h-24 w-24 rounded-full border border-cyan-300/30"
                      animate={{ scale: [0.8, 1.35], opacity: [0.8, 0] }}
                      transition={{ duration: 1.4, repeat: Infinity }}
                    />
                  )}
                  {index + 1}
                </div>
                <div className="mt-4 text-sm text-slate-200">{step}</div>
              </div>
            )
          })}
        </div>
        <div className="mx-auto mt-16 max-w-3xl rounded-2xl border border-cyan-300/15 bg-cyan-300/5 p-5 text-center">
          <div className="text-cyan-100">Trạng thái hiện tại: Đang theo dõi chuyển động</div>
          <div className="mt-4 flex justify-center gap-3">
            <span className="rounded-full border border-cyan-300/20 px-3 py-1 text-sm text-cyan-100">Sensor: Active</span>
            <span className="rounded-full border border-cyan-300/20 px-3 py-1 text-sm text-cyan-100">Latency: 12ms</span>
          </div>
        </div>
      </div>
    </div>
  )
}
