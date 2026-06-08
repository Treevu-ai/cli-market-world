"use client";
import { useLang } from "@/lib/LanguageContext";
import { useLiveStats } from "@/hooks/useLiveStats";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";
import { SECTION_NAV, PRICING_LISTED_HASH, PRICING_PROCURE_HASH } from "@/lib/siteNav";

export default function Footer() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceChip } = useLiveStats();
  const year = new Date().getFullYear();

  return (
    <footer
      className="w-full py-12 bg-gradient-to-b from-[var(--cm-surface-low)] to-[var(--cm-background)] border-t border-[var(--cm-outline-variant)]/20"
      role="contentinfo"
    >
      <div className="landing-container-wide grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-8">
        <div className="sm:col-span-2 md:col-span-1">
          <div className="font-display text-xl font-bold text-white mb-4">CLI Market</div>
          <p className="font-mono text-sm text-[var(--cm-on-surface-variant)] opacity-80">
            {isES
              ? "© " + year + " CLI Market LatAm. Infraestructura para agentes."
              : "© " + year + " CLI Market LatAm. Infrastructure for agents."}
          </p>
          <p className="font-mono text-xs text-[var(--cm-on-surface-variant)]/60 mt-4">
            {isES
              ? `${MARKET_STATS.retailersPhraseEs} · ${priceChip} precios · MIT`
              : `${MARKET_STATS.retailersPhraseEn} · ${priceChip} prices · MIT`}
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <span className="font-label-caps text-[var(--cm-mint)] opacity-50 mb-1">
            {isES ? "Desarrolladores" : "Developers"}
          </span>
          <a href="/docs#quickstart" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Quickstart API" : "Quickstart API"}
          </a>
          <a href={`${API_URL}/docs`} className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors" target="_blank" rel="noopener noreferrer">
            OpenAPI
          </a>
          <a href="/tools" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Referencia MCP" : "MCP Tool Reference"}
          </a>
          <a href="/docs#quickstart" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Demo en terminal" : "Terminal demo"}
          </a>
          <a href="/docs#mcp" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Integración MCP" : "MCP integration"}
          </a>
          <a href={MARKET_STATS.pypiUrl} className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors" target="_blank" rel="noopener noreferrer">
            PyPI
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="font-label-caps text-[var(--cm-mint)] opacity-50 mb-1">
            {isES ? "Compañía" : "Company"}
          </span>
          <a href={PRICING_LISTED_HASH} className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            Listed — {isES ? "góndola gratis" : "free shelf"}
          </a>
          <a href={PRICING_PROCURE_HASH} className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            Procure Copilot
          </a>
          <a href="/retailers" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Catálogo retailers" : "Retailer catalog"}
          </a>
          <a href="/intelligence-pilot-es.md" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "One-pager Intelligence" : "Intelligence one-pager"}
          </a>
          <a href="/#about" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Nosotros" : "About"}
          </a>
          <a href="/#contact" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Contacto" : "Contact"}
          </a>
          <a href="mailto:hello@cli-market.dev" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            hello@cli-market.dev
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="font-label-caps text-[var(--cm-mint)] opacity-50 mb-1">
            {isES ? "Producto" : "Product"}
          </span>
          {SECTION_NAV.map(({ id, es, en }) => (
            <a
              key={id}
              href={`/#${id}`}
              className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors"
            >
              {id === "pricing"
                ? isES
                  ? "Planes (Build · Procure · Listed)"
                  : "Plans (Build · Procure · Listed)"
                : id === "api"
                  ? isES
                    ? "API en vivo"
                    : "Live API"
                  : id === "casos"
                    ? isES
                      ? "Casos de uso"
                      : "Use cases"
                    : isES
                      ? es
                      : en}
            </a>
          ))}
        </div>
      </div>

      <div className="landing-container-wide mt-10 pt-6 border-t border-[var(--cm-outline-variant)]/20 flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap gap-x-6 gap-y-2">
          <span className="font-label-caps text-[var(--cm-mint)] opacity-50 text-[10px]">
            {isES ? "Legal" : "Legal"}
          </span>
          <a href="/legal/tos" className="font-mono text-xs text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Términos de Servicio" : "Terms of Service"}
          </a>
          <a href="/legal/privacy" className="font-mono text-xs text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Política de Privacidad" : "Privacy Policy"}
          </a>
          <a href="/legal/dla" className="font-mono text-xs text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Licencia de Datos (ALD)" : "Data License (DLA)"}
          </a>
        </div>
        <p className="font-mono text-[10px] text-[var(--cm-on-surface-variant)]/50">
          Sinapsis Innovadora S.A.C. · RUC 20613045563 · Lima, Perú
        </p>
      </div>
    </footer>
  );
}
