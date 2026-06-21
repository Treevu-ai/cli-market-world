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
      className="w-full py-12 bg-[#09090B] border-t border-[#27272A]"
      role="contentinfo"
    >
      <div className="landing-container-wide grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
        <div className="sm:col-span-2 md:col-span-1">
          <div className="text-base font-semibold text-[#FAFAFA] mb-4">CLI Market</div>
          <p className="text-sm text-[#A1A1AA]">
            {isES
              ? "© " + year + " CLI Market. Inteligencia de retail programable para LATAM."
              : "© " + year + " CLI Market. Programmable retail intelligence for LATAM."}
          </p>
          <p className="text-xs text-[#3f3f46] mt-4">
            {isES
              ? `${MARKET_STATS.retailersPhraseEs} · ${priceChip} precios · MIT`
              : `${MARKET_STATS.retailersPhraseEn} · ${priceChip} prices · MIT`}
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#3f3f46] mb-3">
            {isES ? "Producto" : "Product"}
          </span>
          <a href="/#pricing" className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            {isES ? "API Platform" : "API Platform"}
          </a>
          <a href="/procure" className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            Procure Copilot
          </a>
          <a href="/#intelligence" className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            Intelligence
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#3f3f46] mb-3">
            {isES ? "Desarrolladores" : "Developers"}
          </span>
          <a href="/docs" className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            Docs
          </a>
          <a href="/#api" className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            SDK
          </a>
          <a href={MARKET_STATS.pypiUrl} className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors" target="_blank" rel="noopener noreferrer">
            PyPI
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#3f3f46] mb-3">
            {isES ? "Compañía" : "Company"}
          </span>
          <a href="/contact" className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            {isES ? "Contacto" : "Contact"}
          </a>
          <a href="/legal/tos" className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            Legal
          </a>
          <a href="/#about" className="text-sm text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            {isES ? "Acerca de" : "About"}
          </a>
        </div>
      </div>

      <div className="landing-container-wide mt-10 pt-6 border-t border-[#27272A] flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap gap-x-6 gap-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#3f3f46]">
            {isES ? "Legal" : "Legal"}
          </span>
          <a href="/legal/tos" className="text-xs text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            {isES ? "Términos de Servicio" : "Terms of Service"}
          </a>
          <a href="/legal/privacy" className="text-xs text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            {isES ? "Política de Privacidad" : "Privacy Policy"}
          </a>
          <a href="/legal/dla" className="text-xs text-[#A1A1AA] hover:text-[#7CFF5B] transition-colors">
            {isES ? "Licencia de Datos (ALD)" : "Data License (DLA)"}
          </a>
        </div>
        <p className="text-xs text-[#3f3f46]">
          Sinapsis Innovadora S.A.C. · RUC 20613045563 · Lima, Perú
        </p>
      </div>
    </footer>
  );
}
