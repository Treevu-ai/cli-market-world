"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";
import { sinapsisBillingPolicy } from "@/lib/billingCopy";
import { usePaymentsChannels } from "@/lib/useBillingCopy";
import PrereqBlock from "@/components/PrereqBlock";
import BillingCheckoutTrigger from "@/components/BillingCheckoutTrigger";

type SnippetTab = "curl" | "python" | "mcp";
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

const SIDEBAR = {
  start: [
    { id: "quickstart", es: "Quickstart", en: "Quickstart" },
    { id: "auth", es: "Autenticación", en: "Authentication" },
    { id: "billing", es: "Billing y planes", en: "Billing & plans" },
    { id: "doctor", es: "Doctor / readiness", en: "Doctor / readiness" },
  ],
  core: [
    { id: "compare", es: "Compare", en: "Compare" },
    { id: "basket", es: "Basket", en: "Basket" },
    { id: "intel", es: "Intelligence", en: "Intelligence" },
  ],
  integrations: [{ id: "mcp", es: "API Tools", en: "API Tools" }],
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
      "args": [],
      "env": {
        "MARKET_API_URL": "${API_URL}",
        "MCP_TOOL_PROFILE": "default"
      }
    }
  }
}`,
};

export default function DocsPage() {
  const { lang } = useLang();
  const isES = lang === "es";
  const paymentsLabel = usePaymentsChannels(isES);
  const [tab, setTab] = useState<SnippetTab>("curl");
  const [bundleTab, setBundleTab] = useState<BundleKey>("shop");
  const [copied, setCopied] = useState(false);
  const bundleTools = MARKET_STATS.mcpBundles[bundleTab];

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
              `CLI Market entrega precios de retail verificados vía REST y CLI. Diseñado para agentes autónomos y equipos comerciales que necesitan spreads, canasta e inflación con refresh cada ${MARKET_STATS.pricesRefreshHours} h.`,
              `CLI Market delivers verified retail prices via REST and CLI. Built for autonomous agents and commercial teams that need spreads, basket, and inflation with ${MARKET_STATS.pricesRefreshHours} h refresh.`,
            )}
          </p>
          <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="card-cyber header-strip p-6">
              <h4 className="font-label-caps text-[var(--cm-mint)] mb-2">FREE</h4>
              <p className="font-mono text-lg text-white">1,000 req/day</p>
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-1">
                {t("Lectura · búsqueda · API default.", "Read · search · default API profile.")}
              </p>
              <a href={MARKET_STATS.pypiUrl} className="text-xs text-[var(--cm-mint)] underline mt-2 inline-block" target="_blank" rel="noopener noreferrer">
                {MARKET_STATS.pipInstallCmd} →
              </a>
            </div>
            <div className="card-cyber header-strip p-6">
              <h4 className="font-label-caps text-[var(--cm-mint)] mb-2">STARTER</h4>
              <p className="font-mono text-lg text-white">2,000 req/mo · USD 9/mo</p>
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-1">
                {t("3 claves API · export CSV · alertas · sin checkout retail.", "3 API keys · CSV export · alerts · no retail checkout.")}
              </p>
              <a href="/#pricing" className="text-xs text-[var(--cm-mint)] underline mt-2 inline-block">
                {t("Elegir Starter →", "Choose Starter →")}
              </a>
            </div>
            <div className="card-cyber header-strip p-6 energy-border-active sm:col-span-2 lg:col-span-1">
              <h4 className="font-label-caps text-[var(--cm-mint)] mb-2">PRO</h4>
              <p className="font-mono text-lg text-white">10,000 req/day · USD 49/mo</p>
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-1">
                {t(
                  `Checkout ${paymentsLabel} · 10 claves · Intel.`,
                  `Checkout ${paymentsLabel} · 10 keys · Intel.`,
                )}
              </p>
              <p className="text-[10px] text-[var(--cm-signal)] mt-2 font-mono">
                {t("Pro Founding: USD 29/mo · 100 plazas", "Pro Founding: USD 29/mo · 100 seats")}
              </p>
              <a href="/#pricing" className="text-xs text-[var(--cm-mint)] underline mt-2 inline-block">
                {t("Ver planes →", "View plans →")}
              </a>
            </div>
          </div>
          <PrereqBlock level="cli" isES={isES} />
        </section>

        <section className="mb-16 scroll-mt-24" id="quickstart">
          <SectionHead n={1} title={t("Quickstart", "Quickstart")} />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
            {[
              { tier: "STARTER", price: "USD 9/mo", note: t("5k req/día · export CSV", "5k req/day · CSV export") },
              { tier: "PRO", price: "USD 49/mo", note: t("10k/día · checkout", "10k/day · checkout") },

            ].map((p) => (
              <div key={p.tier} className="card-cyber p-4 text-left">
                <p className="font-label-caps text-[10px] text-[var(--cm-mint)]/80">{p.tier}</p>
                <p className="font-mono text-sm text-white mt-1">{p.price}</p>
                <p className="text-[10px] text-[var(--cm-on-surface-variant)]/70 mt-1">{p.note}</p>
              </div>
            ))}
          </div>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/80 mb-6">
            {t("Detalle en ", "Details in ")}{" "}
            <a href="#billing" className="text-[var(--cm-mint)] underline">
              Billing
            </a>
            {" · "}
            <a href="/#pricing" className="text-[var(--cm-mint)] underline">
              /#pricing
            </a>
            .
          </p>
          <PrereqBlock level="cli" isES={isES} />
          <p className="text-[var(--cm-on-surface-variant)] mb-6">
            {t(
              "De pip install a precios reales en ~5 min. Recomendado: onboarding guiado.",
              "From pip install to real prices in ~5 min. Recommended: guided onboarding.",
            )}
          </p>
          <CodeBlock>{`${MARKET_STATS.pipInstallCmd}
