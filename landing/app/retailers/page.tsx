import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import RetailerApplyForm from "@/components/RetailerApplyForm";

export default function RetailersPage() {
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
              { "@type": "Question", name: "How do I list my store on CLI Market?",
                acceptedAnswer: { "@type": "Answer", text: "Generate a read-only API token from your Shopify, Magento, or VTEX admin panel. Send it to us. Your products appear in AI agent searches in 30 seconds. Free. Forever." }},
              { "@type": "Question", name: "Is CLI Market free for retailers?",
                acceptedAnswer: { "@type": "Answer", text: "Yes. Completely free. MIT licensed. No hidden fees, no usage limits, no credit card required." }},
              { "@type": "Question", name: "What platforms does CLI Market support?",
                acceptedAnswer: { "@type": "Answer", text: "VTEX, Shopify, and Magento. We connect via public catalog APIs — zero development required from your side." }},
              { "@type": "Question", name: "How many retailers are already on CLI Market?",
                acceptedAnswer: { "@type": "Answer", text: "60 retailers across 8 countries (30 verified active): Peru, Argentina, Mexico, Colombia, Chile, Brazil, Italy, and France. 43,000+ real prices refreshed every 8 hours." }},
              { "@type": "Question", name: "What is GEO and why does my store need it?",
                acceptedAnswer: { "@type": "Answer", text: "GEO (Generative Engine Optimization) is the equivalent of SEO for AI agents. When AI assistants like ChatGPT and Claude search for products, they use structured data indexes like CLI Market. If your store isn't indexed, you're invisible to the fastest-growing shopping channel." }},
            ],
          }),
        }}
      />

      <div className="relative z-10">
        <section className="py-24 px-[var(--cm-gutter)] text-center border-b border-[var(--cm-outline-variant)]/20 pt-28">
          <div className="max-w-[720px] mx-auto">
            <p className="section-eyebrow mb-4">CLI Market for Retailers</p>
            <h1 className="font-display text-[clamp(1.75rem,5vw,3rem)] leading-tight font-bold text-white mb-3 tracking-tight">
              Your brand, inside AI agents.<br />Free. Today.
            </h1>
            <p className="text-[11px] text-[#ffbd2e] max-w-[500px] mx-auto mb-6 font-medium">
              Free forever. Limited spots per country.
            </p>
            <p className="text-base text-[var(--cm-on-surface-variant)] max-w-[500px] mx-auto leading-relaxed">
              When your products are indexed in CLI Market, AI agents discover, compare, and drive purchase traffic to your store. This is GEO — the SEO of the agent era.
            </p>
          </div>
        </section>

        <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20 landing-section-alt">
          <div className="max-w-[720px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            {[
              { n: "30", l: "Retailers live" },
              { n: "43K+", l: "Prices indexed" },
              { n: "8", l: "Countries" },
              { n: "30s", l: "To integrate" },
            ].map((s) => (
              <div key={s.l}>
                <div className="text-3xl font-black text-[var(--cm-mint)]">{s.n}</div>
                <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{s.l}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="py-16 px-[var(--cm-gutter)] border-b border-[var(--cm-outline-variant)]/20">
          <div className="max-w-[720px] mx-auto">
            <h2 className="section-title mb-12 text-center">What you get</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                { t: "Agent-driven traffic", d: "AI agents search and compare autonomously. Your products appear in their results — just like SEO, but for the agent economy. Every day you're not here, your competitor is.", i: "🤖" },
                { t: "Competitive edge", d: "See how your prices compare to 30 retailers in real time. Track competitors, adjust pricing, and never lose a sale to an unseen rival.", i: "📊" },
                { t: "Zero effort, zero cost", d: "Generate a read-only API token. 30 seconds. No SDK, no integration, no maintenance. Free forever. MIT.", i: "⚡" },
              ].map((b) => (
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
            <h2 className="section-title mb-12 text-center">How to get listed — 30 seconds</h2>
            <div className="space-y-4">
              {[
                { step: "01", title: "Shopify: Storefront API token", desc: "Settings → Apps → Manage private apps → Create app. Read-only catalog scope. No customer data. 30 seconds.", cmd: "Admin → Settings → Apps → Manage private apps" },
                { step: "02", title: "Magento: REST API integration", desc: "Create an integration with catalog read-only. We access /V1/products to index your catalog.", cmd: "System → Integrations → Add New → Catalog (read only)" },
                { step: "03", title: "VTEX: already connected", desc: "If you're on VTEX with a public catalog, you're probably already indexable. No token needed.", cmd: "Zero action required — we auto-detect VTEX stores" },
              ].map((s) => (
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
            <h2 className="section-title mb-2">Ready to get listed?</h2>
            <p className="text-sm text-[var(--cm-on-surface-variant)] mb-8">Free. Forever. Self-serve form below.</p>
            <RetailerApplyForm />
            <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-8">
              Prefer email?{" "}
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
