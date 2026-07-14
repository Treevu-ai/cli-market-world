"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import LatAmCoverageMap from "@/components/LatAmCoverageMap";
import ImpactTerminal from "@/components/ImpactTerminal";
import PriceTicker from "@/components/PriceTicker";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLang } from "@/lib/LanguageContext";
import { useLiveStats } from "@/hooks/useLiveStats";
import { PRICING_BUILD_HASH, PRICING_PROCURE_HASH } from "@/lib/siteNav";
import { TRIAL_DAYS } from "@/lib/buildPricingTiers";

const COVERAGE_ROWS = [
  { cc: "PE", stores: "Wong · Metro · Plaza Vea", noteEs: "supermercados · piloto FMCG orgánico", noteEn: "supermarkets · organic FMCG pilot" },
  { cc: "AR", stores: "Carrefour · Jumbo · Vea", noteEs: "supermercados · electro", noteEn: "supermarkets · electronics" },
  { cc: "BR", stores: "Carrefour · C&A · Drogaria Pacheco", noteEs: "super · moda · farmacia", noteEn: "grocery · fashion · pharmacy" },
  { cc: "MX", stores: "Chedraui · HEB · Liverpool", noteEs: "super · departamental", noteEn: "grocery · department" },
  { cc: "CL", stores: "Falabella · Paris · Ripley · Cruz Verde", noteEs: "departamental · farmacia", noteEn: "department · pharmacy" },
  { cc: "CO", stores: "Éxito · Falabella · Cruz Verde", noteEs: "super · departamental", noteEn: "grocery · department" },
];

