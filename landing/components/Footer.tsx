"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { PROCURE_SITE_URL } from "@/lib/procurePlans";

export default function Footer() {
  const { lang } = useLang();
  const isES = lang === "es";
  const year = new Date().getFullYear();

  return (
    <footer
      className="w-full py-12 bg-[var(--cm-canvas)] border-t border-[var(--cm-outline-variant)]"
      role="contentinfo"
    >
      <div className="landing-container-wide grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
        <div className="sm:col-span-2 md:col-span-1">
          <div className="text-base font-semibold text-[var(--cm-on-surface)] mb-4">CLI Market</div>
          <p className="text-sm text-[var(--cm-text-secondary)]">
            {isES
              ? "© " + year + " CLI Market. Inteligencia de retail programable para LATAM."
              : "© " + year + " CLI Market. Programmable retail intelligence for LATAM."}
          </p>
          <p className="text-xs text-[var(--cm-text-secondary)] mt-4">
            {isES
              ? `${MARKET_STATS.retailersPhraseEs} · ${MARKET_STATS.pricesVerifiedLabel} precios · MIT`
              : `${MARKET_STATS.retailersPhraseEn} · ${MARKET_STATS.pricesVerifiedLabel} prices · MIT`}
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[var(--cm-text-secondary)] mb-3">
            {isES ? "Producto" : "Product"}
          </span>
          <a href="/#pricing" className="text-sm text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            CLI Build
          </a>
          <a href={`${PROCURE_SITE_URL}/procure`} className="text-sm text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors" target="_blank" rel="noopener noreferrer">
            Procure Copilot
          </a>
          <a href="/#intelligence" className="text-sm text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            Intelligence
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[var(--cm-text-secondary)] mb-3">
            {isES ? "Desarrolladores" : "Developers"}
          </span>
          <a href="/docs" className="text-sm text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            Docs
          </a>
          <a href={MARKET_STATS.pypiUrl} className="text-sm text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors" target="_blank" rel="noopener noreferrer">
            PyPI
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[var(--cm-text-secondary)] mb-3">
            {isES ? "Compañía" : "Company"}
          </span>
          <a href="mailto:hello@cli-market.dev" className="text-sm text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Contacto" : "Contact"}
          </a>
          <a href="/legal/tos" className="text-sm text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            Legal
          </a>
          <a href="/#metrics" className="text-sm text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Acerca de" : "About"}
          </a>
        </div>
      </div>

      <div className="landing-container-wide mt-10 pt-6 border-t border-[var(--cm-outline-variant)] flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap gap-x-6 gap-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[var(--cm-text-secondary)]">
            {isES ? "Legal" : "Legal"}
          </span>
          <a href="/legal/tos" className="text-xs text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Términos de Servicio" : "Terms of Service"}
          </a>
          <a href="/legal/privacy" className="text-xs text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Política de Privacidad" : "Privacy Policy"}
          </a>
          <a href="/legal/dla" className="text-xs text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Licencia de Datos (ALD)" : "Data License (DLA)"}
          </a>
        </div>
        <p className="text-xs text-[var(--cm-text-secondary)]">
          Sinapsis Innovadora S.A.C. · RUC 20613045563 · Lima, Perú
        </p>
      </div>
    </footer>
  );
}
