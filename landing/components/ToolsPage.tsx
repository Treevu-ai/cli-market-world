"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const MCP_API_URL = "https://cli-market-production.up.railway.app";

const MCP_CONFIG = {
  cursor: `{
  "mcpServers": {
    "cli-market": {
      "command": "market-mcp",
      "args": [],
      "env": {
        "MARKET_API_URL": "${MCP_API_URL}"
      }
    }
  }
}`,
  claude: `{
  "mcpServers": {
    "cli-market": {
      "command": "market-mcp",
      "args": [],
      "env": {
        "MARKET_API_URL": "${MCP_API_URL}"
      }
    }
  }
}`,
  vscode: `{
  "servers": {
    "cli-market": {
      "type": "stdio",
      "command": "market-mcp",
      "env": {
        "MARKET_API_URL": "${MCP_API_URL}"
      }
    }
  }
}`,
};

const STARTER_TOOLS = [
  { id: "market_search", es: "Buscar productos por query y país", en: "Search products by query and country" },
  { id: "market_compare", es: "Comparar precio del mismo SKU entre retailers", en: "Compare same SKU price across retailers" },
  { id: "market_cart", es: "Ver y gestionar carrito", en: "View and manage cart" },
  { id: "market_whoami", es: "Usuario, tier y límites", en: "User, tier, and limits" },
  { id: "market_stats", es: "Estadísticas de red (retailers, snapshots)", en: "Network stats (retailers, snapshots)" },
];

const TOOLS = [
  "market_add",
  "market_cart",
  "market_checkout",
  "market_inflation",
  "market_stores",
  "market_countries",
  "market_lines",
  "market_ask",
  "market_orders",
];

export default function ToolsPage() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [tab, setTab] = useState<keyof typeof MCP_CONFIG>("cursor");
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(MCP_CONFIG[tab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      <section className="py-24 px-[var(--cm-gutter)] text-center border-b border-[var(--cm-outline-variant)]/20 pt-28">
        <div className="max-w-[720px] mx-auto">
          <p className="section-eyebrow mb-4">MCP · {isES ? "API de compras para IA" : "AI shopping API"}</p>
          <h1 className="font-display text-[clamp(1.75rem,5vw,3rem)] font-bold text-white mb-4 tracking-tight">
            {isES
              ? `${MARKET_STATS.mcpTools} herramientas MCP para agentes de comercio`
              : `${MARKET_STATS.mcpTools} MCP tools for e-commerce agents`}
          </h1>
          <p className="text-base text-[var(--cm-on-surface-variant)] max-w-[540px] mx-auto leading-relaxed">
            {isES
              ? `API de comercio para agentes de IA — búsqueda, comparación, canasta y checkout en ${MARKET_STATS.retailersVerified} retailers. Copie una config, ejecute `
              : `Commerce API for AI agents — search, compare, basket, and checkout across ${MARKET_STATS.retailersVerified} retailers. Copy a config, run `}
            <code className="font-mono text-sm text-[var(--cm-mint)]">{MARKET_STATS.pipInstallCmd}</code>
            {isES ? ", conecte su IDE." : ", connect your IDE."}
          </p>
        </div>
      </section>

      <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20">
        <div className="max-w-[720px] mx-auto">
          <div className="flex flex-wrap gap-2 mb-4 justify-center">
            {(Object.keys(MCP_CONFIG) as (keyof typeof MCP_CONFIG)[]).map((k) => (
              <button
                key={k}
                type="button"
                onClick={() => setTab(k)}
                className={`font-label-caps px-4 py-1.5 capitalize transition-colors ${
                  tab === k
                    ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]"
                    : "glass-panel text-[var(--cm-on-surface-variant)] hover:text-white"
                }`}
              >
                {k}
              </button>
            ))}
            <button type="button" onClick={copy} className="font-label-caps px-4 py-1.5 bg-[var(--cm-surface-high)] text-white border border-[var(--cm-outline-variant)] hover:border-[var(--cm-mint)]/50">
              {copied ? (isES ? "Copiado" : "Copied") : (isES ? "Copiar config" : "Copy config")}
            </button>
          </div>
          <pre className="text-left code-block-cyber text-[var(--cm-mint)] p-5 overflow-x-auto">
            {MCP_CONFIG[tab]}
          </pre>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-4 text-center">
            {isES ? "Requiere" : "Requires"}{" "}
            <code className="font-mono text-[var(--cm-mint)]">{MARKET_STATS.pipInstallCmd}</code> · Manifest:{" "}
            <a href="/server.json" className="text-[var(--cm-mint)] underline">server.json</a>
            {" "}· Docs:{" "}
            <a href="/llms.txt" className="text-[var(--cm-mint)] underline">llms.txt</a>
          </p>
        </div>
      </section>

      <section className="py-16 px-[var(--cm-gutter)]">
        <div className="max-w-[720px] mx-auto text-center">
          <h2 className="section-title mb-2">
            {isES ? "Herramientas MCP iniciales (5)" : "Starter MCP tools (5)"}
          </h2>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mb-6">
            {isES ? "Ejecute" : "Run"}{" "}
            <code className="font-mono text-[var(--cm-mint)]">market init</code> {isES ? "o" : "or"}{" "}
            <code className="font-mono text-[var(--cm-mint)]">market register</code>
            {isES ? ", luego pruebe estas primero." : ", then try these first."}
          </p>
          <ul className="text-left space-y-3 mb-10 max-w-md mx-auto">
            {STARTER_TOOLS.map((tool) => (
              <li key={tool.id} className="glass-panel rounded-lg px-4 py-3 border border-[var(--cm-mint)]/15">
                <code className="font-mono text-sm text-[var(--cm-mint)]">{tool.id}</code>
                <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{isES ? tool.es : tool.en}</p>
              </li>
            ))}
          </ul>
          <h3 className="text-sm font-semibold text-white mb-4">{isES ? "Más herramientas" : "More tools"}</h3>
          <div className="flex flex-wrap justify-center gap-2">
            {TOOLS.map((t) => (
              <span key={t} className="font-mono text-[11px] glass-panel rounded-full px-3 py-1 text-[var(--cm-on-surface-variant)]">
                {t}
              </span>
            ))}
          </div>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mt-6">
            + {MARKET_STATS.mcpTools - STARTER_TOOLS.length - TOOLS.length}{" "}
            {isES ? "más en el registro completo" : "more in the full registry"}
          </p>
          <a href="/tools" className="inline-block mt-8 text-sm font-semibold text-[var(--cm-mint)] underline">
            {isES ? "Registro completo MCP →" : "Full MCP registry →"}
          </a>
        </div>
      </section>
    </>
  );
}