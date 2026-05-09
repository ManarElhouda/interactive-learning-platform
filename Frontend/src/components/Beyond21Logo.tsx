type Props = { size?: number; showText?: boolean; className?: string };

// One chromosome 21 — a single stubby X with rounded ends.
// Short p-arms (top), longer q-arms (bottom), pinched at the centromere.
function Chromosome({ rotate = 0, x = 0 }: { rotate?: number; x?: number }) {
  return (
    <g transform={`translate(${x}, 0) rotate(${rotate})`}>
      {/* Single body — stroked X with rounded caps so it reads as ONE chromosome */}
      <g
        stroke="#FFF6EE"
        strokeWidth="4.4"
        strokeLinecap="round"
        fill="none"
      >
        {/* Top-left p-arm to bottom-right q-arm */}
        <path d="M -5 -8 Q -1.5 -3 0 0 Q 1.5 4 5 11" />
        {/* Top-right p-arm to bottom-left q-arm */}
        <path d="M 5 -8 Q 1.5 -3 0 0 Q -1.5 4 -5 11" />
      </g>
      {/* Centromere pinch */}
      <circle cx="0" cy="0" r="1.6" fill="#F2D9C4" />
    </g>
  );
}

export function Beyond21Logo({ size = 48, showText = false, className }: Props) {
  const totalWidth = showText ? size * 3.2 : size;
  const totalHeight = size;

  return (
    <svg
      viewBox={showText ? "0 0 320 100" : "0 0 100 100"}
      width={totalWidth}
      height={totalHeight}
      className={className}
      role="img"
      aria-label="Beyond 21"
    >
      <defs>
        <radialGradient id="b21-heart-fill" cx="35%" cy="30%" r="75%">
          <stop offset="0%" stopColor="#F49AAE" />
          <stop offset="55%" stopColor="#E8677D" />
          <stop offset="100%" stopColor="#C84A63" />
        </radialGradient>
        <radialGradient id="b21-heart-shine" cx="30%" cy="22%" r="35%">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
        </radialGradient>
      </defs>

      <path
        d="M50 86 C 14 62, 8 38, 26 24 C 38 15, 47 22, 50 32 C 53 22, 62 15, 74 24 C 92 38, 86 62, 50 86 Z"
        fill="url(#b21-heart-fill)"
      />
      <path
        d="M50 86 C 14 62, 8 38, 26 24 C 38 15, 47 22, 50 32 C 53 22, 62 15, 74 24 C 92 38, 86 62, 50 86 Z"
        fill="url(#b21-heart-shine)"
      />

      {/* Trisomy 21 — three single chromosomes */}
      <g transform="translate(50, 50)">
        <Chromosome x={-12} rotate={-12} />
        <Chromosome x={0} rotate={0} />
        <Chromosome x={12} rotate={12} />
      </g>

      {showText && (
        <g
          fontFamily="Quicksand, system-ui, sans-serif"
          fill="#2D3436"
          dominantBaseline="middle"
        >
          <text x="115" y="42" fontWeight="500" fontSize="32" letterSpacing="0.5">
            Beyond
          </text>
          <text x="115" y="78" fontWeight="700" fontSize="40" fill="#E8677D">
            21
          </text>
        </g>
      )}
    </svg>
  );
}
