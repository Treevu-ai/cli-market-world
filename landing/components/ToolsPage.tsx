"use client";

import { useState } from "react";

const MCP_CONFIG = {
  cursor: `{
  "mcpServers": {
    "cli-market": {
      "command": "market-mcp",
      "args": [],
      "env": {}
    }
  }
}`,
  claude: `{
  "mcpServers": {
    "cli-market": {
      "command": "market-mcp",
      "args": []
    }
  }
}`,
  vscode: `{
  "servers": {
    "cli-market": {
      "type": "stdio",
      "command": "market-mcp"
    }
  }
}`,
};

const TOOLS = [
  "market_search",
  "market_compare",
  "market_basket",
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
          <p className="section-eyebrow mb-4">MCP · AI shopping API</p>
          <h1 className="font-display text-[clamp(1.75rem,5vw,3rem)] font-bold text-white mb-4 tracking-tight">
            36 MCP tools for e-commerce agents
          </h1>
          <p className="text-base text-[var(--cm-on-surface-variant)] max-w-[540px] mx-auto leading-relaxed">
            Commerce API for AI agents — search, compare, basket, and checkout across 30 retailers.
            Copy a config, run <code className="font-mono text-sm text-[var(--cm-mint)]">pip install cli-market</code>, connect your IDE.
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
              {copied ? "Copied" : "Copy config"}
            </button>
          </div>
          <pre className="text-left code-block-cyber text-[var(--cm-mint)] p-5 overflow-x-auto">
            {MCP_CONFIG[tab]}
          </pre>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-4 text-center">
            Requires <code className="font-mono text-[var(--cm-mint)]">pip install cli-market</code> · Manifest:{" "}
            <a href="/server.json" className="text-[var(--cm-mint)] underline">server.json</a>
            {" "}· Docs:{" "}
            <a href="/llms.txt" className="text-[var(--cm-mint)] underline">llms.txt</a>
          </p>
        </div>
      </section>

      <section className="py-16 px-[var(--cm-gutter)]">
        <div className="max-w-[720px] mx-auto text-center">
          <h2 className="section-title mb-6">Popular MCP tools</h2>
          <div className="flex flex-wrap justify-center gap-2">
            {TOOLS.map((t) => (
              <span key={t} className="font-mono text-[11px] glass-panel rounded-full px-3 py-1 text-[var(--cm-on-surface-variant)]">
                {t}
              </span>
            ))}
          </div>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mt-6">+ 24 more tools in the full registry</p>
          <a href="https://github.com/Treevu-ai/cli-market-world" className="inline-block mt-8 text-sm font-semibold text-[var(--cm-mint)] underline">
            Full tool list on GitHub →
          </a>
        </div>
      </section>
    </>
  );
}
