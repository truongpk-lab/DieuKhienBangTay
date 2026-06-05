import type { HandLandmark } from '../types'

const defaultLandmarks: HandLandmark[] = [
  { x: 100 / 200, y: 190 / 220, z: 0 },
  { x: 75 / 200, y: 160 / 220, z: 0 },
  { x: 55 / 200, y: 132 / 220, z: 0 },
  { x: 42 / 200, y: 108 / 220, z: 0 },
  { x: 30 / 200, y: 84 / 220, z: 0 },
  { x: 86 / 200, y: 128 / 220, z: 0 },
  { x: 78 / 200, y: 88 / 220, z: 0 },
  { x: 74 / 200, y: 58 / 220, z: 0 },
  { x: 70 / 200, y: 28 / 220, z: 0 },
  { x: 106 / 200, y: 122 / 220, z: 0 },
  { x: 106 / 200, y: 78 / 220, z: 0 },
  { x: 106 / 200, y: 45 / 220, z: 0 },
  { x: 106 / 200, y: 14 / 220, z: 0 },
  { x: 128 / 200, y: 128 / 220, z: 0 },
  { x: 137 / 200, y: 91 / 220, z: 0 },
  { x: 144 / 200, y: 62 / 220, z: 0 },
  { x: 151 / 200, y: 34 / 220, z: 0 },
  { x: 148 / 200, y: 142 / 220, z: 0 },
  { x: 165 / 200, y: 116 / 220, z: 0 },
  { x: 176 / 200, y: 94 / 220, z: 0 },
  { x: 186 / 200, y: 72 / 220, z: 0 },
]

const handConnections = [
  [0, 1],
  [1, 2],
  [2, 3],
  [3, 4],
  [0, 5],
  [5, 6],
  [6, 7],
  [7, 8],
  [5, 9],
  [9, 10],
  [10, 11],
  [11, 12],
  [9, 13],
  [13, 14],
  [14, 15],
  [15, 16],
  [13, 17],
  [0, 17],
  [17, 18],
  [18, 19],
  [19, 20],
]

type HandSkeletonProps = {
  landmarks?: HandLandmark[]
  className?: string
}

export default function HandSkeleton({ landmarks, className = 'h-full w-full' }: HandSkeletonProps) {
  const points = landmarks?.length === 21 ? landmarks : defaultLandmarks

  return (
    <svg viewBox="0 0 200 220" className={`${className} drop-shadow-[0_0_18px_rgba(0,242,255,0.55)]`}>
      <g stroke="#00f2ff" strokeLinecap="round" strokeWidth="2.5" opacity="0.82">
        {handConnections.map(([from, to]) => (
          <line
            key={`${from}-${to}`}
            x1={points[from].x * 200}
            y1={points[from].y * 220}
            x2={points[to].x * 200}
            y2={points[to].y * 220}
          />
        ))}
      </g>
      <g fill="#e1fdff">
        {points.map((point, index) => (
          <circle
            key={`${point.x}-${point.y}-${index}`}
            cx={point.x * 200}
            cy={point.y * 220}
            r={index === 0 || [4, 8, 12, 16, 20].includes(index) ? 4.5 : 3}
            fill={index === 0 || [4, 8, 12, 16, 20].includes(index) ? '#00dbe7' : undefined}
          />
        ))}
      </g>
    </svg>
  )
}
