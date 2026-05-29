"use client";
import { useLang } from "@/lib/LanguageContext";

export default function QuickstartAPI() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="api" className="relative bg-[var(--wise-canvas-soft)] py-16 border-t border-[#c5edab]">
      <div className="landing-container px-6 text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-8">API</p>
        <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-3 tracking-tight">
          {isES ? "Una llamada. Datos verificados." : "One call. Verified data."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-md mx-auto mb-12">
          {isES
            ? "Todo lo que haces en la CLI está disponible vía HTTP. Busca, compara canastas y crea órdenes con JSON plano."
            : "Everything in the CLI is available over HTTP. Search, compare baskets, and create orders with flat JSON."}
        </p>

        <div className="text-left space-y-4 max-w-[560px] mx-auto">
          <div className="bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-lg p-4 font-mono text-[11px] leading-relaxed">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[#c5edab]">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" /><span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" /><span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[var(--wise-body)] ml-2 uppercase">bash · canasta AR</span>
            </div>
            <pre className="text-[var(--wise-body)] whitespace-pre-wrap">{`market basket "arroz:1 aceite:1 leche:1 huevos:1" --country AR
# Carrefour vs Jumbo vs Vea · total por cadena · precio normalizado`}</pre>
          </div>

          <div className="bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-lg p-4 font-mono text-[11px] leading-relaxed">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[#c5edab]">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" /><span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" /><span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[var(--wise-body)] ml-2 uppercase">POST /products/compare</span>
            </div>
            <pre className="text-[var(--wise-body)] whitespace-pre-wrap">{`{
  "query": "aceite de girasol 900ml",
  "country": "AR",
  "limit": 8
}
# Mismo producto · varias cadenas · precio por litro`}</pre>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-[var(--wise-body)]">
          <span>{isES ? "REST simple con JSON plano" : "Simple REST with flat JSON"}</span>
          <span className="text-[#c5edab] hidden sm:inline">·</span>
          <a href="/tools" className="underline hover:text-[var(--wise-ink)]">
            {isES ? "36 herramientas MCP → configs" : "36 MCP tools → configs"}
          </a>
          <span className="text-[#c5edab] hidden sm:inline">·</span>
          <a href="https://cli-market-production.up.railway.app/dashboard" target="_blank" rel="noopener" className="underline hover:text-[var(--wise-ink)]">
            {isES ? "Dashboard en vivo" : "Live dashboard"}
          </a>
        </div>
      </div>
    </section>
  );
}
