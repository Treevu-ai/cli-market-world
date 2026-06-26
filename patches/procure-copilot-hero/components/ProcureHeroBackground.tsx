/** Supermarket aisle background for /procure hero — decorative only. */
export default function ProcureHeroBackground() {
  return (
    <div
      className="pointer-events-none absolute inset-0 z-0 overflow-hidden"
      aria-hidden="true"
    >
      <img
        src="/hero-supermarket.webp"
        alt=""
        width={1920}
        height={1080}
        className="absolute inset-0 h-full w-full object-cover object-center scale-105 saturate-110"
        loading="eager"
        decoding="async"
      />
      {/* Left: readable copy. Right: aisle visible. */}
      <div className="absolute inset-0 bg-gradient-to-r from-[var(--cm-background)]/92 via-[var(--cm-background)]/55 to-[var(--cm-background)]/10" />
      <div className="absolute inset-0 bg-gradient-to-t from-[var(--cm-background)]/75 via-transparent to-[var(--cm-background)]/25" />
    </div>
  );
}
