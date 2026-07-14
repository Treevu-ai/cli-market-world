"use client";

import LegalPage from "@/components/LegalPage";
import { MARKET_STATS } from "@/lib/marketStats";

function PilotTable({ isES }: { isES: boolean }) {
  const headers = isES
    ? ["", "Pilot S", "Pilot M", "Pilot L"]
    : ["", "Pilot S", "Pilot M", "Pilot L"];
  const rows = isES
    ? [
        ["Precio", "USD 300/mes", "USD 400/mes", "USD 500/mes"],
        ["Alcance", "1 país, 1–2 líneas", "1–2 países, 3 líneas", "Multi-país LATAM"],
        ["Histórico", "30 días", "60 días", "90 días"],
        ["Entrega", "Export semanal", "API + export", "API + SLA 48 h"],
      ]
    : [
        ["Price", "USD 300/mo", "USD 400/mo", "USD 500/mo"],
        ["Scope", "1 country, 1–2 lines", "1–2 countries, 3 lines", "Multi-country LATAM"],
        ["History", "30 days", "60 days", "90 days"],
        ["Delivery", "Weekly export", "API + export", "API + 48 h SLA"],
      ];

  return (
    <div className="overflow-x-auto my-6">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr>
            {headers.map((h) => (
              <th
                key={h || "row"}
                className="border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] px-3 py-2 text-left font-semibold text-[var(--cm-on-surface)]"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row[0]}>
              {row.map((cell, i) => (
                <td
                  key={`${row[0]}-${i}`}
                  className="border border-[var(--cm-outline-variant)] px-3 py-2 text-[var(--cm-on-surface-variant)] align-top"
                >
                  {i === 0 ? <strong className="text-[var(--cm-on-surface)]">{cell}</strong> : cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function IntelligencePilotOnePagerPage() {
  const statsLine = `${MARKET_STATS.pricesVerifiedLabel} verified prices · ${MARKET_STATS.retailersDefined} catalog · ${MARKET_STATS.retailersVerified} verified active · ${MARKET_STATS.countries} countries · ${MARKET_STATS.pricesRefreshHours}h refresh`;
  const statsLineEs = `${MARKET_STATS.pricesVerifiedLabel} precios verificados · ${MARKET_STATS.retailersDefined} catálogo · ${MARKET_STATS.retailersVerified} verificados activos · ${MARKET_STATS.countries} países · refresh ${MARKET_STATS.pricesRefreshHours} h`;

  return (
    <LegalPage
      titleES="CLI Market Intelligence — Piloto"
      titleEN="CLI Market Intelligence — Pilot"
      updatedES="14 de julio de 2026"
      updatedEN="July 14, 2026"
    >
      {(isES) =>
        isES ? (
          <>
            <p className="text-base text-[var(--cm-on-surface)] font-medium">
              Precios de góndola en LATAM · calidad verificable · piloto desde USD 300/mes
            </p>
            <hr />

            <h2>Para quién</h2>
            <p>
              Equipos de <strong>pricing</strong>, <strong>trade marketing</strong>,{" "}
              <strong>inteligencia comercial</strong>, <strong>fintech (datos para modelos)</strong> y{" "}
              <strong>consultoras</strong> que necesitan spreads, inflación y canasta con datos frescos — no
              checkout autónomo ni listado de tienda.
            </p>

            <h2>Qué obtiene</h2>
            <ul>
              <li>Spreads entre retailers (mismo producto comparable)</li>
              <li>Inflación por línea y país (7 / 30 / 90 días según piloto)</li>
              <li>Canasta básica con reglas de comparabilidad explícitas</li>
              <li>
                Capa <strong>clean / flagged / citable</strong> — sin publicar outliers sin filtrar
              </li>
              <li>{statsLineEs}</li>
              <li>
                Piloto FMCG WooCommerce: <strong>Nuna Orgánica</strong> (620+ SKUs orgánicos PE, Store API)
              </li>
            </ul>

            <h2>Por qué ahora</h2>
            <p>
              Fuentes oficiales llegan con semanas de retraso. Bureaus y paneles legacy suelen costar{" "}
              <strong>USD 500+/mes</strong> (o contratos anuales altos) con menos cobertura LATAM y sin capa de
              calidad documentada.
            </p>

            <h2>Piloto 30–90 días</h2>
            <PilotTable isES />
            <p>Onboarding en <strong>48 h</strong>. Propuesta personalizada según categorías y volumen.</p>

            <h2>Qué NO es</h2>
            <ul>
              <li>
                <strong>Build (Starter $9 · Pro $49/mes):</strong> API/MCP para developers — no es Intelligence ni
                Procure
              </li>
              <li>
                <strong>Procure Copilot ($29–79/mes):</strong> equipos de compras — infra API incluida en Pro+
              </li>
              <li>
                <strong>Retailer listing:</strong> gratis — aparecer en búsquedas de agentes
              </li>
              <li>
                <strong>Checkout autónomo:</strong> roadmap, no producto comercial este trimestre
              </li>
            </ul>

            <h2>Siguiente paso</h2>
            <p>
              <a href="/contact?topic=intelligence#contact-intelligence">Solicitar piloto →</a>
              <br />
              <a href="mailto:hello@cli-market.dev?subject=Intelligence%20Pilot">hello@cli-market.dev</a> · asunto{" "}
              <strong>Intelligence Pilot</strong>
            </p>
            <p>Indique país, categorías y equipo. Respondemos en 48 h.</p>
            <p className="text-xs text-[var(--cm-on-surface-variant)]/70">
              <a href="/intelligence-pilot-es.md">Versión markdown</a> · Data sujeta a Data License Agreement
            </p>
          </>
        ) : (
          <>
            <p className="text-base text-[var(--cm-on-surface)] font-medium">
              LATAM shelf prices · verifiable quality · pilot from USD 300/mo
            </p>
            <hr />

            <h2>Who it&apos;s for</h2>
            <p>
              <strong>Pricing</strong>, <strong>trade marketing</strong>, <strong>commercial intelligence</strong>,{" "}
              <strong>fintech data teams</strong>, and <strong>consultancies</strong> that need spreads, inflation,
              and basket signals from fresh shelf data — not autonomous checkout or store listing.
            </p>

            <h2>What you get</h2>
            <ul>
              <li>Cross-retailer spreads (comparable products)</li>
              <li>Line and country inflation (7 / 30 / 90 days per pilot tier)</li>
              <li>Basic basket with explicit comparability rules</li>
              <li>
                <strong>Clean / flagged / citable</strong> layer — no unfiltered outliers in client-facing outputs
              </li>
              <li>{statsLine}</li>
              <li>
                FMCG WooCommerce pilot: <strong>Nuna Orgánica</strong> (620+ organic SKUs PE, Store API)
              </li>
            </ul>

            <h2>Why now</h2>
            <p>
              Official sources lag by weeks. Legacy bureaus often cost <strong>USD 500+/mo</strong> with less LATAM
              coverage and no documented quality layer.
            </p>

            <h2>30–90 day pilot</h2>
            <PilotTable isES={false} />
            <p>
              Onboarding in <strong>48 hours</strong>. Custom proposal by category and volume.
            </p>

            <h2>What it is not</h2>
            <ul>
              <li>
                <strong>Build (Starter $9 · Pro $49/mo):</strong> API/MCP for developers — not Intelligence or Procure
              </li>
              <li>
                <strong>Procure Copilot ($29–79/mo):</strong> procurement teams — Build API included on Pro+
              </li>
              <li>
                <strong>Retailer listing:</strong> free — visibility in agent search
              </li>
              <li>
                <strong>Autonomous checkout:</strong> roadmap, not a commercial product this quarter
              </li>
            </ul>

            <h2>Next step</h2>
            <p>
              <a href="/contact?topic=intelligence#contact-intelligence">Request pilot →</a>
              <br />
              <a href="mailto:hello@cli-market.dev?subject=Intelligence%20Pilot">hello@cli-market.dev</a> · subject{" "}
              <strong>Intelligence Pilot</strong>
            </p>
            <p>Share country, categories, and team. We reply within 48 hours.</p>
            <p className="text-xs text-[var(--cm-on-surface-variant)]/70">
              <a href="/intelligence-pilot-es.md">Markdown version</a> · Data subject to Data License Agreement
            </p>
          </>
        )
      }
    </LegalPage>
  );
}
