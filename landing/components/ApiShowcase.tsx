"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { recordPipInstallIntent } from "@/lib/funnel";
import { PRICING_BUILD_HASH } from "@/lib/siteNav";

type Tab = "python" | "curl";

const CURL_CODE = `# Search products
curl -X POST https://cli-market-production.up.railway.app/products/search \\
  -H "Authorization: Bearer $CLI_MARKET_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "arroz", "limit": 10}'

# Compare basket across retailers
curl -X POST https://cli-market-production.up.railway.app/v1/basket/compare \\
  -H "Authorization: Bearer $CLI_MARKET_KEY" \\
  -d '{
    "items": [{"name":"arroz","qty":1}],
    "stores": ["metro-pe","wong-pe","plaza-vea-pe"]
  }'`;

function PythonBlock() {
  const lines = [
    { text: "import cli_market", type: "keyword" },
    { text: "", type: "blank" },
    { text: `# Search across ${MARKET_STATS.retailersVerified} retailers — normalized per kg/L`, type: "comment" },
    { text: 'results = cli_market.compare("arroz", country="PE")', type: "code" },
    { text: "", type: "blank" },
    { text: "# Output:", type: "comment" },
    { text: '# Metro PE   → S/ 2.90 /kg  ✓ in stock', type: "comment" },
    { text: '# Plaza Vea  → S/ 3.05 /kg  ✓ in stock', type: "comment" },
    { text: '# Wong PE    → S/ 3.10 /kg  ✓ in stock', type: "comment" },
    { text: "", type: "blank" },
    { text: "# Multi-retailer basket — best total in <1s", type: "comment" },
    { text: "basket = cli_market.basket(", type: "code" },
    { text: '    items=["arroz:1kg", "leche:1L", "aceite:1L"],', type: "code" },
    { text: '    country="PE"', type: "code" },
    { text: ")", type: "code" },
    { text: 'print(basket.best_store)   # → Metro PE  S/ 18.40', type: "code-comment" },
    { text: 'print(basket.savings)      # → S/ 2.30 vs worst option', type: "code-comment" },
  ];

  return (
    <div className="font-mono text-[13px] leading-relaxed">
      {lines.map((line, i) => {
        if (line.type === "blank") return <div key={i} className="h-4" />;
        if (line.type === "comment") return <div key={i} className="text-[#64748d]">{line.text}</div>;
        if (line.type === "keyword") return <div key={i}><span className="text-[#b9b9f9]">{line.text}</span></div>;
        if (line.type === "code-comment") {
          const [code, ...rest] = line.text.split("#");
          return (
            <div key={i}>
              <span className="text-white/80">{code}</span>
              <span className="text-[#64748d]">#{rest.join("#")}</span>
            </div>
          );
        }
        return <div key={i} className="text-white/80">{line.text}</div>;
      })}
    </div>
  );
}

function CurlBlock() {
  const lines = CURL_CODE.split("\n");
  return (
    <div className="font-mono text-[13px] leading-relaxed">
      {lines.map((line, i) => {
        if (line.startsWith("#")) return <div key={i} className="text-[#64748d]">{line}</div>;
        if (line.includes("\\")) return <div key={i} className="text-white/80">{line}</div>;
        return <div key={i} className="text-white/80">{line}</div>;
      })}
    </div>
  );
}

export default function ApiShowcase() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [tab, setTab] = useState<Tab>("python");

  return (
    <section className="landing-section animate-fade-in bg-[#f6f9fc] overflow-x-hidden" style={{ borderTop: "1px solid #e3e8ee", borderBottom: "1px solid #e3e8ee" }}>
      <div className="landing-container-wide">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 items-center">

          {/* Left — text */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <p className="section-eyebrow mb-4">{isES ? "API" : "API"}</p>
            <h2 className="section-title mb-4">
              {isES
                ? "Datos limpios. Una línea de código."
                : "Clean data. One line of code."}
            </h2>
            <p className="text-base text-[#64748d] leading-relaxed mb-6">
              {isES
                ? `${MARKET_STATS.retailersVerified} retailers. Precios normalizados por kg/L. Sin scraping, sin parsers frágiles, sin mantenimiento.`
                : `${MARKET_STATS.retailersVerified} retailers. Prices normalized per kg/L. No scraping, no fragile parsers, no maintenance.`}
            </p>
            <ul className="space-y-3 mb-8">
              {(isES ? [
                `${MARKET_STATS.mcpTools} tools MCP listos para Claude y Cursor`,
                "Basket multi-retailer en <1s",
                `Refresh cada ${MARKET_STATS.pricesRefreshHours}h · historial 12 meses`,
              ] : [
                `${MARKET_STATS.mcpTools} MCP tools ready for Claude and Cursor`,
                "Multi-retailer basket in <1s",
                `Refresh every ${MARKET_STATS.pricesRefreshHours}h · 12-month history`,
              ]).map((item) => (
                <li key={item} className="flex items-start gap-2.5 text-sm text-[#64748d]">
                  <svg className="w-4 h-4 mt-0.5 shrink-0 text-[#533afd]" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M6.5 12L2 7.5l1.4-1.4 3.1 3.1 6.1-6.1L14 4.5z"/>
                  </svg>
                  {item}
                </li>
              ))}
            </ul>
            <a
              href={PRICING_BUILD_HASH}
              onClick={() => recordPipInstallIntent("landing_api_showcase")}
              className="inline-flex items-center rounded-full bg-[#533afd] text-white text-sm font-semibold px-5 py-2.5 hover:bg-[#4434d4] transition-colors"
            >
              {isES ? "Empezar gratis →" : "Get started free →"}
            </a>
          </motion.div>

          {/* Right — terminal */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="rounded-xl overflow-hidden bg-[#0d1117]" style={{ boxShadow: "0 0 0 1px rgba(255,255,255,0.06), 0 24px 48px rgba(0,0,0,0.3)" }}>
              {/* Terminal top bar */}
              <div className="flex items-center gap-2 px-4 py-3 bg-[#161b22] border-b border-white/5">
                <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
                <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
                <div className="w-3 h-3 rounded-full bg-[#28c840]" />
                <div className="flex gap-1 ml-4">
                  {(["python", "curl"] as Tab[]).map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setTab(t)}
                      className={`text-xs font-mono px-3 py-1 rounded-md transition-colors ${
                        tab === t
                          ? "bg-white/10 text-white"
                          : "text-white/40 hover:text-white/70"
                      }`}
                    >
                      {t === "python" ? "Python" : "cURL"}
                    </button>
                  ))}
                </div>
              </div>

              {/* Code content */}
              <div className="p-5 overflow-x-auto min-h-[200px] sm:min-h-[320px] max-h-[380px] overflow-y-auto">
                {tab === "python" ? <PythonBlock /> : <CurlBlock />}
              </div>

              {/* Footer bar */}
              <div className="px-5 py-3 bg-[#161b22] border-t border-white/5 flex items-center justify-between">
                <span className="text-[11px] font-mono text-white/30">
                  {isES ? `${MARKET_STATS.retailersVerified} retailers · ${MARKET_STATS.countries} países` : `${MARKET_STATS.retailersVerified} retailers · ${MARKET_STATS.countries} countries`}
                </span>
                <span className="text-[11px] font-mono text-[#533afd]/70">
                  pip install cli-market-world
                </span>
              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
