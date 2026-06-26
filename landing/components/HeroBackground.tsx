/** Decorative hero — retail data network (no people / stock photos). */
export default function HeroBackground() {
  return (
    <div
      className="pointer-events-none absolute inset-0 z-0 overflow-hidden"
      aria-hidden="true"
    >
      <div
        className="absolute inset-0 opacity-[0.55]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(15, 23, 42, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(15, 23, 42, 0.04) 1px, transparent 1px)
          `,
          backgroundSize: "48px 48px",
        }}
      />
      <svg
        className="absolute inset-0 h-full w-full"
        viewBox="0 0 1200 600"
        preserveAspectRatio="xMidYMid slice"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="hero-mint-glow" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3afecf" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#3afecf" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="hero-orange-glow" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#ea580c" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#ea580c" stopOpacity="0" />
          </linearGradient>
        </defs>
        <ellipse cx="180" cy="120" rx="280" ry="200" fill="url(#hero-orange-glow)" />
        <ellipse cx="980" cy="80" rx="320" ry="220" fill="url(#hero-mint-glow)" />
        <path
          d="M80 420 C 200 360, 320 480, 440 400 S 680 320, 800 380 S 1000 440, 1120 360"
          stroke="#3afecf"
          strokeOpacity="0.25"
          strokeWidth="1.5"
          strokeDasharray="6 8"
        />
        <path
          d="M120 180 L 280 240 L 420 200 L 560 280 L 720 220 L 880 260 L 1040 200"
          stroke="#ea580c"
          strokeOpacity="0.18"
          strokeWidth="1.5"
        />
        {[
          [120, 180],
          [280, 240],
          [420, 200],
          [560, 280],
          [720, 220],
          [880, 260],
          [1040, 200],
          [200, 400],
          [480, 360],
          [760, 420],
          [1000, 380],
        ].map(([cx, cy], i) => (
          <g key={i}>
            <circle cx={cx} cy={cy} r="14" stroke="#3afecf" strokeOpacity="0.35" strokeWidth="1" />
            <circle cx={cx} cy={cy} r="4" fill="#3afecf" fillOpacity="0.5" />
          </g>
        ))}
        <rect x="60" y="480" width="48" height="6" rx="2" fill="#0f172a" fillOpacity="0.06" />
        <rect x="68" y="468" width="32" height="6" rx="2" fill="#ea580c" fillOpacity="0.12" />
        <rect x="1080" y="100" width="56" height="6" rx="2" fill="#0f172a" fillOpacity="0.06" />
        <rect x="1092" y="88" width="36" height="6" rx="2" fill="#3afecf" fillOpacity="0.2" />
      </svg>
      <div className="absolute inset-0 bg-gradient-to-r from-[#f8fafc] via-[#f8fafc]/85 to-[#f8fafc]/40" />
      <div className="absolute inset-0 bg-gradient-to-t from-[#f8fafc] via-transparent to-[#f8fafc]/30" />
    </div>
  );
}
