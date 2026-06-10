"use client";
import { useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import PrereqBlock from "@/components/PrereqBlock";
import { recordPipInstallIntent } from "@/lib/funnel";

export default function QuickstartAPI() {
  const { lang } = useLang();
  const isES = lang === "es";

  useEffect(() => {
    recordPipInstallIntent("api_section");
  }, []);

  return (
    <section id="api" className="brand-mode-terminal landing-section landing-section-glow animate-fade-in">
      <div className="landing-container-wide text-center">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-4">API</p>
          <h2 className="section-title">
            {isES ? "Una llamada. Datos verificados." : "One call. Verified data."}
          </h2>
          <p className="section-intro">
            {isES
              ? "Todo lo que haces en la CLI está disponible vía HTTP. Busca, compara canastas y crea órdenes con JSON plano."
              : "Everything in the CLI is available over HTTP. Search, compare baskets, and create orders with flat JSON."}
          </p>
        </div>

        <div className="text-left space-y-4 w-full landing-content-narrow min-w-0">
          <PrereqBlock level="session" isES={isES} />
          <div className="code-block-cyber px-5 py-4">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[var(--cm-outline-variant)]/30">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" /><span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" /><span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[var(--cm-on-surface-variant)] ml-2 uppercase break-words">bash · onboarding</span>
            </div>
            <pre className="code-snippet text-[var(--cm-on-surface-variant)]">{`${MARKET_STATS.pipInstallCmd}
market init
market search "leche" --country PE`}</pre>
          </div>

          <div className="code-block-cyber px-5 py-4">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[var(--cm-outline-variant)]/30">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" /><span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" /><span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[var(--cm-on-surface-variant)] ml-2 uppercase break-words">POST /products/compare</span>
            </div>
            <pre className="code-snippet text-[var(--cm-on-surface-variant)]">{`{
  "query": "aceite de girasol 900ml",
  "country": "AR",
  "limit": 8
}`}</pre>
          </div>

          <div className="code-block-cyber px-5 py-4">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[var(--cm-outline-variant)]/30">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" /><span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" /><span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[var(--cm-mint)] ml-2 uppercase break-words">200 · response (ejemplo)</span>
            </div>
            <pre className="code-snippet text-[var(--cm-on-surface-variant)]">{`{
  "query": "aceite de girasol 900ml",
  "country": "AR",
  "results": [
    { "store": "carrefour_ar", "price": 2899, "unit_price_per_l": 3221, "currency": "ARS" },
    { "store": "jumbo_ar", "price": 3150, "unit_price_per_l": 3500, "currency": "ARS" }
  ],
  "cheapest": "carrefour_ar",
  "normalized_unit": "per_l"
}`}</pre>
            <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono">
              {isES ? "Precios ilustrativos · estructura real de la API" : "Illustrative prices · real API shape"}
            </p>
          </div>

          <div className="code-block-cyber px-5 py-4">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[var(--cm-outline-variant)]/30">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" /><span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" /><span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[var(--cm-on-surface-variant)] ml-2 uppercase break-words">bash · canasta AR</span>
            </div>
            <pre className="code-snippet text-[var(--cm-on-surface-variant)]">{`market basket "arroz:1 aceite:1 leche:1 huevos:1" --country AR
# Carrefour vs Jumbo vs Vea · total por cadena · precio normalizado`}</pre>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-[var(--cm-on-surface-variant)]">
          <span>{isES ? "REST simple con JSON plano" : "Simple REST with flat JSON"}</span>
          <span className="text-[var(--cm-mint)]/30 hidden sm:inline">·</span>
          <a href="/docs#auth" className="underline hover:text-[var(--cm-mint)]">
            {isES ? "Crear cuenta (register) →" : "Create account (register) →"}
          </a>
          <span className="text-[var(--cm-mint)]/30 hidden sm:inline">·</span>
          <a href="/tools" className="underline hover:text-[var(--cm-mint)]">
            {isES ? `${MARKET_STATS.mcpTools} herramientas MCP → configs` : `${MARKET_STATS.mcpTools} MCP tools → configs`}
          </a>
        </div>
      </div>
    </section>
  );
}
