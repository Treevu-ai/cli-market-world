"use client";
import { useLang } from "@/lib/LanguageContext";

export default function QuickstartAPI() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="api" className="relative bg-[#e8ebe6] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#454745] font-mono uppercase tracking-[0.15em] mb-8">API</p>
        <h2 className="text-[24px] font-medium text-[#0e0f0c] mb-3 tracking-tight">
          {isES ? "API lista para tus agentes y backends." : "API ready for your agents and backends."}
        </h2>
        <p className="text-sm text-[#454745] max-w-md mx-auto mb-12">
          {isES ? "Todo lo que haces en la CLI está disponible vía HTTP. Tu agente puede buscar, comparar y crear órdenes con una API JSON simple." : "Everything you do in the CLI is available over HTTP. Your agent can search, compare, and create orders with a simple JSON API."}
        </p>

        {/* Request + Response */}
        <div className="text-left space-y-4 max-w-[560px] mx-auto">
          <div className="bg-[#e2f6d5] border border-[#c5edab] rounded-lg p-4 font-mono text-[11px] leading-relaxed">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[#c5edab]">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" /><span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" /><span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[#454745] ml-2 uppercase">POST /v1/search</span>
            </div>
            <pre className="text-[#454745] whitespace-pre-wrap">{`Content-Type: application/json
Authorization: Bearer sk-xxxxxxxx

{
  "query": "leche gloria",
  "country": "PE",
  "limit": 5
}`}</pre>
          </div>

          <div className="bg-[#e2f6d5] border border-[#c5edab] rounded-lg p-4 font-mono text-[11px] leading-relaxed">
            <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[#c5edab]">
              <span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
              <span className="text-[10px] text-[#454745] ml-1 uppercase">200 OK</span>
            </div>
            <pre className="text-[#454745] whitespace-pre-wrap">{`{
  "results": [{
    "retailer": "Metro",
    "price": 3.90,
    "currency": "PEN",
    "product_id": "12345"
  }],
  "generated_at": "2026-05-25T12:00:00Z"
}`}</pre>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-[#454745]">
          <span>{isES ? "REST simple con JSON plano" : "Simple REST with flat JSON"}</span>
          <span className="text-[#c5edab] hidden sm:inline">·</span>
          <span>{isES ? "Precios actualizados cada 8 horas" : "Prices refreshed every 8 hours"}</span>
          <span className="text-[#c5edab] hidden sm:inline">·</span>
          <span>{isES ? "Listo para agentes en Python, JS, etc." : "Ready for agents in Python, JS, etc."}</span>
        </div>
      </div>
    </section>
  );
}
