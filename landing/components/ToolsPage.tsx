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
      <section className="py-24 px-6 text-center border-b border-[#c5edab]">
        <div className="max-w-[720px] mx-auto">
          <p className="text-xs font-mono uppercase tracking-[0.15em] text-[var(--wise-body)] mb-4">
            MCP · AI shopping API
          </p>
          <h1 className="text-[clamp(28px,5vw,48px)] font-black text-[var(--wise-ink)] mb-4 tracking-tight">
            36 MCP tools for e-commerce agents
          </h1>
          <p className="text-base text-[var(--wise-body)] max-w-[540px] mx-auto leading-relaxed">
            Commerce API for AI agents — search, compare, basket, and checkout across 30 retailers.
            Copy a config, run <code className="font-mono text-sm">pip install cli-market</code>, connect your IDE.
          </p>
        </div>
      </section>

      <section className="py-16 px-6 border-b border-[#c5edab]">
        <div className="max-w-[720px] mx-auto">
          <div className="flex flex-wrap gap-2 mb-4 justify-center">
            {(Object.keys(MCP_CONFIG) as (keyof typeof MCP_CONFIG)[]).map((k) => (
              <button
                key={k}
                type="button"
                onClick={() => setTab(k)}
                className={`rounded-full px-4 py-1.5 text-sm font-medium capitalize ${
                  tab === k
                    ? "bg-[var(--wise-green)] text-[var(--wise-ink)]"
                    : "bg-white border border-[#c5edab] text-[var(--wise-body)]"
                }`}
              >
                {k}
              </button>
            ))}
            <button
              type="button"
              onClick={copy}
              className="rounded-full px-4 py-1.5 text-sm font-medium bg-[var(--wise-ink)] text-white"
            >
              {copied ? "Copied" : "Copy config"}
            </button>
          </div>
          <pre className="text-left bg-[var(--wise-ink)] text-[#9fe870] rounded-2xl p-5 text-[11px] leading-relaxed overflow-x-auto font-mono">
            {MCP_CONFIG[tab]}
          </pre>
          <p className="text-xs text-[var(--wise-mute)] mt-4 text-center">
            Requires <code className="font-mono">pip install cli-market</code> · Manifest:{" "}
            <a href="/server.json" className="underline">
              server.json
            </a>{" "}
            · Docs:{" "}
            <a href="/llms.txt" className="underline">
              llms.txt
            </a>
          </p>
        </div>
      </section>

      <section className="py-16 px-6">
        <div className="max-w-[720px] mx-auto text-center">
          <h2 className="text-xl font-medium text-[var(--wise-ink)] mb-6">Popular MCP tools</h2>
          <div className="flex flex-wrap justify-center gap-2">
            {TOOLS.map((t) => (
              <span
                key={t}
                className="font-mono text-[11px] bg-white border border-[#c5edab] rounded-full px-3 py-1 text-[var(--wise-body)]"
              >
                {t}
              </span>
            ))}
          </div>
          <p className="text-xs text-[var(--wise-mute)] mt-6">+ 24 more tools in the full registry</p>
          <a
            href="https://github.com/Treevu-ai/cli-market-world"
            className="inline-block mt-8 text-sm font-semibold text-[var(--wise-green-hover)] underline"
          >
            Full tool list on GitHub →
          </a>
        </div>
      </section>
    </>
  );
}
