/** Retail aisle + data overlay — hero background (decorative only). */
export default function HeroBackground({ dense = false }: { dense?: boolean }) {
  const overlayHorizontal = dense
    ? "absolute inset-0 bg-gradient-to-r from-[var(--cm-background)]/97 via-[var(--cm-background)]/82 to-[var(--cm-background)]/45"
    : "absolute inset-0 bg-gradient-to-r from-[var(--cm-background)]/94 via-[var(--cm-background)]/70 to-[var(--cm-background)]/40";
  const overlayVertical = dense
    ? "absolute inset-0 bg-gradient-to-t from-[var(--cm-background)]/90 via-[var(--cm-background)]/35 to-[var(--cm-background)]/45"
    : "absolute inset-0 bg-gradient-to-t from-[var(--cm-background)]/85 via-[var(--cm-background)]/30 to-[var(--cm-background)]/40";

  return (
    <div
      className="pointer-events-none absolute inset-0 z-0 overflow-hidden"
      aria-hidden="true"
    >
      <img
        src="/hero-retail-data.webp"
        alt=""
        width={1920}
        height={1080}
        className="absolute inset-0 h-full w-full object-cover object-[50%_38%] scale-105 saturate-75 brightness-110"
        loading="eager"
        decoding="async"
      />
      <div className={overlayHorizontal} />
      <div className={overlayVertical} />
    </div>
  );
}