market init
market search "leche" --country PE
market doctor`}</CodeBlock>
          <p className="text-[var(--cm-on-surface-variant)] text-sm mt-4">
            {t(
              "market init verifica API, crea cuenta gratuita si no hay sesión, muestra readiness %.",
              "market init checks API, creates a free account if needed, shows readiness %.",
            )}
          </p>
        </section>

        <section className="mb-16 scroll-mt-24" id="auth">
          <SectionHead n={2} title={t("Autenticación", "Authentication")} />
          <PrereqBlock level="session" isES={isES} />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            {t(
              "Cuenta gratuita vía CLI o HTTP. La API key (sk-...) se muestra una sola vez.",
              "Free account via CLI or HTTP. The API key (sk-...) is shown once.",
            )}
          </p>
          <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mb-3">CLI</h3>
          <CodeBlock>{`market register
# Usuario: user-abc123...
# API key: sk-...   ← guárdela ahora`}</CodeBlock>
          <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mt-8 mb-3">HTTP</h3>
          <CodeBlock>{`curl -X POST ${API_URL}/auth/register \\
  -H "Content-Type: application/json"`}</CodeBlock>
          <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mt-8 mb-3">{t("RESPONSE", "RESPONSE")}</h3>
          <CodeBlock>{`{
  "username": "user-abc123...",
  "api_key": "sk-...",
  "message": "Account created"
}`}</CodeBlock>
          <p className="text-[var(--cm-on-surface-variant)] text-sm mt-4 mb-4">
            {t("Si ya tiene credenciales: ", "If you already have credentials: ")}
            <code className="text-[var(--cm-mint)]">market login</code>.
          </p>
          <CodeBlock>{`Authorization: Bearer sk-...`}</CodeBlock>
        </section>

        <section className="mb-16 scroll-mt-24" id="billing">
          <SectionHead n={3} title={t("Billing y planes", "Billing & plans")} />
          <PrereqBlock level="paid" isES={isES} />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            {t(
              "Build (API/MCP): Free, Starter ($9/mes), Pro ($49/mes o $490/año), Pro Founding ($29/mes, 100 plazas).",
              "Build (API/MCP): Free, Starter ($9/mo), Pro ($49/mo or $490/yr), Pro Founding ($29/mo, 100 seats).",
            )}
          </p>
          <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4 leading-relaxed rounded-lg border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/40 px-4 py-3">
            {sinapsisBillingPolicy(isES)}
          </p>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/80 mb-6">
            {t("Canales:", "Channels:")} {paymentsLabel}
          </p>
          <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mb-3">
            {t("CHECKOUT EN LA WEB", "WEB CHECKOUT")}
          </h3>
          <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4 leading-relaxed">
            {t(
              "Pro estándar: elige PayPal (USD) o soles (Mercado Pago · Yape · Plin). En Perú, soles aparece recomendado.",
              "Standard Pro: choose PayPal (USD) or soles (Mercado Pago · Yape · Plin). In Peru, soles is recommended.",
            )}
          </p>
          <div className="flex flex-wrap gap-3 mb-8">
            <BillingCheckoutTrigger kind={{ type: "build-pro" }} className="btn-mint" />
            <BillingCheckoutTrigger
              kind={{ type: "build-pro", annual: true }}
              className="rounded-full border border-[var(--cm-outline-variant)]/50 px-5 py-2.5 text-sm font-semibold text-white hover:border-[var(--cm-mint)] hover:text-[var(--cm-mint)] transition-colors"
              label_es="Pro anual $490/año →"
              label_en="Pro annual $490/yr →"
            />
          </div>
          <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mb-3">
            {t("CHECKOUT PROGRAMÁTICO", "PROGRAMMATIC CHECKOUT")}
          </h3>
          <CodeBlock>{`curl -X POST ${API_URL}/billing/build-checkout \\
  -H "Content-Type: application/json" \\
  -d '{
    "plan": "starter",
    "email": "dev@example.com",
    "return_url": "https://cli-market.dev/#pricing",
    "cancel_url": "https://cli-market.dev/#pricing"
  }'`}</CodeBlock>
          <p className="text-[var(--cm-on-surface-variant)] text-sm mt-4 mb-4">
            {t(
              "Valores de plan: starter | pro | pro_founding | pro_annual. La respuesta incluye approve_url para redirigir al usuario. Pro Founding usa promo founding100 en PayPal.",
              "Plan values: starter | pro | pro_founding | pro_annual. Response includes approve_url for redirect. Pro Founding uses PayPal promo founding100.",
            )}
          </p>
          <h3 className="font-label-caps text-[var(--cm-on-surface-variant)]/50 mb-3">CLI</h3>
          <CodeBlock>{`market register
market upgrade --plan starter
market upgrade --plan pro`}</CodeBlock>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-4">
            {t("Precios completos: ", "Full pricing: ")}{" "}
            <a href="/#pricing" className="text-[var(--cm-mint)] underline">/#pricing</a>.
          </p>
        </section>

        <section className="mb-16 scroll-mt-24" id="doctor">
          <SectionHead n={4} title={t("Doctor / readiness", "Doctor / readiness")} />
          <PrereqBlock level="cli" isES={isES} />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            {t(
              "Diagnóstico local: URL de API, salud, auth, tier, país por defecto y market-mcp en PATH.",
              "Local diagnostics: API URL, health, auth, tier, default country, and market-mcp on PATH.",
            )}
          </p>
          <CodeBlock>{`market doctor
market --json doctor`}</CodeBlock>
        </section>

        <section className="mb-16 scroll-mt-24" id="compare">
          <SectionHead n={5} title="Compare" />
          <PrereqBlock level="session" isES={isES} />
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
          <SectionHead n={6} title="Basket" />
          <PrereqBlock level="session" isES={isES} />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            <code className="text-[var(--cm-mint)]">POST /v1/basket/compare</code>
            {t(" — canasta multi-ítem por cadena.", " — multi-item basket by chain.")}
          </p>
          <CodeBlock>{`market basket "arroz:1 aceite:1 leche:1" --country AR`}</CodeBlock>
        </section>

        <section className="mb-16 scroll-mt-24" id="intel">
          <SectionHead n={7} title="Intelligence" />
          <PrereqBlock level="session" isES={isES} />
          <p className="text-[var(--cm-on-surface-variant)] mb-2 text-sm">
            {t(
              "Export CSV (`market_export`) requiere Starter o superior. Checkout retail requiere Pro.",
              "CSV export (`market_export`) requires Starter or above. Retail checkout requires Pro.",
            )}
          </p>
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
          <SectionHead n={8} title={`MCP Tools (${MARKET_STATS.mcpTools})`} />
          <PrereqBlock level="mcp" isES={isES} />
          <p className="text-[var(--cm-on-surface-variant)] mb-4">
            {t(
              `Perfil default: ${MARKET_STATS.mcpTools} herramientas (Shop · Intel · Account). Legacy: ${MARKET_STATS.mcpToolsLegacy} con aliases. Configs en `,
              `Default profile: ${MARKET_STATS.mcpTools} tools (Shop · Intel · Account). Legacy: ${MARKET_STATS.mcpToolsLegacy} with aliases. Configs at `,
            )}
            <a href="/tools" className="text-[var(--cm-mint)] underline">/tools</a>
            {" · "}
            <a href="/mcp.json" className="text-[var(--cm-mint)] underline">mcp.json</a>.
          </p>
          <div className="flex flex-wrap gap-2 mb-4">
            {(Object.keys(BUNDLE_LABELS) as BundleKey[]).map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => setBundleTab(key)}
                className={`font-label-caps px-3 py-1 text-xs capitalize transition-colors ${
                  bundleTab === key
                    ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)]"
                    : "glass-panel text-[var(--cm-on-surface-variant)] hover:text-white"
                }`}
              >
                {isES ? BUNDLE_LABELS[key].es : BUNDLE_LABELS[key].en}
                <span className="ml-1 opacity-70">({MARKET_STATS.mcpBundles[key].length})</span>
              </button>
            ))}
          </div>
          <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4">
            {isES ? BUNDLE_INTRO[bundleTab].es : BUNDLE_INTRO[bundleTab].en}
          </p>
          <ul className="space-y-2 mb-4">
            {bundleTools.map((tool) => (
              <li
                key={tool.id}
                className={`glass-panel rounded-lg px-3 py-2 border text-sm ${
                  tool.canonical
                    ? "border-[var(--cm-mint)]/40 bg-[var(--cm-mint)]/5"
                    : "border-[var(--cm-outline-variant)]/30"
                }`}
              >
                <div className="flex items-center gap-2 flex-wrap">
                  <code className="font-mono text-xs text-[var(--cm-mint)]">{tool.id}</code>
                  {tool.canonical && (
                    <span className="font-label-caps text-[9px] px-1.5 py-0.5 rounded-full bg-[var(--cm-mint)]/20 text-[var(--cm-mint)]">
                      {isES ? "canónica" : "canonical"}
                    </span>
                  )}
                </div>
                <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1 leading-relaxed">{tool.description}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="mb-16 scroll-mt-24" id="limits">
          <SectionHead n={9} title={t("Rate limits", "Rate limits")} />
          <PrereqBlock level="cli" isES={isES} />
          <ul className="text-sm text-[var(--cm-on-surface-variant)] space-y-3 list-none pl-0">
            <li>
              <strong className="text-white">Free</strong> — 1,000 {t("consultas/día", "requests/day")} · 1 {t("clave API (lectura)", "API key (read)")} · {MARKET_STATS.mcpTools} MCP · {t("historial 7 días", "7-day history")}
            </li>
            <li>
              <strong className="text-white">Starter</strong> — 2,000 {t("consultas/mes", "requests/mo")} · 3 {t("claves API", "API keys")} · export CSV · 3 {t("alertas", "alerts")} · USD 9/mo
            </li>
            <li>
              <strong className="text-white">Pro</strong> — 10,000 {t("consultas/día", "requests/day")} · 10 {t("claves (lectura/escritura)", "keys (read/write)")} · checkout · Intel MCP · USD 49/mo {t("o 490/año", "or 490/yr")}
            </li>
            <li>
              <strong className="text-white">Pro Founding</strong> — 10,000 {t("consultas/día", "requests/day")} · 10 {t("claves", "keys")} · checkout · Intel MCP · USD 29/mo {t("bloqueado · 100 plazas", "locked · 100 seats")}
            </li>
            <li>
              <strong className="text-white">Enterprise</strong> — {t("límites y SLAs a medida", "custom limits + SLAs")}
            </li>
          </ul>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mt-4">
            {t("Planes completos en ", "Full plans at ")}{" "}
            <a href="/#pricing" className="text-[var(--cm-mint)] underline">/#pricing</a>.
            {t(" Datos comerciales sujetos al ", " Commercial data subject to ")}{" "}
            <a href="/legal/dla" className="text-[var(--cm-mint)] underline">ALD/DLA</a>.
          </p>
        </section>

        <section className="mb-16 scroll-mt-24" id="errors">
          <SectionHead n={10} title={t("Errores", "Errors")} />
          <PrereqBlock level="cli" isES={isES} />
          <p className="text-[var(--cm-on-surface-variant)] text-sm">
            {t("401 token inválido · 429 rate limit · 503 collector degradado. OpenAPI completo: ", "401 invalid token · 429 rate limit · 503 collector degraded. Full OpenAPI: ")}
            <a href={`${API_URL}/docs`} className="text-[var(--cm-mint)] underline" target="_blank" rel="noopener noreferrer">
              {API_URL}/docs
            </a>
          </p>
        </section>
        <section className="mb-16 scroll-mt-24">
          <div className="card-cyber header-strip p-8 text-center energy-border-active">
            <h3 className="font-display text-xl font-semibold text-white mb-2">
              {t("¿Listo para Starter o Pro?", "Ready for Starter or Pro?")}
            </h3>
            <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4 max-w-md mx-auto">
              {t(
                "Free para lectura · Starter $9 para export · Pro $49 para checkout retail.",
                "Free for read · Starter $9 for export · Pro $49 for retail checkout.",
              )}
            </p>
            <a href="/#pricing" className="btn-action inline-flex px-6 py-3 text-sm font-bold">
              {t("Ver planes Build →", "View Build plans →")}
            </a>
          </div>
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