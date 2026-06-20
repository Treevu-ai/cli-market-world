"use client";

import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function RetailerCTABanner() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section
      aria-label={isES ? "Para retailers" : "For retailers"}
      className="landing-container-wide py-6"
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border border-[var(--cm-mint)]/20 rounded-xl px-6 py-5 bg-[var(--cm-mint)]/5">
        <div>
          <p className="text-xs font-mono text-[var(--cm-mint)] mb-1">
            {isES ? "¿Eres retailer?" : "Are you a retailer?"}
          </p>
          <p className="text-sm text-white font-medium">
            {isES
              ? "Si tu tienda no está indexada, los agentes de IA no te encuentran."
              : "If your store isn't indexed, AI agents can't find you."}
          </p>
          <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
            {isES
              ? `${MARKET_STATS.retailersVerified} retailers ya son visibles para agentes en Perú y LATAM. Gratis.`
              : `${MARKET_STATS.retailersVerified} retailers are already visible to AI agents across LATAM. Free.`}
          </p>
        </div>
        <a
          href="/retailers"
          className="shrink-0 inline-flex items-center gap-2 rounded-3xl border border-[var(--cm-mint)]/50 text-[var(--cm-mint)] text-xs font-semibold px-5 py-2.5 hover:bg-[var(--cm-mint)] hover:text-[var(--cm-on-mint)] transition-all whitespace-nowrap"
        >
          {isES ? "Listar mi tienda — gratis →" : "List my store — free →"}
        </a>
      </div>
    </section>
  );
}
