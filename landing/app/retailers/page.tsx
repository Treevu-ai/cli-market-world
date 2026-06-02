import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import RetailerApplyForm from "@/components/RetailerApplyForm";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLang } from "@/lib/LanguageContext";

export default function RetailersPage() {
  const { lang } = useLang();
  const isES = lang === "es";

  const stats = [
    { n: String(MARKET_STATS.retailersVerified), l: isES ? "Retailers activos" : "Retailers live" },
    { n: MARKET_STATS.pricesVerifiedLabel, l: isES ? "Precios indexados" : "Prices indexed" },
    { n: String(MARKET_STATS.countries), l: isES ? "Pa\u00edses" : "Countries" },
    { n: "30s", l: isES ? "Para integrar" : "To integrate" },
  ];

  const benefits = [
    {
      t: isES ? "Tr\u00e1fico desde agentes" : "Agent-driven traffic",
      d: isES
        ? "Los agentes de IA buscan y comparan de forma aut\u00f3noma. Tus productos aparecen en sus resultados \u2014 como SEO, pero para la econom\u00eda de agentes. Cada d\u00eda que no est\u00e1s, tu competidor s\u00ed."
        : "AI agents search and compare autonomously. Your products appear in their results \u2014 just like SEO, but for the agent economy. Every day you're not here, your competitor is.",
      i: "\ud83e\udd16",
    },
    {
      t: isES ? "Ventaja competitiva" : "Competitive edge",
      d: isES
        ? `Compara tus precios contra ${MARKET_STATS.retailersVerified} retailers en tiempo real. Sigue a tus competidores, ajusta precios, y nunca pierdas una venta frente a un rival invisible.`
        : `See how your prices compare to ${MARKET_STATS.retailersVerified} retailers in real time. Track competitors, adjust pricing, and never lose a sale to an unseen rival.`,
      i: "\ud83d\udcca",
    },
    {
      t: isES ? "Cero esfuerzo, cero costo" : "Zero effort, zero cost",
      d: isES
        ? "Genera un token de API de solo lectura. 30 segundos. Sin SDK, sin integraci\u00f3n, sin mantenimiento. Gratis para siempre. MIT."
        : "Generate a read-only API token. 30 seconds. No SDK, no integration, no maintenance. Free forever. MIT.",
      i: "\u26a1",
    },
  ];

  const steps = [
    {
      step: "01",
      title: isES ? "Shopify: token de Storefront API" : "Shopify: Storefront API token",
      desc: isES
        ? "Configuraci\u00f3n \u2192 Apps \u2192 Gestionar apps privadas \u2192 Crear app. Alcance cat\u00e1logo de solo lectura. Sin datos de clientes. 30 segundos."
        : "Settings \u2192 Apps \u2192 Manage private apps \u2192 Create app. Read-only catalog scope. No customer data. 30 seconds.",
      cmd: "Admin \u2192 Settings \u2192 Apps \u2192 Manage private apps",
    },
    {
      step: "02",
      title: isES ? "Magento: integraci\u00f3n REST API" : "Magento: REST API integration",
      desc: isES
        ? "Crea una integraci\u00f3n con cat\u00e1logo de solo lectura. Accedemos a /V1/products para indexar tu cat\u00e1logo."
        : "Create an integration with catalog read-only. We access /V1/products to index your catalog.",
      cmd: "System \u2192 Integrations \u2192 Add New \u2192 Catalog (read only)",
    },
    {
      step: "03",
      title: isES ? "VTEX: ya conectado" : "VTEX: already connected",
      desc: isES
        ? "Si est\u00e1s en VTEX con cat\u00e1logo p\u00fablico, probablemente ya sos indexable. Sin token necesario."
        : "If you're on VTEX with a public catalog, you're probably already indexable. No token needed.",
      cmd: isES ? "Cero acci\u00f3n requerida \u2014 detectamos tiendas VTEX autom\u00e1ticamente" : "Zero action required \u2014 we auto-detect VTEX stores",
    },
  ];

  return (
    <main className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            mainEntity: [
              {
                "@type": "Question",
                name: isES ? "\u00bfC\u00f3mo listo mi tienda en CLI Market?" : "How do I list my store on CLI Market?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? "Genera un token de API de solo lectura desde tu panel de Shopify, Magento o VTEX. Env\u00edanoslo. Tus productos aparecen en b\u00fasquedas de agentes de IA en 30 segundos. Gratis. Para siempre."
                    : "Generate a read-only API token from your Shopify, Magento, or VTEX admin panel. Send it to us. Your products appear in AI agent searches in 30 seconds. Free. Forever.",
                },
              },
              {
                "@type": "Question",
                name: isES ? "\u00bfCLI Market es gratis para retailers?" : "Is CLI Market free for retailers?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? "S\u00ed. Completamente gratis. Licencia MIT. Sin costos ocultos, sin l\u00edmites de uso, sin tarjeta de cr\u00e9dito."
                    : "Yes. Completely free. MIT licensed. No hidden fees, no usage limits, no credit card required.",
                },
              },
              {
                "@type": "Question",
                name: isES ? "\u00bfQu\u00e9 plataformas soporta CLI Market?" : "What platforms does CLI Market support?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? "VTEX, Shopify y Magento. Nos conectamos via APIs p\u00fablicas de cat\u00e1logo \u2014 cero desarrollo de tu lado."
                    : "VTEX, Shopify, and Magento. We connect via public catalog APIs \u2014 zero development required from your side.",
                },
              },
              {
                "@type": "Question",
                name: isES ? "\u00bfCu\u00e1ntos retailers ya est\u00e1n en CLI Market?" : "How many retailers are already on CLI Market?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? `${MARKET_STATS.retailersDefined} retailers en ${MARKET_STATS.countries} pa\u00edses (${MARKET_STATS.retailersVerified} verificados activos): ${MARKET_STATS.countryCodes.join(", ")}. ${MARKET_STATS.pricesVerifiedLabel} precios reales actualizados cada ${MARKET_STATS.pricesRefreshHours} horas.`
                    : `${MARKET_STATS.retailersDefined} retailers across ${MARKET_STATS.countries} countries (${MARKET_STATS.retailersVerified} verified active): ${MARKET_STATS.countryCodes.join(", ")}. ${MARKET_STATS.pricesVerifiedLabel} real prices refreshed every ${MARKET_STATS.pricesRefreshHours} hours.`,
                },
              },
              {
                "@type": "Question",
                name: isES ? "\u00bfQu\u00e9 es GEO y por qu\u00e9 mi tienda lo necesita?" : "What is GEO and why does my store need it?",
                acceptedAnswer: {
                  "@type": "Answer",
                  text: isES
                    ? "GEO (Generative Engine Optimization) es el equivalente de SEO para agentes de IA. Cuando asistentes como ChatGPT y Claude buscan productos, usan \u00edndices de datos estructurados como CLI Market. Si tu tienda no est\u00e1 indexada, eres invisible para el canal de compras de mayor crecimiento."
                    : "GEO (Generative Engine Optimization) is the equivalent of SEO for AI agents. When AI assistants like ChatGPT and Claude search for products, they use structured data indexes like CLI Market. If your store isn't indexed, you're invisible to the fastest-growing shopping channel.",
                },
              },
            ],
          }),
        }}
      />

      <div className="relative z-10">
        <section className="py-24 px-[var(--cm-gutter)] text-center border-b border-[var(--cm-outline-variant)]/20 pt-28">
          <div className="max-w-[720px] mx-auto">
            <p className="section-eyebrow mb-4">
              {isES ? "CLI Market para Retailers" : "CLI Market for Retailers"}
            </p>
            <h1 className="font-display text-[clamp(1.75rem,5vw,3rem)] leading-tight font-bold text-white mb-3 tracking-tight">
              {isES
                ? "Tu marca, dentro de agentes de IA. Gratis. Hoy."
                : "Your brand, inside AI agents. Free. Today."}
            </h1>
            <p className="text-[11px] text-[#ffbd2e] max-w-[500px] mx-auto mb-6 font-medium">
              {isES ? "Gratis para siempre. Cupos limitados por pa\u00eds." : "Free forever. Limited spots per country."}
            </p>
            <p className="text-base text-[var(--cm-on-surface-variant)] max-w-[500px] mx-auto leading-relaxed">
              {isES
                ? "Cuando tus productos est\u00e1n indexados en CLI Market, los agentes de IA los descubren, comparan y dirigen tr\u00e1fico de compra a tu tienda. Esto es GEO \u2014 el SEO de la era de los agentes."
                : "When your products are indexed in CLI Market, AI agents discover, compare, and drive purchase traffic to your store. This is GEO \u2014 the SEO of the agent era."}
            </p>
          </div>
        </section>

        <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20 landing-section-alt">
          <div className="max-w-[720px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {stats.map((s) => (
              <div key={s.l}>
                <div className="text-3xl font-black text-[var(--cm-mint)]">{s.n}</div>
                <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{s.l}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20">
          <div className="max-w-[720px] mx-auto">
            <h2 className="section-title mb-12 text-center">
              {isES ? "Lo que obtienes" : "What you get"}
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {benefits.map((b) => (
                <div key={b.t} className="card-cyber header-strip p-6">
                  <div className="text-2xl mb-3">{b.i}</div>
                  <h3 className="text-sm font-bold text-white mb-2">{b.t}</h3>
                  <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">{b.d}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20">
          <div className="max-w-[560px] mx-auto">
            <h2 className="section-title mb-12 text-center">
              {isES ? "C\u00f3mo aparecer \u2014 30 segundos" : "How to get listed \u2014 30 seconds"}
            </h2>
            <div className="space-y-4">
              {steps.map((s) => (
                <div key={s.step} className="card-cyber p-5 flex gap-4">
                  <span className="text-[var(--cm-mint)] font-bold text-lg shrink-0">{s.step}</span>
                  <div>
                    <h3 className="text-sm font-bold text-white mb-1">{s.title}</h3>
                    <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed mb-2">{s.desc}</p>
                    <code className="text-[11px] text-[var(--cm-mint)]/80 bg-[var(--cm-surface-lowest)] px-2 py-0.5 rounded font-mono">{s.cmd}</code>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-24 px-[var(--cm-gutter)] text-center">
          <div className="max-w-[520px] mx-auto">
            <h2 className="section-title mb-2">
              {isES ? "\u00bfListo para aparecer?" : "Ready to get listed?"}
            </h2>
            <p className="text-sm text-[var(--cm-on-surface-variant)] mb-8">
              {isES ? "Gratis. Para siempre. Formulario abajo." : "Free. Forever. Self-serve form below."}
            </p>
            <RetailerApplyForm />
            <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-8">
              {isES ? "\u00bfPrefieres email? " : "Prefer email? "}
              <a href="mailto:hello@cli-market.dev?subject=CLI%20Market%20Retailer%20Listing" className="text-[var(--cm-mint)] underline">
                hello@cli-market.dev
              </a>
            </p>
          </div>
        </section>

        <Footer />
      </div>
    </main>
  );
}
