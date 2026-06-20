"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import LatAmCoverageMap from "@/components/LatAmCoverageMap";
import ImpactTerminal from "@/components/ImpactTerminal";
import PriceTicker from "@/components/PriceTicker";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLang } from "@/lib/LanguageContext";
import { useLiveStats } from "@/hooks/useLiveStats";
import { PRICING_BUILD_HASH, PRICING_PROCURE_HASH } from "@/lib/siteNav";

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
    <div className="impact-page brand-mode-terminal">
      <nav className="impact-nav">
        <Link href="/" className="impact-brand">
          CLI_MARKET<span className="impact-blink">▮</span>
        </Link>
        <div className="impact-nav-r">
          <a href="#coverage">{isES ? "Cobertura" : "Coverage"}</a>
          <a href="#intel">Intelligence</a>
          <a href="#planes">{isES ? "Planes" : "Plans"}</a>
          <Link href={PRICING_BUILD_HASH} className="impact-nav-cta">
            {isES ? "Empezar gratis →" : "Start free →"}
          </Link>
        </div>
      </nav>

      <div className="impact-hero">
        <div>
          <div className="impact-hero-badges">
            <div className="impact-eyebrow">
              <span className="impact-live-dot" />
              {isES
                ? `COLLECTOR EN VIVO · REFRESH ${MARKET_STATS.pricesRefreshHours}H`
                : `LIVE COLLECTOR · ${MARKET_STATS.pricesRefreshHours}H REFRESH`}
            </div>
            {linkageRounded != null ? (
              <div
                className="impact-linkage-chip"
                title={isES ? "Snapshots ligados a golden records" : "Snapshots linked to golden records"}
              >
                <span className="impact-linkage-chip-n">{linkageRounded}%</span>
                <span>{isES ? "golden linkage" : "golden linkage"}</span>
              </div>
            ) : null}
          </div>
          <h1>
            {isES ? (
              <>
                El precio de la <em>góndola</em>, como infraestructura.
              </>
            ) : (
              <>
                Shelf <em>prices</em> as infrastructure.
              </>
            )}
          </h1>
          <p className="impact-lead">
            {isES
              ? `${MARKET_STATS.pricesVerifiedLabel} precios reales de ${MARKET_STATS.retailersVerified} retailers verificados en ${MARKET_STATS.countries} países, normalizados por kg/L. Una API, una CLI y ${MARKET_STATS.mcpTools} herramientas MCP para agentes de IA. Cero scraping.`
              : `${MARKET_STATS.pricesVerifiedLabel} real prices from ${MARKET_STATS.retailersVerified} verified retailers across ${MARKET_STATS.countries} countries, normalized per kg/L. One API, one CLI, and ${MARKET_STATS.mcpTools} MCP tools for AI agents. Zero scraping.`}
          </p>
          <div className="impact-hero-ctas">
            <Link href={PRICING_BUILD_HASH} className="impact-btn impact-btn-action">
              {isES ? "Empezar con la API — gratis" : "Start with the API — free"}
            </Link>
            <a href="#intel" className="impact-btn impact-btn-ghost">
              {isES ? "Ver Intelligence ↓" : "See Intelligence ↓"}
            </a>
          </div>
          <p className="impact-pip">{pipLine}</p>
        </div>
        <ImpactTerminal />
      </div>

      <PriceTicker />

      <section className="impact-section">
        <div className="impact-stats impact-rv">
          <div className="impact-stat">
            <div className="impact-stat-n" data-count={parseInt(MARKET_STATS.pricesVerifiedLabel.replace(/[^0-9]/g, ""), 10)} data-suffix="+">
              0
            </div>
            <div className="impact-stat-l">{isES ? "Precios verificados" : "Verified prices"}</div>
          </div>
          <div className="impact-stat">
            <div className="impact-stat-n" data-count={MARKET_STATS.retailersVerified}>
              0
            </div>
            <div className="impact-stat-l">{isES ? "Retailers activos" : "Active retailers"}</div>
          </div>
          <div className="impact-stat">
            <div className="impact-stat-n" data-count={MARKET_STATS.countries}>
              0
            </div>
            <div className="impact-stat-l">{isES ? "Países" : "Countries"}</div>
          </div>
          <div className="impact-stat">
            <div className="impact-stat-n" data-count={MARKET_STATS.mcpTools}>
              0
            </div>
            <div className="impact-stat-l">{isES ? "API tools" : "API tools"}</div>
          </div>
          {linkageRounded != null ? (
            <div className="impact-stat impact-stat-linkage">
              <div className="impact-stat-n" data-count={linkageRounded} data-suffix="%">
                0
              </div>
              <div className="impact-stat-l">{isES ? "Linkage golden" : "Golden linkage"}</div>
            </div>
          ) : null}
        </div>
      </section>

      <section id="coverage" className="impact-section">
        <div className="impact-sec-head impact-rv">
          <span className="impact-idx">[01]</span>
          <h2>{isES ? "Cobertura LatAm" : "LatAm coverage"}</h2>
          <span className="impact-rule" />
          <span className="impact-idx">VTEX · SHOPIFY · MAGENTO · WOO</span>
        </div>
        <div className="impact-coverage">
          <div className="impact-map-wrap impact-rv">
            <LatAmCoverageMap />
          </div>
          <div className="impact-cov-list impact-rv">
            {COVERAGE_ROWS.map((row) => (
              <div key={row.cc} className="impact-cov-row">
                <span className="impact-cc">{row.cc}</span>
                <span className="impact-rt">
                  {row.stores}
                  <span>{isES ? row.noteEs : row.noteEn}</span>
                </span>
                <span className="impact-ct">● {isES ? "activo" : "active"}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="intel" className="impact-section">
        <div className="impact-sec-head impact-rv">
          <span className="impact-idx">[02]</span>
          <h2>{isES ? "Spreads reales, no estimaciones" : "Real spreads, not estimates"}</h2>
          <span className="impact-rule" />
        </div>
        <div className="impact-spread impact-rv">
          <div>
            <h3>{isES ? "aceite vegetal 900ml — PE" : "vegetable oil 900ml — PE"}</h3>
            <p>
              {isES
                ? "Mismo producto, precio normalizado por litro entre cadenas. El IPC oficial llega con 30 días de retraso; tu collector lo ve cada 4 horas."
                : "Same product, price normalized per liter across chains. Official CPI arrives 30 days late; your collector sees it every 4 hours."}
            </p>
            <p className="impact-demo-note">{isES ? "Datos ilustrativos · demo" : "Illustrative data · demo"}</p>
            <div className="impact-spread-meta">
              <div>
                <b ref={spreadPctRef}>0%</b>
                <span>{isES ? "spread entre cadenas" : "cross-chain spread"}</span>
              </div>
              <div>
                <b>{MARKET_STATS.indicatorsCount}</b>
                <span>{isES ? "datos de mercado" : "market data"}</span>
              </div>
              {linkageRounded != null ? (
                <div>
                  <b data-count={linkageRounded} data-suffix="%">
                    0
                  </b>
                  <span>{isES ? "linkage golden" : "golden linkage"}</span>
                </div>
              ) : null}
              <div>
                <b>{MARKET_STATS.pricesRefreshHours}h</b>
                <span>{isES ? "frescura" : "freshness"}</span>
              </div>
            </div>
          </div>
          <div className="impact-sp-rows" id="impactSpRows">
            <div className="impact-sp-row">
              <span>Plaza Vea</span>
              <div className="impact-sp-track">
                <div className="impact-sp-fill impact-sp-fill-a" data-w="100" />
              </div>
              <span className="impact-sp-price">
                <b>S/ 19.20</b> /L
              </span>
            </div>
            <div className="impact-sp-row">
              <span>Wong</span>
              <div className="impact-sp-track">
                <div className="impact-sp-fill impact-sp-fill-a" data-w="98" />
              </div>
              <span className="impact-sp-price">
                <b>S/ 18.90</b> /L
              </span>
            </div>
            <div className="impact-sp-row">
              <span>Metro</span>
              <div className="impact-sp-track">
                <div className="impact-sp-fill impact-sp-fill-b" data-w="91" />
              </div>
              <span className="impact-sp-price">
                <b>S/ 17.40</b> /L ✓
              </span>
            </div>
          </div>
        </div>
      </section>

      <section id="planes" className="impact-section">
        <div className="impact-sec-head impact-rv">
          <span className="impact-idx">[03]</span>
          <h2>{isES ? "Construido para escalar" : "Built to scale"}</h2>
          <span className="impact-rule" />
        </div>
        <div className="impact-plans">
          <div className="impact-plan impact-rv">
            <h3>Build · Free</h3>
            <div className="impact-pr">
              $0<small> / {isES ? "siempre" : "forever"}</small>
            </div>
            <ul>
              <li>1,000 {isES ? "consultas / día" : "queries / day"}</li>
              <li>
                {MARKET_STATS.mcpTools} {isES ? "API tools" : "API tools"}
              </li>
              <li>{isES ? "Compare multi-retailer" : "Multi-retailer compare"}</li>
              <li>{isES ? "Historial 7 días" : "7-day history"}</li>
            </ul>
            <Link href={PRICING_BUILD_HASH} className="impact-btn impact-btn-ghost impact-btn-block">
              {isES ? "Empezar gratis" : "Start free"}
            </Link>
          </div>
          <div className="impact-plan impact-rv">
            <h3>Procure · Ops</h3>
            <div className="impact-pr">
              $79<small> / {isES ? "mes" : "mo"}</small>
            </div>
            <ul>
              <li>200 procurement / {isES ? "mes" : "mo"}</li>
              <li>{isES ? "Flujo run → approve → checkout" : "Run → approve → checkout flow"}</li>
              <li>{isES ? "Aprobaciones + audit trail" : "Approvals + audit trail"}</li>
              <li>{isES ? "API Build Pro incluida" : "Build Pro API included"}</li>
            </ul>
            <Link href={PRICING_PROCURE_HASH} className="impact-btn impact-btn-ghost impact-btn-block">
              {isES ? "Suscribir →" : "Subscribe →"}
            </Link>
          </div>
        </div>
      </section>

      <footer className="impact-footer">
        <div>© 2026 CLI Market · Sinapsis Innovadora S.A.C. · Lima, Perú</div>
        <div>
          <a href={MARKET_STATS.pypiUrl} target="_blank" rel="noopener noreferrer">
            PyPI
          </a>
          {" · "}
          <Link href="/docs">Docs</Link>
          {" · "}
          <Link href="/tools">MCP Registry</Link>
          {" · "}
          <Link href="/stats">{isES ? "Métricas públicas" : "Public metrics"}</Link>
          {" · "}
          <Link href="/">{isES ? "Home" : "Home"}</Link>
        </div>
      </footer>
    </div>
  );
}