const ITEMS = ["☁️", "⭐", "🌸", "🫧", "🌟", "☁️", "🦋", "🌸"];

export function FloatingBackground() {
  return (
    <div aria-hidden className="pointer-events-none fixed inset-0 overflow-hidden -z-10">
      {ITEMS.map((emoji, i) => (
        <span
          key={i}
          className="absolute text-4xl opacity-50 animate-float-slow"
          style={{
            left: `${(i * 13 + 5) % 95}%`,
            top: `${(i * 19 + 8) % 90}%`,
            animationDelay: `${i * 0.7}s`,
            animationDuration: `${7 + (i % 4)}s`,
          }}
        >
          {emoji}
        </span>
      ))}
    </div>
  );
}
