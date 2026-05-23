import { motion } from 'motion/react'
import HandSkeleton from './HandSkeleton'

type HandCameraHUDProps = {
  compact?: boolean
}

export default function HandCameraHUD({ compact = false }: HandCameraHUDProps) {
  return (
    <div className={`relative overflow-hidden rounded-2xl bg-[#0e0e10] ${compact ? 'h-[340px]' : 'h-[470px]'}`}>
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,242,255,0.07)_1px,transparent_1px),linear-gradient(90deg,rgba(0,242,255,0.07)_1px,transparent_1px)] bg-[size:50px_50px]" />
      <div className="absolute left-4 top-4 rounded-full border border-red-300/30 bg-red-500/10 px-3 py-1 text-xs font-semibold text-red-200">
        LIVE
      </div>
      <motion.div
        animate={{ scale: [1, 1.025, 1], rotate: [-1, 1, -1] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute left-1/2 top-1/2 h-[72%] w-[42%] -translate-x-1/2 -translate-y-1/2"
      >
        <HandSkeleton />
      </motion.div>
      <div className="absolute bottom-4 left-4 rounded-xl border border-cyan-300/15 bg-black/35 px-4 py-3 font-mono text-xs text-cyan-100">
        <div>Model: ACV-Hand-v2.1</div>
        <div>Res: 1920x1080</div>
      </div>
    </div>
  )
}
