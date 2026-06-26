import type { ProductDoor } from "@/lib/productDoors";

type ProductDoorCardProps = {
  door: ProductDoor;
  isES: boolean;
  compact?: boolean;
  onClick?: () => void;
};

const accentClass: Record<ProductDoor["id"], string> = {
  build: "border-[var(--cm-mint)]/25 hover:border-[var(--cm-mint)]/45",
  procure: "border-[var(--cm-outline-variant)] hover:border-[var(--cm-on-surface-variant)]/40",
  intelligence: "border-[#38bdf8]/20 hover:border-[#38bdf8]/40",
};

const eyebrowClass: Record<ProductDoor["id"], string> = {
  build: "text-[var(--cm-mint)]",
  procure: "text-[var(--cm-on-surface-variant)]",
  intelligence: "text-[#38bdf8]",
};

export default function ProductDoorCard({ door, isES, compact, onClick }: ProductDoorCardProps) {
  const linkProps = door.external
    ? { target: "_blank" as const, rel: "noopener noreferrer" }
    : {};

  return (
    <a
      href={door.href}
      onClick={onClick}
      className={`card-cyber flex flex-col h-full text-left transition-all duration-200 hover:-translate-y-0.5 border ${accentClass[door.id]} ${
        compact ? "rounded-xl p-4 sm:p-5" : "rounded-2xl p-5 sm:p-6 hover:shadow-md"
      }`}
      {...linkProps}
    >
      <span className={`text-[10px] font-bold uppercase tracking-widest ${eyebrowClass[door.id]}`}>
        {isES ? door.eyebrow_es : door.eyebrow_en}
      </span>
      <h3 className={`mt-2 font-semibold text-[var(--cm-on-surface)] leading-snug ${compact ? "text-base" : "text-lg"}`}>
        {isES ? door.title_es : door.title_en}
      </h3>
      <p className={`mt-2 text-sm text-[var(--cm-on-surface-variant)] leading-relaxed flex-1 ${compact ? "line-clamp-2" : "mt-3"}`}>
        {isES ? door.outcome_es : door.outcome_en}
      </p>
      <div className="mt-4 pt-3 border-t border-[var(--cm-outline-variant)] flex items-center justify-between gap-3">
        <span className="text-xs font-mono text-[var(--cm-text-secondary)]">{isES ? door.price_es : door.price_en}</span>
        <span className="text-sm font-semibold text-[var(--cm-mint)] shrink-0">
          {isES ? door.cta_es : door.cta_en}
        </span>
      </div>
    </a>
  );
}
