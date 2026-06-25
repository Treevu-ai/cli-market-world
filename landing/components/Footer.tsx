"use client";
import { useLang } from "@/lib/LanguageContext";
import { useLiveStats } from "@/hooks/useLiveStats";
import { MARKET_STATS } from "@/lib/marketStats";

export default function Footer() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceChip } = useLiveStats();
  const year = new Date().getFullYear();

  return (
    <footer
      className="w-full py-12 bg-[#f8fafc] border-t border-[#e2e8f0]"
      role="contentinfo"
    >
      <div className="landing-container-wide grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
        <div className="sm:col-span-2 md:col-span-1">
          <div className="text-base font-semibold text-[#0f172a] mb-4">CLI Market</div>
          <p className="text-sm text-[#64748b]">
            {isES
              ? "© " + year + " CLI Market. Inteligencia de retail programable para LATAM."
              : "© " + year + " CLI Market. Programmable retail intelligence for LATAM."}
          </p>
          <p className="text-xs text-[#71717a] mt-4">
            {isES
              ? `${MARKET_STATS.retailersPhraseEs} · ${priceChip} precios · MIT`
              : `${MARKET_STATS.retailersPhraseEn} · ${priceChip} prices · MIT`}
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#71717a] mb-3">
            {isES ? "Producto" : "Product"}
          </span>
          <a href="/#pricing" className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors">
            CLI Develop
          </a>
          <a href="https://procure-copilot.contacto-8e4.workers.dev/procure" className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors" target="_blank" rel="noopener noreferrer">
            Procure Copilot
          </a>
          <a href="/#intelligence" className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors">
            Intelligence
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#71717a] mb-3">
            {isES ? "Desarrolladores" : "Developers"}
          </span>
          <a href="/docs" className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors">
            Docs
          </a>
          <a href="/#api" className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors">
            SDK
          </a>
          <a href={MARKET_STATS.pypiUrl} className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors" target="_blank" rel="noopener noreferrer">
            PyPI
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#71717a] mb-3">
            {isES ? "Compañía" : "Company"}
          </span>
          <a href="mailto:hello@cli-market.dev" className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors">
            {isES ? "Contacto" : "Contact"}
          </a>
          <a href="/legal/tos" className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors">
            Legal
          </a>
          <a href="/#moat" className="text-sm text-[#64748b] hover:text-[#ea580c] transition-colors">
            {isES ? "Acerca de" : "About"}
          </a>
        </div>
      </div>

      <div className="landing-container-wide mt-10 pt-6 border-t border-[#e2e8f0] flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap gap-x-6 gap-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#71717a]">
            {isES ? "Legal" : "Legal"}
          </span>
          <a href="/legal/tos" className="text-xs text-[#64748b] hover:text-[#ea580c] transition-colors">
            {isES ? "Términos de Servicio" : "Terms of Service"}
          </a>
          <a href="/legal/privacy" className="text-xs text-[#64748b] hover:text-[#ea580c] transition-colors">
            {isES ? "Política de Privacidad" : "Privacy Policy"}
          </a>
          <a href="/legal/dla" className="text-xs text-[#64748b] hover:text-[#ea580c] transition-colors">
            {isES ? "Licencia de Datos (ALD)" : "Data License (DLA)"}
          </a>
        </div>
        <p className="text-xs text-[#71717a]">
          Sinapsis Innovadora S.A.C. · RUC 20613045563 · Lima, Perú
        </p>
      </div>
    </footer>
  );
}
