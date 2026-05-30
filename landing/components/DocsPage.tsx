"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";

type SnippetTab = "curl" | "python" | "mcp";

const SIDEBAR = {
  start: [
    { id: "quickstart", es: "Quickstart", en: "Quickstart" },
    { id: "auth", es: "Autenticación", en: "Authentication" },
  ],
  core: [
    { id: "compare", es: "Compare", en: "Compare" },
    { id: "basket", es: "Basket", en: "Basket" },
    { id: "intel", es: "Intelligence", en: "Intelligence" },
  ],
  integrations: [{ id: "mcp", es: "MCP Tools", en: "MCP Tools" }],
  governance: [
    { id: "limits", es: "Rate limits", en: "Rate limits" },
    { id: "errors", es: "Errores", en: "Errors" },
  ],
};

const SNIPPETS: Record<SnippetTab, string> = {
  curl: `curl -X POST ${API_URL}/products/compare \\
  -H "Authorization: Bearer $CLI_MARKET_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"query":"aceite de girasol 900ml","country":"AR","limit":8}'`,
  python: `import httpx

r = httpx.post(
    "${API_URL}/products/compare",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": "aceite de girasol 900ml", "country": "AR", "limit": 8},
)
print(r.json())`,
  mcp: `{
  "mcpServers": {
    "cli-market": {
      "command": "market-mcp",
      "args": []
    }
  }
}`,
};

