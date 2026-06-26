import type { ProductDoor } from "@/lib/productDoors";

type ProductDoorCardProps = {
  door: ProductDoor;
  isES: boolean;
  onClick?: () => void;
};

const accentClass: Record<ProductDoor["id"], string> = {
  build: "border-[#ea580c]/25 hover:border-[#ea580c]/45",
  procure: "border-[#0f172a]/10 hover:border-[#0f172a]/25",
  intelligence: "border-[#0369a1]/20 hover:border-[#0369a1]/40",
};

const eyebrowClass: Record<ProductDoor["id"], string> = {
  build: "text-[#ea580c]",
  procure: "text-[#0f172a]",
  intelligence: "text-[#0369a1]",
};

export default function ProductDoorCard({ door, isES, onClick }: ProductDoorCardProps) {
  const linkProps = door.external
    ? { target: "_blank" as const, rel: "noopener noreferrer" }
    : {};

  return (
    <a
      href={door.href}
      onClick={onClick}
      className={`card-cyber rounded-2xl p-5 sm:p-6 flex flex-col h-full text-left transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 border ${accentClass[door.id]}`}
      {...linkProps}
    >
      <span className={`text-[10px] font-bold uppercase tracking-widest ${eyebrowClass[door.id]}`}>
        {isES ? door.eyebrow_es : door.eyebrow_en}
      </span>
      <h3 className="mt-2 text-lg font-semibold text-[#0f172a] leading-snug">
        {isES ? door.title_es : door.title_en}
      </h3>
      <p className="mt-3 text-sm text-[#64748b] leading-relaxed flex-1">
        {isES ? door.outcome_es : door.outcome_en}
      </p>
      <div className="mt-5 pt-4 border-t border-[#e2e8f0] flex items-center justify-between gap-3">
        <span className="text-xs font-mono text-[#64748b]">{isES ? door.price_es : door.price_en}</span>
        <span className="text-sm font-semibold text-[#ea580c] shrink-0">
          {isES ? door.cta_es : door.cta_en}
        </span>
      </div>
    </a>
  );
}
