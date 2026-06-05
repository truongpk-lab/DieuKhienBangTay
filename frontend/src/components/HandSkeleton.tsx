export default function HandSkeleton() {
  return (
    <svg viewBox="0 0 200 220" className="h-full w-full drop-shadow-[0_0_18px_rgba(0,242,255,0.55)]">
      <g stroke="#00f2ff" strokeLinecap="round" strokeWidth="2.5" opacity="0.82">
        <line x1="100" y1="180" x2="60" y2="120" />
        <line x1="100" y1="180" x2="80" y2="100" />
        <line x1="100" y1="180" x2="110" y2="90" />
        <line x1="100" y1="180" x2="140" y2="105" />
        <line x1="100" y1="180" x2="160" y2="130" />
        <polyline fill="none" points="60,120 40,105 30,80" />
        <polyline fill="none" points="80,100 75,55 70,25" />
        <polyline fill="none" points="110,90 110,45 110,15" />
        <polyline fill="none" points="140,105 145,65 150,35" />
        <polyline fill="none" points="160,130 170,100 180,75" />
      </g>
      <g fill="#e1fdff">
        {[
          [100, 180, 5],
          [60, 120, 3.5],
          [80, 100, 3.5],
          [110, 90, 3.5],
          [140, 105, 3.5],
          [160, 130, 3.5],
          [40, 105, 2.5],
          [75, 55, 2.5],
          [110, 45, 2.5],
          [145, 65, 2.5],
          [170, 100, 2.5],
          [30, 80, 4],
          [70, 25, 4],
          [110, 15, 4],
          [150, 35, 4],
          [180, 75, 4],
        ].map(([cx, cy, r], index) => (
          <circle
            key={`${cx}-${cy}-${index}`}
            cx={cx}
            cy={cy}
            r={r}
            fill={index === 0 || index > 10 ? '#00dbe7' : undefined}
          />
        ))}
      </g>
    </svg>
  )
}
