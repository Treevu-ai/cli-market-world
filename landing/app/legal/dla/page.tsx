"use client";

import LegalPage from "@/components/LegalPage";
import { MARKET_STATS } from "@/lib/marketStats";

export default function DataLicenseAgreement() {
  return (
    <LegalPage
      titleES="Acuerdo de Licencia de Datos (ALD)"
      titleEN="Data License Agreement (DLA)"
      updatedES="6 de junio de 2026"
      updatedEN="June 6, 2026"
    >
      {(isES) =>
        isES ? (
          <>
            <p>
              <strong>Entidad:</strong> Sinapsis Innovadora S.A.C. (operador de CLI Market) ·{" "}
              <strong>Contacto:</strong>{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
            </p>
            <hr />

            <h2>1. Alcance</h2>
            <p>
              Este Acuerdo de Licencia de Datos (&quot;ALD&quot;) complementa los{" "}
              <a href="/legal/tos">Términos de Servicio</a> y rige el uso de datos de precios,
              mapeos de SKU, snapshots históricos, índices de retailers y derivados agregados
              (&quot;Datos&quot;) obtenidos a través del Servicio CLI Market.
            </p>
            <p>
              El software CLI Market (CLI, MCP, SDK) permanece bajo la Licencia MIT. Los Datos se
              licencian por separado según este ALD y su tier contratado.
            </p>

            <h2>2. Concesión de licencia</h2>
            <p>Según su plan activo, le otorgamos una licencia limitada, no exclusiva y no transferible para:</p>
            <ul>
              <li>Consultar Datos vía API, CLI o MCP dentro de los límites de su tier.</li>
              <li>Usar resultados en aplicaciones internas, dashboards y agentes autorizados.</li>
              <li>Exportar según lo permitido por su tier (p. ej. CSV en Starter y superiores).</li>
            </ul>

            <h2>3. Restricciones</h2>
            <p>Salvo acuerdo escrito, no puede:</p>
            <ul>
              <li>Revender, redistribuir o sublicenciar feeds de Datos en bruto o casi en bruto.</li>
              <li>Republicar índices completos de precios como producto independiente.</li>
              <li>Eludir límites de tasa, autenticación o controles de acceso.</li>
              <li>Usar los Datos para entrenar modelos de terceros sin autorización expresa.</li>
            </ul>

            <h2>4. Tiers y límites</h2>
            <p>
              Los límites de consulta, exportación y endpoints comerciales (Intelligence) dependen
              del plan publicado en{" "}
              <a href="https://cli-market.dev/#pricing">cli-market.dev/#pricing</a>:
            </p>
            <ul>
              <li>
                <strong>Free:</strong> 1.000 consultas/día · uso de API/MCP de lectura.
              </li>
              <li>
                <strong>Starter:</strong> 5.000 consultas/día · exportación CSV · suscripción PayPal.
              </li>
              <li>
                <strong>Pro:</strong> 10.000 consultas/día · checkout y claves de escritura.
              </li>
              <li>
                <strong>Builder / Intelligence:</strong> límites ampliados y endpoints comerciales
                bajo contrato.
              </li>
            </ul>
            <p>
              Cobertura actual: {MARKET_STATS.retailersVerified} retailers verificados en{" "}
              {MARKET_STATS.countries} países, con refresh cada {MARKET_STATS.pricesRefreshHours}{" "}
              horas.
            </p>

            <h2>5. Propiedad y atribución</h2>
            <p>
              CLI Market conserva todos los derechos sobre los Datos y su curación. Usted conserva la
              propiedad de su historial de compras, carritos y metadatos generados por su uso.
            </p>

            <h2>6. Exactitud y disponibilidad</h2>
            <p>
              Los Datos reflejan precios de góndola obtenidos de APIs públicas de catálogo. No
              garantizamos disponibilidad de stock ni exactitud en tiempo real de cada retailer.
              Consulte los Términos de Servicio para limitaciones de responsabilidad.
            </p>

            <h2>7. Duración y terminación</h2>
            <p>
              Este ALD entra en vigor al crear una cuenta o firmar un anexo comercial. Termina al
              cancelar su suscripción o por incumplimiento. Tras la terminación, debe cesar el uso de
              Datos almacenados salvo retención legal; las exportaciones post-suspensión están
              disponibles 30 días según los Términos.
            </p>

            <h2>8. Licencias empresariales</h2>
            <p>
              Para redistribución, white-label, snapshots PostgreSQL o feeds bulk, contacte a{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a> para un anexo ALD
              personalizado.
            </p>
          </>
        ) : (
          <>
            <p>
              <strong>Entity:</strong> Sinapsis Innovadora S.A.C. (CLI Market operator) ·{" "}
              <strong>Contact:</strong>{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
            </p>
            <hr />

            <h2>1. Scope</h2>
            <p>
              This Data License Agreement (&quot;DLA&quot;) supplements the{" "}
              <a href="/legal/tos">Terms of Service</a> and governs use of pricing data, SKU
              mappings, historical snapshots, retailer indexes, and aggregated derivatives
              (&quot;Data&quot;) obtained through the CLI Market Service.
            </p>
            <p>
              CLI Market software (CLI, MCP, SDK) remains under the MIT License. Data is licensed
              separately under this DLA and your contracted tier.
            </p>

            <h2>2. License grant</h2>
            <p>Based on your active plan, we grant a limited, non-exclusive, non-transferable license to:</p>
            <ul>
              <li>Query Data via API, CLI, or MCP within your tier limits.</li>
              <li>Use results in internal applications, dashboards, and authorized agents.</li>
              <li>Export as permitted by your tier (e.g. CSV on Starter and above).</li>
            </ul>

            <h2>3. Restrictions</h2>
            <p>Unless agreed in writing, you may not:</p>
            <ul>
              <li>Resell, redistribute, or sublicense raw or near-raw Data feeds.</li>
              <li>Republish complete price indexes as a standalone product.</li>
              <li>Circumvent rate limits, authentication, or access controls.</li>
              <li>Use Data to train third-party models without express authorization.</li>
            </ul>

            <h2>4. Tiers and limits</h2>
            <p>
              Query, export, and commercial endpoint (Intelligence) limits depend on the plan
              published at{" "}
              <a href="https://cli-market.dev/#pricing">cli-market.dev/#pricing</a>:
            </p>
            <ul>
              <li>
                <strong>Free:</strong> 1,000 requests/day · read API/MCP usage.
              </li>
              <li>
                <strong>Starter:</strong> 5,000 requests/day · CSV export · PayPal subscription.
              </li>
              <li>
                <strong>Pro:</strong> 10,000 requests/day · checkout and write API keys.
              </li>
              <li>
                <strong>Builder / Intelligence:</strong> expanded limits and commercial endpoints
                under contract.
              </li>
            </ul>
            <p>
              Current coverage: {MARKET_STATS.retailersVerified} verified retailers across{" "}
              {MARKET_STATS.countries} countries, refreshed every {MARKET_STATS.pricesRefreshHours}{" "}
              hours.
            </p>

            <h2>5. Ownership and attribution</h2>
            <p>
              CLI Market retains all rights to the Data and its curation. You retain ownership of
              your purchase history, carts, and metadata generated by your use.
            </p>

            <h2>6. Accuracy and availability</h2>
            <p>
              Data reflects shelf prices from public catalog APIs. We do not guarantee stock
              availability or real-time accuracy for every retailer. See the Terms of Service for
              liability limitations.
            </p>

            <h2>7. Term and termination</h2>
            <p>
              This DLA takes effect when you create an account or sign a commercial addendum. It
              ends when you cancel your subscription or upon breach. After termination, you must
              cease use of stored Data except for legal retention; post-suspension exports are
              available for 30 days per the Terms.
            </p>

            <h2>8. Enterprise licenses</h2>
            <p>
              For redistribution, white-label, PostgreSQL snapshots, or bulk feeds, contact{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a> for a custom DLA
              addendum.
            </p>
          </>
        )
      }
    </LegalPage>
  );
}