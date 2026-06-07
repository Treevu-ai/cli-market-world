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
          <a href="/docs" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Quickstart API" : "Quickstart API"}
          </a>
          <a href="/tools" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Referencia MCP" : "MCP Tool Reference"}
          </a>
          <a href="/retailers" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Retailers" : "Retailers"}
          </a>
          <a href="/docs#quickstart" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Demo en terminal" : "Terminal demo"}
          </a>
          <a href="/docs" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Casos de uso" : "Use cases"}
          </a>
          <a href="/docs" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Arquitectura" : "Architecture"}
          </a>
          <a href="https://pypi.org/project/cli-market/" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            PyPI Package
          </a>
          <a href="https://pypi.org/project/cli-market/" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            PyPI
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="font-label-caps text-[var(--cm-mint)] opacity-50 mb-1">
            {isES ? "Compañía" : "Company"}
          </span>
          <a href="/retailers" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Listar mi tienda" : "List my store"}
          </a>
          <a href="/#intelligence" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Inteligencia piloto" : "Intelligence pilot"}
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
          <a href="/#how" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Flujo" : "Flow"}
          </a>
          <a href="/#casos" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Casos de uso" : "Use cases"}
          </a>
          <a href="/#coverage" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Cobertura" : "Coverage"}
          </a>
          <a href="/#faq" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            FAQ
          </a>
          <a href="/#pricing" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Planes y precios" : "Plans & pricing"}
          </a>
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
