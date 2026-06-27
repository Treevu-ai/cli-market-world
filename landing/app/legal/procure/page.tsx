"use client";

import LegalPage from "@/components/LegalPage";

export default function ProcureTermsPage() {
  return (
    <LegalPage
      titleES="Procure Copilot — Términos de uso"
      titleEN="Procure Copilot — Terms of Use"
      updatedES="27 de junio de 2026"
      updatedEN="June 27, 2026"
    >
      {(isES) =>
        isES ? (
          <>
            <p>
              <strong>Entidad:</strong> Sinapsis Innovadora S.A.C. (operador de CLI Market y Procure Copilot) ·{" "}
              <strong>Contacto:</strong> <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
            </p>
            <hr />

            <h2>1. Naturaleza del servicio</h2>
            <p>
              Procure Copilot es software de inteligencia de precios, señales comerciales y gobernanza de compras B2B
              en LatAm. No somos retailer, importador, transportista ni asegurador de producto.
            </p>

            <h2>2. Identidad de producto</h2>
            <p>
              Las comparaciones usan emparejamiento automatizado (nombre, marca e índice semántico). No garantizamos
              que dos listados sean el mismo SKU, configuración ni cobertura de garantía regional.
            </p>

            <h2>3. Precios y frescura</h2>
            <p>
              Los precios provienen de fuentes indexadas (~4h) y pueden estar desactualizados o ser parciales. La
              validación en checkout aplica solo al momento del pago orquestado por Procure Copilot.
            </p>

            <h2>4. Stock y delivery</h2>
            <p>
              La información de stock y entrega es referencial al cotizar. Revalidamos stock antes del checkout cuando
              hay dato disponible, pero no garantizamos inventario ni plazos al pagar.
            </p>

            <h2>5. Logística, aranceles e impuestos</h2>
            <p>
              Señales cross-border muestran precio de anaquel sin envío, aduanas, IGV ni landed cost.
            </p>

            <h2>6. Garantía y posventa</h2>
            <p>
              No verificamos garantía, distribuidor autorizado ni políticas de devolución. Fulfillment y soporte son
              responsabilidad del retailer o fabricante.
            </p>

            <h2>7. Checkout y fulfillment</h2>
            <p>
              El pago procesado vía Procure Copilot no implica que nosotros enviemos el producto. La entrega depende
              del retailer según sus términos.
            </p>

            <h2>8. Comprobantes fiscales (Perú)</h2>
            <p>
              Salvo indicación expresa, los comprobantes pueden ser informativos y no válidos como comprobante
              electrónico SUNAT.
            </p>

            <h2>9. Señales e inteligencia</h2>
            <p>
              Forecasts, alertas y reportes de ahorro son informativos. No garantizan precios futuros ni ahorro real.
            </p>

            <h2>10. Uso por agentes de IA</h2>
            <p>
              Si un agente ejecuta búsqueda o checkout, el titular de la cuenta es responsable de verificar specs,
              garantía y condiciones antes de confirmar.
            </p>

            <h2>11. Suscripción, cancelación y reembolsos</h2>
            <p>
              Los planes Starter, Pro, Builder y Enterprise tienen límites distintos. La cancelación surte efecto al
              final del período pagado. Salvo obligación legal imperativa, no hay reembolso proporcional por uso
              parcial del período. Solicitudes: <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>.
            </p>

            <h2>12. Limitaciones del producto</h2>
            <p>
              Documento complementario en{" "}
              <a href="https://procurecopilot.com#limitations">procurecopilot.com#limitations</a>.
            </p>
          </>
        ) : (
          <>
            <p>
              <strong>Entity:</strong> Sinapsis Innovadora S.A.C. · <strong>Contact:</strong>{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
            </p>
            <hr />

            <h2>1. Nature of the service</h2>
            <p>
              Procure Copilot is B2B price intelligence and purchase governance software for LatAm. We are not a
              retailer, importer, carrier, or product insurer.
            </p>

            <h2>2. Product identity</h2>
            <p>
              Comparisons use automated matching. We do not guarantee same SKU, configuration, or regional warranty
              coverage.
            </p>

            <h2>3. Prices and freshness</h2>
            <p>
              Prices come from indexed sources (~4h) and may be stale or partial. Checkout validation applies only at
              payment time through Procure Copilot.
            </p>

            <h2>4. Stock and delivery</h2>
            <p>
              Stock and delivery data are referential at quote time. We re-check stock before checkout when data exists,
              but do not guarantee inventory or lead times at payment.
            </p>

            <h2>5. Logistics, duties, and taxes</h2>
            <p>Cross-border signals show shelf price only — excluding shipping, duties, VAT, and landed cost.</p>

            <h2>6. Warranty and post-sale</h2>
            <p>
              We do not verify warranty, authorized distributor status, or return policies. Fulfillment is the
              retailer&apos;s responsibility.
            </p>

            <h2>7. Checkout and fulfillment</h2>
            <p>Payment through Procure Copilot does not mean we ship the product.</p>

            <h2>8. Tax receipts (Peru)</h2>
            <p>Unless stated otherwise, receipts may be informational and not valid SUNAT e-invoices.</p>

            <h2>9. Intelligence signals</h2>
            <p>Forecasts and savings reports are informational only.</p>

            <h2>10. AI agent use</h2>
            <p>The account holder is responsible for verifying specs and terms before confirming any transaction.</p>

            <h2>11. Subscription, cancellation, and refunds</h2>
            <p>
              Cancellation takes effect at period end. No prorated refunds unless required by law. Contact{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>.
            </p>

            <h2>12. Product limitations</h2>
            <p>
              See also <a href="https://procurecopilot.com#limitations">procurecopilot.com#limitations</a>.
            </p>
          </>
        )
      }
    </LegalPage>
  );
}
