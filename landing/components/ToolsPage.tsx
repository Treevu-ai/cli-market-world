"use client";
import { useState, useEffect } from "react";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import PrereqBlock from "@/components/PrereqBlock";
import { recordPipInstallIntent } from "@/lib/funnel";

const MCP_API_URL = "https://cli-market-api.fly.dev";

const MCP_CONFIG = {
  cursor: `{
  "mcpServers": {
    "cli-market": {
      "command": "market-mcp",
      "args": [],
      "env": {
        "MARKET_API_URL": "${MCP_API_URL}",
        "MCP_TOOL_PROFILE": "default"
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
        "MARKET_API_URL": "${MCP_API_URL}",
        "MCP_TOOL_PROFILE": "default"
      }
    }
  }
}`,
  vscode: `{
  "servers": {
    "cli-market": {
      "type": "stdio",
      "command": "market-mcp",
      "args": [],
      "env": {
        "MARKET_API_URL": "${MCP_API_URL}",
        "MCP_TOOL_PROFILE": "default"
      }
    }
  }
}`,
};

type BundleKey = keyof typeof MARKET_STATS.mcpBundles;

const BUNDLE_LABELS: Record<BundleKey, { es: string; en: string }> = {
  shop: { es: "Shop", en: "Shop" },
  intel: { es: "Intel", en: "Intel" },
  account: { es: "Account", en: "Account" },
};

const BUNDLE_INTRO: Record<BundleKey, { es: string; en: string }> = {
  shop: {
    es: "Cobertura, búsqueda, comparación, canasta y checkout.",
    en: "Coverage, search, compare, basket, and checkout.",
  },
  intel: {
    es: "Brief de mercado, inflación, scores y exportación de datos.",
    en: "Market brief, inflation, scores, and data export.",
  },
  account: {
    es: "Sesión, preferencias, alertas de precio y favoritos.",
    en: "Session, preferences, price alerts, and favorites.",
  },
};

