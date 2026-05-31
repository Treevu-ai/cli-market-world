"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

export default function QuickstartAPI() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="api" className="landing-section animate-fade-in">
      <div className="landing-container text-center">
        <p className="section-eyebrow mb-8">API</p>
        <h2 className="section-title mb-3">
          {isES ? "Una llamada. Datos verificados." : "One call. Verified data."}
        </h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-md mx-auto mb-12">
          {isES
            ? "Todo lo que haces en la CLI está disponible vía HTTP. Busca, compara canastas y crea órdenes con JSON plano."
            : "Everything in the CLI is available over HTTP. Search, compare baskets, and create orders with flat JSON."}
        </p>

        <div className="text-left space-y-4 w-full max-w-[560px] min-w-0 mx-auto">
          <div className="code-block-cyber px-5 py-4">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[var(--cm-outline-variant)]/30">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" /><span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" /><span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[var(--cm-on-surface-variant)] ml-2 uppercase break-words">bash · canasta AR</span>
            </div>
            <pre className="code-snippet text-[var(--cm-on-surface-variant)]">{`market basket "arroz:1 aceite:1 leche:1 huevos:1" --country AR
# Carrefour vs Jumbo vs Vea · total por cadena · precio normalizado`}</pre>
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
}
# Mismo producto · varias cadenas · precio por litro`}</pre>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-[var(--cm-on-surface-variant)]">
          <span>{isES ? "REST simple con JSON plano" : "Simple REST with flat JSON"}</span>
          <span className="text-[var(--cm-mint)]/30 hidden sm:inline">·</span>
          <a href="/tools" className="underline hover:text-[var(--cm-mint)]">
            {isES ? `${MARKET_STATS.mcpTools} herramientas MCP → configs` : `${MARKET_STATS.mcpTools} MCP tools → configs`}
          </a>
          <span className="text-[var(--cm-mint)]/30 hidden sm:inline">·</span>
          <a href="https://cli-market-production.up.railway.app/dashboard" target="_blank" rel="noopener" className="underline hover:text-[var(--cm-mint)]">
            {isES ? "Dashboard en vivo" : "Live dashboard"}
          </a>
        </div>
      </div>
    </section>
  );
}