export default function DocsPage() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [tab, setTab] = useState<SnippetTab>("curl");
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(SNIPPETS[tab]);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const t = (es: string, en: string) => (isES ? es : en);

  return (
    <div className="pt-20 flex min-h-screen max-w-[1440px] mx-auto">
      <aside className="hidden lg:block w-72 border-r border-[var(--cm-outline-variant)]/20 sticky top-20 h-[calc(100vh-80px)] overflow-y-auto px-6 py-10">
        <div className="space-y-8">
          {[
            { key: "start", label: t("GETTING STARTED", "GETTING STARTED") },
            { key: "core", label: t("CORE API", "CORE API") },
            { key: "integrations", label: t("INTEGRATIONS", "INTEGRATIONS") },
            { key: "governance", label: t("GOVERNANCE", "GOVERNANCE") },
          ].map(({ key, label }) => (
            <div key={key}>
              <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mb-4 tracking-widest">{label}</h3>
              <ul className="space-y-3">
                {SIDEBAR[key as keyof typeof SIDEBAR].map((item) => (
                  <li key={item.id}>
                    <a
                      href={`#${item.id}`}
                      className="font-mono text-sm text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors"
                    >
                      {isES ? item.es : item.en}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </aside>

      <main className="flex-1 px-6 md:px-8 py-10 max-w-3xl border-r border-[var(--cm-outline-variant)]/10">
        <section className="mb-16 scroll-mt-24" id="introduction">
          <h1 className="font-display text-[clamp(1.75rem,4vw,2.75rem)] font-bold text-white mb-4 leading-tight">
            {t(
              "Infraestructura para agentes de IA y equipos de pricing en LatAm",
              "Infrastructure for AI agents & pricing teams in LatAm",
            )}
          </h1>
          <p className="text-[var(--cm-on-surface-variant)] leading-relaxed">
            {t(
              "CLI Market entrega precios de retail verificados vía REST, CLI y MCP. Diseñado para agentes autónomos y equipos comerciales que necesitan spreads, canasta e inflación con refresh cada 8 h.",
              "CLI Market delivers verified retail prices via REST, CLI, and MCP. Built for autonomous agents and commercial teams that need spreads, basket, and inflation with 8 h refresh.",
            )}
          </p>
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="card-cyber header-strip p-6">
              <h4 className="font-label-caps text-[var(--cm-mint)] mb-2">FREE TIER</h4>
              <p className="font-mono text-lg text-white">1,000 req/day</p>
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-1">{t("Ideal para prototipos.", "Ideal for prototyping.")}</p>
            </div>
            <div className="card-cyber header-strip p-6 energy-border-active">
              <h4 className="font-label-caps text-[var(--cm-mint)] mb-2">PRO TIER</h4>
              <p className="font-mono text-lg text-white">10,000 req/day</p>
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-1">{t("Producción y export.", "Production and export.")}</p>
            </div>
          </div>
        </section>

        <section className="mb-16 scroll-mt-24" id="quickstart">
          <SectionHead n={1} title={t("Quickstart", "Quickstart")} />
          <p className="text-[var(--cm-on-surface-variant)] mb-6">{t("Instala la CLI y autentica tu sesión.", "Install the CLI and authenticate your session.")}</p>
          <CodeBlock>{`pip install cli-market\nmarket login`}</CodeBlock>
        </section>

        <section className="mb-16 scroll-mt-24" id="auth">
          <SectionHead n={2} title={t("Autenticación", "Authentication")} />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            {t("Usa Bearer token en HTTP o sesión CLI tras ", "Use Bearer token over HTTP or CLI session after ")}
            <code className="text-[var(--cm-mint)]">market login</code>.
          </p>
          <CodeBlock>{`Authorization: Bearer <token-from-market-login>`}</CodeBlock>
        </section>

        <section className="mb-16 scroll-mt-24" id="compare">
          <SectionHead n={3} title="Compare" />
          <p className="text-[var(--cm-on-surface-variant)] mb-6">
            <code className="text-[var(--cm-mint)]">POST /products/compare</code>
            {t(" — fuzzy match multi-retailer.", " — multi-retailer fuzzy match.")}
          </p>
          <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mb-3">{t("REQUEST", "REQUEST")}</h3>
          <CodeBlock>{`{
  "query": "aceite de girasol 900ml",
  "country": "AR",
  "limit": 8
}`}</CodeBlock>
          <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mt-8 mb-3">{t("RESPONSE", "RESPONSE")}</h3>
          <CodeBlock>{`{
  "results": [
    {"store": "carrefour_ar", "name": "...", "price": 2100.5, "currency": "ARS"},
    {"store": "jumbo_ar", "name": "...", "price": 2050.0, "currency": "ARS"}
  ]
}`}</CodeBlock>
        </section>

        <section className="mb-16 scroll-mt-24" id="basket">
          <SectionHead n={4} title="Basket" />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            <code className="text-[var(--cm-mint)]">POST /v1/basket/compare</code>
            {t(" — canasta multi-ítem por cadena.", " — multi-item basket by chain.")}
          </p>
          <CodeBlock>{`market basket "arroz:1 aceite:1 leche:1" --country AR`}</CodeBlock>
        </section>

        <section className="mb-16 scroll-mt-24" id="intel">
          <SectionHead n={5} title="Intelligence" />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            {t("Endpoints comerciales: ", "Commercial endpoints: ")}
            <code className="text-[var(--cm-mint)]">/v1/prices</code>,{" "}
            <code className="text-[var(--cm-mint)]">/v1/dispersion</code>,{" "}
            <code className="text-[var(--cm-mint)]">/v1/intel/inflation</code>.
          </p>
          <a href="/intelligence-pilot-es.md" className="text-[var(--cm-mint)] underline text-sm">
            {t("One-pager piloto Intelligence →", "Intelligence pilot one-pager →")}
          </a>
        </section>

        <section className="mb-16 scroll-mt-24" id="mcp">
          <SectionHead n={6} title={`MCP Tools (${MARKET_STATS.mcpTools})`} />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            {t("Configs listas en ", "Ready configs at ")}
            <a href="/tools" className="text-[var(--cm-mint)] underline">/tools</a>.
          </p>
        </section>

        <section className="mb-16 scroll-mt-24" id="limits">
          <SectionHead n={7} title={t("Rate limits", "Rate limits")} />
          <ul className="text-sm text-[var(--cm-on-surface-variant)] space-y-2 list-disc pl-5">
            <li>Free: 1,000 {t("consultas/día", "requests/day")}</li>
            <li>Pro: 10,000 {t("consultas/día", "requests/day")}</li>
          </ul>
        </section>

        <section className="mb-16 scroll-mt-24" id="errors">
          <SectionHead n={8} title={t("Errores", "Errors")} />
          <p className="text-[var(--cm-on-surface-variant)] text-sm">
            {t("401 token inválido · 429 rate limit · 503 collector degradado. OpenAPI completo: ", "401 invalid token · 429 rate limit · 503 collector degraded. Full OpenAPI: ")}
            <a href={`${API_URL}/docs`} className="text-[var(--cm-mint)] underline" target="_blank" rel="noopener noreferrer">
              {API_URL}/docs
            </a>
          </p>
        </section>
      </main>

      <aside className="hidden xl:block w-96 px-6 py-10 sticky top-20 h-[calc(100vh-80px)]">
        <div className="glass-panel rounded-xl overflow-hidden cyber-glow-mint">
          <div className="bg-[var(--cm-surface-highest)]/50 px-4 py-3 flex items-center justify-between border-b border-[var(--cm-outline-variant)]/20">
            <div className="flex gap-4">
              {(["curl", "python", "mcp"] as SnippetTab[]).map((k) => (
                <button
                  key={k}
                  type="button"
                  onClick={() => setTab(k)}
                  className={`font-label-caps text-[10px] uppercase ${
                    tab === k ? "text-[var(--cm-mint)] border-b border-[var(--cm-mint)] pb-1" : "text-[var(--cm-on-surface-variant)]"
                  }`}
                >
                  {k}
                </button>
              ))}
            </div>
            <button type="button" onClick={copy} className="font-label-caps text-[10px] text-[var(--cm-on-surface-variant)] hover:text-white">
              {copied ? "OK" : "COPY"}
            </button>
          </div>
          <pre className="p-5 font-mono text-[11px] text-[var(--cm-mint)]/90 bg-black/40 overflow-x-auto whitespace-pre-wrap">{SNIPPETS[tab]}</pre>
        </div>

        <div className="mt-8 glass-panel p-5 rounded-xl border border-[var(--cm-mint)]/10">
          <div className="flex items-center gap-2 mb-3">
            <span className="h-2 w-2 rounded-full bg-[var(--cm-mint)] agent-pulse" />
            <h4 className="font-label-caps text-[var(--cm-mint)] tracking-wider">NETWORK STATUS</h4>
          </div>
          <div className="space-y-3 font-mono text-[11px]">
            <div className="flex justify-between text-[var(--cm-on-surface-variant)]">
              <span>API</span>
              <span className="text-white">{API_URL.replace("https://", "")}</span>
            </div>
            <div className="flex justify-between text-[var(--cm-on-surface-variant)]">
              <span>{t("Retailers verificados", "Verified retailers")}</span>
              <span className="text-white">{MARKET_STATS.retailersVerified}</span>
            </div>
            <div className="flex justify-between text-[var(--cm-on-surface-variant)]">
              <span>Refresh</span>
              <span className="text-white">{MARKET_STATS.pricesRefreshHours}h</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
}

function SectionHead({ n, title }: { n: number; title: string }) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <span className="h-8 w-8 rounded-full bg-[var(--cm-mint)]/20 flex items-center justify-center text-[var(--cm-mint)] font-mono text-sm">{n}</span>
      <h2 className="font-display text-xl font-semibold text-white">{title}</h2>
    </div>
  );
}

function CodeBlock({ children }: { children: string }) {
  return (
    <div className="code-block-cyber p-4">
      <pre className="code-snippet text-[var(--cm-mint)]/90 whitespace-pre-wrap">{children}</pre>
    </div>
  );
}