export default function ToolsPage() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [ideTab, setIdeTab] = useState<keyof typeof MCP_CONFIG>("cursor");
  const [bundleTab, setBundleTab] = useState<BundleKey>("shop");
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(MCP_CONFIG[ideTab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const bundleTools = MARKET_STATS.mcpBundles[bundleTab];

  useEffect(() => {
    recordPipInstallIntent("tools_page");
  }, []);

  return (
    <>
      <section className="py-24 px-[var(--cm-gutter)] text-center border-b border-[var(--cm-outline-variant)]/20 pt-28">
        <div className="max-w-[720px] mx-auto">
          <p className="section-eyebrow mb-4">API · {isES ? "API de compras para IA" : "AI shopping API"}</p>
          <h1 className="font-display text-[clamp(1.75rem,5vw,3rem)] font-bold text-[var(--cm-on-surface)] mb-4 tracking-tight">
            {isES
              ? `${MARKET_STATS.mcpTools} API tools para agentes de comercio`
              : `${MARKET_STATS.mcpTools} API tools for e-commerce agents`}
          </h1>
          <p className="text-base text-[var(--cm-on-surface-variant)] max-w-[540px] mx-auto leading-relaxed">
            {isES
              ? `API de comercio para agentes de IA — Shop, Intel y Account en ${MARKET_STATS.retailersVerified} retailers. Copie una config, ejecute `
              : `Commerce API for AI agents — Shop, Intel, and Account across ${MARKET_STATS.retailersVerified} retailers. Copy a config, run `}
            <code className="font-mono text-sm text-[var(--cm-mint)]">{MARKET_STATS.pipInstallCmd}</code>
            {isES ? ", conecte su IDE." : ", connect your IDE."}
          </p>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-3">
            {isES
              ? `Perfil default (${MARKET_STATS.mcpTools} tools) · legacy: ${MARKET_STATS.mcpToolsLegacy} tools con aliases`
              : `Default profile (${MARKET_STATS.mcpTools} tools) · legacy: ${MARKET_STATS.mcpToolsLegacy} tools with aliases`}
          </p>
        </div>
      </section>

      <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20">
        <div className="max-w-[720px] mx-auto">
          <PrereqBlock level="mcp" isES={isES} />
          <div className="flex flex-wrap gap-2 mb-4 justify-center">
            {(Object.keys(MCP_CONFIG) as (keyof typeof MCP_CONFIG)[]).map((k) => (
              <button
                key={k}
                type="button"
                onClick={() => setIdeTab(k)}
                className={`font-label-caps px-4 py-1.5 capitalize transition-colors ${
                  ideTab === k
                    ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]"
                    : "glass-panel text-[var(--cm-on-surface-variant)] hover:text-[#0f172a]"
                }`}
              >
                {k}
              </button>
            ))}
            <button type="button" onClick={copy} className="font-label-caps px-4 py-1.5 bg-[var(--cm-surface-high)] text-[var(--cm-on-surface)] border border-[var(--cm-outline-variant)] hover:border-[var(--cm-mint)]/50">
              {copied ? (isES ? "Copiado" : "Copied") : (isES ? "Copiar config" : "Copy config")}
            </button>
          </div>
          <pre className="text-left code-block-cyber text-[var(--cm-mint)] p-5 overflow-x-auto">
            {MCP_CONFIG[ideTab]}
          </pre>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-4 text-center">
            {isES ? "Requiere" : "Requires"}{" "}
            <code className="font-mono text-[var(--cm-mint)]">{MARKET_STATS.pipInstallCmd}</code> · Manifest:{" "}
            <a href="/mcp.json" className="text-[var(--cm-mint)] underline">mcp.json</a>
            {" "}· Docs:{" "}
            <a href="/llms.txt" className="text-[var(--cm-mint)] underline">llms.txt</a>
          </p>
          {ideTab === "vscode" && (
            <p className="text-xs text-[var(--cm-on-surface-variant)]/80 mt-3 text-center max-w-lg mx-auto leading-relaxed">
              {isES
                ? "VS Code usa transporte stdio local (market-mcp). No uses la URL remota /mcp — ese endpoint es Streamable HTTP para Claude.ai y clientes compatibles."
                : "VS Code uses local stdio transport (market-mcp). Do not use the remote /mcp URL — that endpoint is Streamable HTTP for Claude.ai and compatible clients."}
            </p>
          )}
        </div>
      </section>

      <section className="py-16 px-[var(--cm-gutter)]">
        <div className="max-w-[720px] mx-auto text-center">
          <h2 className="section-title mb-2">
            {isES ? "Bundles (Shop · Intel · Account)" : "Bundles (Shop · Intel · Account)"}
          </h2>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mb-6 max-w-lg mx-auto">
            {isES
              ? `Perfil con ${MARKET_STATS.mcpTools} herramientas. Use MCP_TOOL_PROFILE=legacy para ${MARKET_STATS.mcpToolsLegacy} tools (aliases incluidos).`
              : `Profile with ${MARKET_STATS.mcpTools} tools. Set MCP_TOOL_PROFILE=legacy for ${MARKET_STATS.mcpToolsLegacy} tools (includes aliases).`}
          </p>

          <div className="flex flex-wrap gap-2 mb-6 justify-center">
            {(Object.keys(BUNDLE_LABELS) as BundleKey[]).map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => setBundleTab(key)}
                className={`font-label-caps px-4 py-1.5 capitalize transition-colors ${
                  bundleTab === key
                    ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]"
                    : "glass-panel text-[var(--cm-on-surface-variant)] hover:text-[#0f172a]"
                }`}
              >
                {isES ? BUNDLE_LABELS[key].es : BUNDLE_LABELS[key].en}
                <span className="ml-1 opacity-70">({MARKET_STATS.mcpBundles[key].length})</span>
              </button>
            ))}
          </div>

          <p className="text-sm text-[var(--cm-on-surface-variant)] mb-6">
            {isES ? BUNDLE_INTRO[bundleTab].es : BUNDLE_INTRO[bundleTab].en}
          </p>

          <ul className="text-left space-y-3 mb-10 max-w-lg mx-auto">
            {bundleTools.map((tool) => (
              <li
                key={tool.id}
                className={`glass-panel rounded-lg px-4 py-3 border ${
                  tool.canonical
                    ? "border-[var(--cm-mint)]/40 bg-[var(--cm-mint)]/5"
                    : "border-[var(--cm-outline-variant)]/30"
                }`}
              >
                <div className="flex items-center gap-2 flex-wrap">
                  <code className="font-mono text-sm text-[var(--cm-mint)]">{tool.id}</code>
                  {tool.canonical && (
                    <span className="font-label-caps text-[10px] px-2 py-0.5 rounded-full bg-[var(--cm-mint)]/20 text-[var(--cm-mint)]">
                      {isES ? "canónica" : "canonical"}
                    </span>
                  )}
                </div>
                <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1 leading-relaxed">
                  {tool.description}
                </p>
              </li>
            ))}
          </ul>

          <p className="text-xs text-[var(--cm-on-surface-variant)]/60">
            {isES
              ? `+ ${MARKET_STATS.mcpToolsLegacy - MARKET_STATS.mcpTools} herramientas más en perfil legacy (advanced, admin, aliases)`
              : `+ ${MARKET_STATS.mcpToolsLegacy - MARKET_STATS.mcpTools} more tools in legacy profile (advanced, admin, aliases)`}
          </p>
          <a href="/llms-full.txt" className="inline-block mt-8 text-sm font-semibold text-[var(--cm-mint)] underline">
            {isES ? "Flujos recomendados por ICP →" : "Recommended ICP flows →"}
          </a>
        </div>
      </section>
    </>
  );
}