export default function ImpactLanding() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { pypiChip, goldenLinkagePct } = useLiveStats();
  const linkageRounded =
    goldenLinkagePct != null && goldenLinkagePct > 0 ? Math.round(goldenLinkagePct) : null;
  const spreadPctRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const els = document.querySelectorAll(".impact-rv");
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          e.target.classList.add("impact-rv-on");

          e.target.querySelectorAll<HTMLElement>("[data-count]").forEach((n) => {
            const target = Number(n.dataset.count);
            const suffix = n.dataset.suffix ?? "";
            const t0 = performance.now();
            const dur = reduced ? 1 : 1600;
            const step = (t: number) => {
              const k = Math.min(1, (t - t0) / dur);
              const eased = 1 - (1 - k) ** 3;
              n.textContent = Math.round(target * eased).toLocaleString(isES ? "es-PE" : "en-US") + suffix;
              if (k < 1) requestAnimationFrame(step);
            };
            requestAnimationFrame(step);
          });

          if (e.target.querySelector(".impact-sp-fill")) {
            document.querySelectorAll<HTMLElement>(".impact-sp-fill").forEach((f, i) => {
              setTimeout(() => {
                f.style.width = `${f.dataset.w ?? 0}%`;
              }, i * 180);
            });
            const sp = spreadPctRef.current;
            if (sp) {
              const t0 = performance.now();
              const step = (t: number) => {
                const k = Math.min(1, (t - t0) / 1400);
                sp.textContent = `${(10.3 * (1 - (1 - k) ** 3)).toFixed(1)}%`;
                if (k < 1) requestAnimationFrame(step);
              };
              requestAnimationFrame(step);
            }
          }
          io.unobserve(e.target);
        });
      },
      { threshold: 0.2 }
    );
    els.forEach((x) => io.observe(x));
    return () => io.disconnect();
  }, [isES]);

  const pipLine = pypiChip
    ? `$ ${MARKET_STATS.pipInstallCmd} · ${pypiChip} ${isES ? "instalaciones" : "installs"}`
    : `$ ${MARKET_STATS.pipInstallCmd}`;

  return (
    <main className="bg-[var(--cm-canvas)]">
      <Navbar />

      {/* Hero */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide pt-10 pb-12 sm:pt-14 sm:pb-16">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-start">
            <div className="max-w-xl text-left">
              <div className="flex flex-wrap items-center gap-2 mb-4">
                <span className="stripe-tag-soft inline-flex items-center gap-2">
                  <span className="impact-live-dot" />
                  {isES
                    ? `COLLECTOR EN VIVO · REFRESH ${MARKET_STATS.pricesRefreshHours}H`
                    : `LIVE COLLECTOR · ${MARKET_STATS.pricesRefreshHours}H REFRESH`}
                </span>
                {linkageRounded != null ? (
                  <span
                    className="stripe-tag-soft"
                    title={isES ? "Snapshots ligados a golden records" : "Snapshots linked to golden records"}
                  >
                    {linkageRounded}% golden linkage
                  </span>
                ) : null}
              </div>

              <h1 className="hero-garamond-headline text-balance">
                {isES ? (
                  <>
                    El precio de la <span className="text-gradient-orange">góndola</span>, como infraestructura.
                  </>
                ) : (
                  <>
                    Shelf <span className="text-gradient-orange">prices</span> as infrastructure.
                  </>
                )}
              </h1>

              <p className="mt-4 text-base sm:text-lg leading-relaxed text-[var(--cm-on-surface-variant)]">
                {isES
                  ? `${MARKET_STATS.pricesVerifiedLabel} precios reales de ${MARKET_STATS.retailersVerified} retailers verificados en ${MARKET_STATS.countries} países, normalizados por kg/L. Una API, una CLI y ${MARKET_STATS.mcpTools} herramientas MCP para agentes de IA. Cero scraping.`
                  : `${MARKET_STATS.pricesVerifiedLabel} real prices from ${MARKET_STATS.retailersVerified} verified retailers across ${MARKET_STATS.countries} countries, normalized per kg/L. One API, one CLI, and ${MARKET_STATS.mcpTools} MCP tools for AI agents. Zero scraping.`}
              </p>

              <div className="mt-6 flex flex-wrap gap-3">
                <Link href={PRICING_BUILD_HASH} className="btn-mint">
                  {isES ? "Empezar con la API — prueba gratis" : "Start with the API — free trial"}
                </Link>
                <a href="#intel" className="btn-outline">
                  {isES ? "Ver Intelligence ↓" : "See Intelligence ↓"}
                </a>
              </div>

              <p className="mt-4 text-xs font-mono text-[var(--cm-on-surface-variant)]">{pipLine}</p>
            </div>

            <ImpactTerminal />
          </div>
        </div>
      </section>

      <PriceTicker />

      {/* Stats */}
      <section className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 impact-rv">
            <div className="card-cyber p-5 text-center">
              <div
                className="text-2xl sm:text-3xl font-display font-semibold text-[var(--cm-on-surface)]"
                data-count={parseInt(MARKET_STATS.pricesVerifiedLabel.replace(/[^0-9]/g, ""), 10)}
                data-suffix="+"
              >
                0
              </div>
              <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
                {isES ? "Precios verificados" : "Verified prices"}
              </div>
            </div>
            <div className="card-cyber p-5 text-center">
              <div
                className="text-2xl sm:text-3xl font-display font-semibold text-[var(--cm-on-surface)]"
                data-count={MARKET_STATS.retailersVerified}
              >
                0
              </div>
              <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
                {isES ? "Retailers activos" : "Active retailers"}
              </div>
            </div>
            <div className="card-cyber p-5 text-center">
              <div
                className="text-2xl sm:text-3xl font-display font-semibold text-[var(--cm-on-surface)]"
                data-count={MARKET_STATS.countries}
              >
                0
              </div>
              <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">{isES ? "Países" : "Countries"}</div>
            </div>
            <div className="card-cyber p-5 text-center">
              <div
                className="text-2xl sm:text-3xl font-display font-semibold text-[var(--cm-on-surface)]"
                data-count={MARKET_STATS.mcpTools}
              >
                0
              </div>
              <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">API tools</div>
            </div>
            {linkageRounded != null ? (
              <div className="card-cyber p-5 text-center">
                <div
                  className="text-2xl sm:text-3xl font-display font-semibold text-[var(--cm-mint)]"
                  data-count={linkageRounded}
                  data-suffix="%"
                >
                  0
                </div>
                <div className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
                  {isES ? "Linkage golden" : "Golden linkage"}
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </section>

      {/* Coverage */}
      <section id="coverage" className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <div className="flex items-baseline gap-3 mb-2 impact-rv">
            <span className="text-xs font-mono text-[var(--cm-mint)]">01</span>
            <h2 className="section-title !mb-0">{isES ? "Cobertura LatAm" : "LatAm coverage"}</h2>
          </div>
          <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-8">
            VTEX · SHOPIFY · MAGENTO · WOOCOMMERCE
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="card-cyber p-4 impact-rv">
              <LatAmCoverageMap />
            </div>
            <div className="space-y-3 impact-rv">
              {COVERAGE_ROWS.map((row) => (
                <div key={row.cc} className="card-cyber p-4 flex items-center justify-between gap-3">
                  <span className="text-xs font-mono text-[var(--cm-mint)] shrink-0">{row.cc}</span>
                  <span className="flex-1 text-sm text-[var(--cm-on-surface)]">
                    {row.stores}
                    <span className="block text-xs text-[var(--cm-on-surface-variant)] mt-0.5">
                      {isES ? row.noteEs : row.noteEn}
                    </span>
                  </span>
                  <span className="text-xs font-mono text-[var(--cm-mint)] shrink-0">
                    ● {isES ? "activo" : "active"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Spreads */}
      <section id="intel" className="landing-section" style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}>
        <div className="landing-container-wide py-12 sm:py-16">
          <div className="flex items-baseline gap-3 mb-8 impact-rv">
            <span className="text-xs font-mono text-[var(--cm-mint)]">02</span>
            <h2 className="section-title !mb-0">
              {isES ? "Spreads reales, no estimaciones" : "Real spreads, not estimates"}
            </h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 impact-rv">
            <div className="card-cyber p-6">
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-2">
                {isES ? "aceite vegetal 900ml — PE" : "vegetable oil 900ml — PE"}
              </h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed mb-1">
                {isES
                  ? "Mismo producto, precio normalizado por litro entre cadenas. El IPC oficial llega con 30 días de retraso; tu collector lo ve cada 4 horas."
                  : "Same product, price normalized per liter across chains. Official CPI arrives 30 days late; your collector sees it every 4 hours."}
              </p>
              <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mb-4">
                {isES ? "Datos ilustrativos · demo" : "Illustrative data · demo"}
              </p>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <b ref={spreadPctRef} className="block text-xl font-display font-semibold text-[var(--cm-on-surface)]">
                    0%
                  </b>
                  <span className="text-xs text-[var(--cm-on-surface-variant)]">
                    {isES ? "spread entre cadenas" : "cross-chain spread"}
                  </span>
                </div>
                <div>
                  <b className="block text-xl font-display font-semibold text-[var(--cm-on-surface)]">
                    {MARKET_STATS.indicatorsCount}
                  </b>
                  <span className="text-xs text-[var(--cm-on-surface-variant)]">
                    {isES ? "datos de mercado" : "market data"}
                  </span>
                </div>
                {linkageRounded != null ? (
                  <div>
                    <b
                      className="block text-xl font-display font-semibold text-[var(--cm-on-surface)]"
                      data-count={linkageRounded}
                      data-suffix="%"
                    >
                      0
                    </b>
                    <span className="text-xs text-[var(--cm-on-surface-variant)]">
                      {isES ? "linkage golden" : "golden linkage"}
                    </span>
                  </div>
                ) : null}
                <div>
                  <b className="block text-xl font-display font-semibold text-[var(--cm-on-surface)]">
                    {MARKET_STATS.pricesRefreshHours}h
                  </b>
                  <span className="text-xs text-[var(--cm-on-surface-variant)]">
                    {isES ? "frescura" : "freshness"}
                  </span>
                </div>
              </div>
            </div>

            <div className="card-cyber p-6 flex flex-col justify-center gap-4">
              {[
                { name: "Plaza Vea", price: "S/ 19.20", w: 100, best: false },
                { name: "Wong", price: "S/ 18.90", w: 98, best: false },
                { name: "Metro", price: "S/ 17.40", w: 91, best: true },
              ].map((row) => (
                <div key={row.name} className="flex items-center gap-3 text-sm">
                  <span className="w-16 shrink-0 text-[var(--cm-on-surface)]">{row.name}</span>
                  <div className="flex-1 h-2 rounded-full bg-[var(--cm-surface-high)] overflow-hidden">
                    <div
                      className="impact-sp-fill h-full rounded-full"
                      data-w={row.w}
                      style={{ width: 0, background: row.best ? "var(--cm-mint)" : "var(--cm-outline-variant)" }}
                    />
                  </div>
                  <span className="shrink-0 text-[var(--cm-on-surface)] font-mono text-xs">
                    <b>{row.price}</b> /L{row.best ? " ✓" : ""}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Plans */}
      <section id="planes" className="landing-section">
        <div className="landing-container-wide py-14 sm:py-20">
          <div className="flex items-baseline gap-3 mb-8 impact-rv">
            <span className="text-xs font-mono text-[var(--cm-mint)]">03</span>
            <h2 className="section-title !mb-0">{isES ? "Construido para escalar" : "Built to scale"}</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto impact-rv">
            <div className="card-cyber p-6 text-center flex flex-col items-center">
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-2">Build · Starter</h3>
              <div className="text-3xl font-semibold text-[var(--cm-on-surface)] mb-4">
                $9
                <small className="text-sm font-normal text-[var(--cm-on-surface-variant)]">
                  {" "}
                  / {isES ? `mes · ${TRIAL_DAYS} días gratis` : `mo · ${TRIAL_DAYS}-day trial`}
                </small>
              </div>
              <ul className="text-sm text-[var(--cm-on-surface-variant)] space-y-2 mb-6 text-left w-full max-w-[16rem]">
                <li>• 5,000 {isES ? "consultas / día" : "requests / day"}</li>
                <li>
                  • {MARKET_STATS.mcpTools} {isES ? "API tools" : "API tools"}
                </li>
                <li>• {isES ? "Basket · compare · export CSV" : "Basket · compare · CSV export"}</li>
                <li>• {isES ? "Historial 7 días" : "7-day history"}</li>
              </ul>
              <Link href={PRICING_BUILD_HASH} className="btn-outline w-full mt-auto">
                {isES ? `Prueba ${TRIAL_DAYS} días gratis →` : `Free ${TRIAL_DAYS}-day trial →`}
              </Link>
            </div>

            <div className="card-cyber p-6 text-center flex flex-col items-center">
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)] mb-2">Procure · Ops</h3>
              <div className="text-3xl font-semibold text-[var(--cm-on-surface)] mb-4">
                $79<small className="text-sm font-normal text-[var(--cm-on-surface-variant)]"> / {isES ? "mes" : "mo"}</small>
              </div>
              <ul className="text-sm text-[var(--cm-on-surface-variant)] space-y-2 mb-6 text-left w-full max-w-[16rem]">
                <li>• 200 procurement / {isES ? "mes" : "mo"}</li>
                <li>• {isES ? "Flujo run → approve → checkout" : "Run → approve → checkout flow"}</li>
                <li>• {isES ? "Aprobaciones + audit trail" : "Approvals + audit trail"}</li>
                <li>• {isES ? "API Build Pro incluida" : "Build Pro API included"}</li>
              </ul>
              <a
                href={PRICING_PROCURE_HASH}
                className="btn-outline w-full mt-auto"
                target="_blank"
                rel="noopener noreferrer"
              >
                {isES ? "Suscribirse →" : "Subscribe →"}
              </a>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
