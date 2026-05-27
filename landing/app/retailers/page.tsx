import Footer from "@/components/Footer";

export default function RetailersPage() {
  return (
    <main className="min-h-screen bg-[var(--wise-canvas-soft)]">
      {/* Header */}
      <section className="py-24 px-6 text-center border-b border-[#c5edab]">
        <div className="max-w-[720px] mx-auto">
          <p className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-[0.15em] mb-6">
            CLI Market for Retailers
          </p>
          <h1 className="text-[clamp(28px,5vw,48px)] leading-[1.05] font-black text-[var(--wise-ink)] mb-4 tracking-tight">
            Your brand, inside AI agents.
          </h1>
          <p className="text-base text-[var(--wise-body)] max-w-[500px] mx-auto leading-relaxed">
            CLI Market is commerce infrastructure for autonomous AI agents. When your products are indexed here, agents can discover, compare, and drive purchase traffic to your store.
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="py-16 px-6 bg-white border-b border-[#c5edab]">
        <div className="max-w-[720px] mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {[
            { n: "27", l: "Retailers live" },
            { n: "9K+", l: "Prices indexed" },
            { n: "7", l: "Countries" },
            { n: "30s", l: "To integrate" },
          ].map((s) => (
            <div key={s.l}>
              <div className="text-3xl font-black text-[var(--wise-green)]">{s.n}</div>
              <div className="text-xs text-[var(--wise-body)] mt-1">{s.l}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Benefits */}
      <section className="py-24 px-6 border-b border-[#c5edab]">
        <div className="max-w-[720px] mx-auto">
          <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-12 text-center">What you get</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { t: "Agent-driven traffic", d: "AI agents search, compare, and purchase autonomously. Your products appear in their results — just like SEO, but for agents.", i: "🤖" },
              { t: "Competitive intelligence", d: "See how your prices compare to 27 retailers in real time. Spot gaps, track competitors, and adjust pricing with data.", i: "📊" },
              { t: "Zero technical effort", d: "Generate a read-only API token in 30 seconds. No SDK, no integration, no maintenance. We handle everything.", i: "⚡" },
            ].map((b) => (
              <div key={b.t} className="bg-[var(--wise-canvas)] rounded-3xl border border-[var(--wise-green-pale)] p-6">
                <div className="text-2xl mb-3">{b.i}</div>
                <h3 className="text-sm font-bold text-[var(--wise-ink)] mb-2">{b.t}</h3>
                <p className="text-xs text-[var(--wise-body)] leading-relaxed">{b.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 px-6 border-b border-[#c5edab]">
        <div className="max-w-[560px] mx-auto">
          <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-12 text-center">How it works</h2>
          <div className="space-y-4">
            {[
              { step: "01", title: "Shopify: generate a Storefront API token", desc: "Settings → Apps → Manage private apps → Create app. Read-only. No customer data. 30 seconds.", cmd: "Admin → Settings → Apps → Manage private apps" },
              { step: "02", title: "Magento: share REST API credentials", desc: "Create an integration with catalog read-only scope. We access /V1/products to index your catalog.", cmd: "System → Integrations → Add New → Catalog (read)" },
              { step: "03", title: "We index your catalog", desc: "Our collector runs every 8 hours. Your products appear in AI agent searches, price comparisons, and dashboards.", cmd: "Done. No code." },
            ].map((s) => (
              <div key={s.step} className="bg-[var(--wise-canvas)] rounded-3xl border border-[var(--wise-green-pale)] p-5 flex gap-4">
                <span className="text-[var(--wise-green)] font-bold text-lg shrink-0">{s.step}</span>
                <div>
                  <h3 className="text-sm font-bold text-[var(--wise-ink)] mb-1">{s.title}</h3>
                  <p className="text-xs text-[var(--wise-body)] leading-relaxed mb-2">{s.desc}</p>
                  <code className="text-[11px] text-[var(--wise-mute)] bg-[var(--wise-green-pale)] px-2 py-0.5 rounded">{s.cmd}</code>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 text-center">
        <div className="max-w-[480px] mx-auto">
          <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-3">Ready to get listed?</h2>
          <p className="text-sm text-[var(--wise-body)] mb-8">Send us your API token or ask any question. We handle the rest.</p>
          <a href="mailto:hello@cli-market.dev?subject=CLI%20Market%20Retailer%20Listing" className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[var(--wise-green-hover)] transition-colors">hello@cli-market.dev</a>
          <p className="text-[10px] text-[var(--wise-mute)] mt-4">MIT License · Open source · No lock-in</p>
        </div>
      </section>

      <Footer />
    </main>
  );
}
