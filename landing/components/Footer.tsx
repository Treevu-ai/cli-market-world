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
      <div className="landing-container-wide grid grid-cols-2 md:grid-cols-4 gap-8">
        <div className="col-span-2 md:col-span-1">
          <div className="font-display text-xl font-bold text-white mb-4">CLI Market</div>
          <p className="font-mono text-sm text-[var(--cm-on-surface-variant)] opacity-80">
            {isES
              ? "© " + year + " CLI Market LatAm. Infraestructura para agentes."
              : "© " + year + " CLI Market LatAm. Infrastructure for agents."}
          </p>
          <p className="font-mono text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-4">
            {isES
              ? `${MARKET_STATS.retailersPhraseEs} · ${priceChip} precios · MIT`
              : `${MARKET_STATS.retailersPhraseEn} · ${priceChip} prices · MIT`}
          </p>
        </div>

        <div className="flex flex-col gap-3">
          <span className="font-label-caps text-[var(--cm-mint)] opacity-50 mb-1">Developers</span>
          <a href="/docs" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            Quickstart API
          </a>
          <a href="/tools" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            MCP Tool Reference
          </a>
          <a
            href="https://github.com/Treevu-ai/cli-market-world"
            className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors"
          >
            GitHub Repo
          </a>
          <a
            href="https://pypi.org/project/cli-market/"
            className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors"
          >
            PyPI
          </a>
        </div>

        <div className="flex flex-col gap-3">
          <span className="font-label-caps text-[var(--cm-mint)] opacity-50 mb-1">
            {isES ? "Compañía" : "Company"}
          </span>
          <a href="#retailers" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Listar mi tienda" : "List my store"}
          </a>
          <a href="#pricing-intelligence" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Inteligencia piloto" : "Intelligence pilot"}
          </a>
          <a href="#contact" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
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
          <a href="#how" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Flujo" : "Flow"}
          </a>
          <a href="#coverage" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            {isES ? "Cobertura" : "Coverage"}
          </a>
          <a href="#faq" className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors">
            FAQ
          </a>
          <a
            href="https://cli-market-production.up.railway.app/dashboard"
            target="_blank"
            rel="noopener noreferrer"
            className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors"
          >
            Dashboard
          </a>
        </div>
      </div>
    </footer>
  );
}
