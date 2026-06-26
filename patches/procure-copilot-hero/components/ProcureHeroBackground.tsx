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
        className="absolute inset-0 h-full w-full object-cover object-[center_40%] scale-105 saturate-125 brightness-95"
        loading="eager"
        decoding="async"
      />
      {/* Text column (left): dark. Right side: aisle visible. */}
      <div className="absolute inset-0 bg-gradient-to-r from-[var(--cm-background)] via-[var(--cm-background)]/70 to-transparent" />
      <div className="absolute inset-0 bg-gradient-to-t from-[var(--cm-background)]/60 via-transparent to-[var(--cm-background)]/20" />
    </div>
  );
}
