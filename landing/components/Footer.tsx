"use client";
import { useLang } from "@/lib/LanguageContext";
import { useLiveStats } from "@/hooks/useLiveStats";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";
import { RETAILERS_PAGE } from "@/lib/siteNav";

export default function Footer() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceChip } = useLiveStats();
  const year = new Date().getFullYear();

  return (
    <footer
      className="w-full py-12 bg-[#f6f9fc] border-t border-[#e3e8ee]"
      role="contentinfo"
    >
      <div className="landing-container-wide grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
        <div className="sm:col-span-2 md:col-span-1">
          <div className="text-base font-semibold text-[#0d253d] mb-4">CLI Market</div>
          <p className="text-sm text-[#64748d]">
            {isES
              ? "© " + year + " CLI Market. Inteligencia de retail programable para LATAM."
              : "© " + year + " CLI Market. Programmable retail intelligence for LATAM."}
          </p>
          <p className="text-xs text-[#a8c3de] mt-4">
            {isES
              ? `${MARKET_STATS.retailersPhraseEs} · ${priceChip} precios · MIT`
              : `${MARKET_STATS.retailersPhraseEn} · ${priceChip} prices · MIT`}
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#a8c3de] mb-3">
            {isES ? "Producto" : "Product"}
          </span>
          <a href="/#hero" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Home" : "Home"}
          </a>
          <a href="/#how-it-works" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "API Platform" : "API Platform"}
          </a>
          <a href="/procure" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            Procure Copilot
          </a>
          <a href="/#pricing" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Planes" : "Pricing"}
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#a8c3de] mb-3">
            {isES ? "Desarrolladores" : "Developers"}
          </span>
          <a href="/docs" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Docs · Quickstart" : "Docs · Quickstart"}
          </a>
          <a href={`${API_URL}/docs`} className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors" target="_blank" rel="noopener noreferrer">
            OpenAPI (Swagger)
          </a>
          <a href="/tools" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "API tools · IDEs" : "API tools · IDEs"}
          </a>
          <a href={MARKET_STATS.pypiUrl} className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors" target="_blank" rel="noopener noreferrer">
            PyPI
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#a8c3de] mb-3">
            {isES ? "Compañía" : "Company"}
          </span>
          <a href={RETAILERS_PAGE} className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Listar mi tienda (gratis)" : "List my store (free)"}
          </a>
          <a href="/stats" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Métricas públicas" : "Public stats"}
          </a>
          <a href="/impact" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Impacto" : "Impact"}
          </a>
          <a href="/#contact" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Contacto" : "Contact"}
          </a>
          <a href="mailto:hello@cli-market.dev" className="text-sm text-[#64748d] hover:text-[#533afd] transition-colors">
            hello@cli-market.dev
          </a>
        </div>
      </div>

      <div className="landing-container-wide mt-10 pt-6 border-t border-[#e3e8ee] flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap gap-x-6 gap-y-2">
          <span className="text-[11px] font-semibold uppercase tracking-widest text-[#a8c3de]">
            {isES ? "Legal" : "Legal"}
          </span>
          <a href="/legal/tos" className="text-xs text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Términos de Servicio" : "Terms of Service"}
          </a>
          <a href="/legal/privacy" className="text-xs text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Política de Privacidad" : "Privacy Policy"}
          </a>
          <a href="/legal/dla" className="text-xs text-[#64748d] hover:text-[#533afd] transition-colors">
            {isES ? "Licencia de Datos (ALD)" : "Data License (DLA)"}
          </a>
        </div>
        <p className="text-xs text-[#a8c3de]">
          Sinapsis Innovadora S.A.C. · RUC 20613045563 · Lima, Perú
        </p>
      </div>
    </footer>
  );
}
