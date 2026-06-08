"use client";
import LegalPage from "@/components/LegalPage";
import { MARKET_STATS } from "@/lib/marketStats";

export default function TermsOfService() {
  return (
    <LegalPage
      titleES="Términos de Servicio"
      titleEN="Terms of Service"
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

            <h2>1. Aceptación de los Términos</h2>
            <p>
              Al acceder o utilizar la API de CLI Market, las herramientas MCP, el cliente CLI o
              cualquier servicio de datos relacionado (colectivamente, el "Servicio"), aceptas
              quedar vinculado por estos Términos de Servicio ("Términos"). Si no estás de
              acuerdo, no utilices el Servicio.
            </p>

            <h2>2. Descripción del Servicio</h2>
            <p>
              CLI Market proporciona una interfaz programable para búsqueda de productos,
              comparación de precios y ejecución de compras en {MARKET_STATS.retailersDefined}{" "}
              retailers ({MARKET_STATS.retailersVerified} verificados activos) en{" "}
              {MARKET_STATS.countries} países. El Servicio se entrega mediante el paquete PyPI (
              <code>{MARKET_STATS.pipInstallCmd}</code>), servidor MCP ({MARKET_STATS.mcpTools}{" "}
              herramientas), una API REST y snapshots de datos (bases de datos PostgreSQL de
              historial de precios y mapeos de SKU — licenciados por separado bajo acuerdo
              comercial de datos, previa solicitud a{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>).
            </p>

            <h2>3. Registro de Cuenta</h2>
            <p>
              Debes registrar una cuenta para usar el Servicio más allá del acceso público con
              límite de tasa. Eres responsable de mantener la confidencialidad de tus claves
              API y credenciales, y debes proporcionar información de registro precisa y
              completa.
            </p>

            <h2>4. Uso Aceptable</h2>
            <p>Aceptas no:</p>
            <ul>
              <li>Usar el Servicio para fines ilegales o en violación de los términos de servicio de los retailers.</li>
              <li>Revender, redistribuir o sublicenciar feeds de datos sin un Acuerdo de Licencia de Datos.</li>
              <li>Intentar eludir límites de tasa, autenticación o controles de acceso.</li>
              <li>Usar el Servicio para construir un producto competidor sustancialmente similar.</li>
              <li>Extraer datos sistemáticamente más allá de tu nivel de acceso autorizado.</li>
              <li>Usar el Servicio para compras automatizadas que violen los términos de los retailers, incluida la acumulación de inventario, manipulación de precios o transacciones fraudulentas.</li>
            </ul>

            <h2>5. Licencia de Datos</h2>
            <p>
              El software de CLI Market está licenciado bajo la Licencia MIT. Los datos de
              precios, mapeos de SKU, snapshots históricos e índices de retailers ("Datos") se
              licencian por separado bajo el{" "}
              <a href="/legal/dla">Acuerdo de Licencia de Datos ("ALD")</a>. Conserva la
              propiedad de su historial de compras y datos de carrito.
            </p>

            <h2>6. Tarifas y Pago</h2>
            <p>
              Los planes actuales se publican en{" "}
              <a href="https://cli-market.dev/#pricing">cli-market.dev/#pricing</a>. Las tarifas
              se cobran mensual o anualmente según lo seleccionado al registrarse. CLI Market se
              reserva el derecho de modificar los precios con 30 días de aviso. El incumplimiento
              de pago puede resultar en la suspensión del Servicio; las exportaciones de datos
              están disponibles durante 30 días post-suspensión.
            </p>

            <h3>6.1 Pagos, suscripciones y facturación</h3>
            <ul>
              <li>
                Los pagos del plan Pro (USD 39/mes u opción anual publicada en la landing), de
                servicios SaaS de Sinapsis Innovadora S.A.C. y el checkout de productos retail
                utilizan los mismos canales: PayPal, Mercado Pago, Yape y Plin, según
                disponibilidad regional y tier activo.
              </li>
              <li>
                La activación del tier Pro ocurre automáticamente tras la confirmación del pago.
                Puede verificar con <code>market whoami</code>.
              </li>
              <li>
                Puede cancelar la renovación en cualquier momento desde el canal de pago utilizado
                (p. ej. cuenta PayPal para suscripciones recurrentes) o contactando a{" "}
                <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>. La cancelación
                detiene cargos futuros; no reembolsa periodos ya facturados salvo lo exigido por
                ley o la política del procesador de pagos.
              </li>
              <li>
                Facturación de suscripciones y servicios SaaS en dólares estadounidenses (USD).
                Emisor: Sinapsis Innovadora S.A.C., RUC 20613045563 — solicite comprobante por
                correo a{" "}
                <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a> tras el pago.
              </li>
            </ul>

            <h2>7. Propiedad Intelectual</h2>
            <p>
              CLI Market y Sinapsis Innovadora S.A.C. conservan todos los derechos sobre el
              Servicio, incluidos software, esquemas de datos, lógica de agregación y marca. La
              Licencia MIT rige únicamente los componentes de software de código abierto — no se
              extiende a los Datos propietarios. "CLI Market" y el logotipo de CLI Market son
              marcas registradas de Sinapsis Innovadora S.A.C.
            </p>

            <h2>8. Retailers de Terceros</h2>
            <p>
              CLI Market se conecta a APIs de retailers de terceros (VTEX, Shopify, Magento).
              CLI Market no es responsable de la disponibilidad de productos o precisión de
              precios reportados por los retailers, transacciones fallidas por errores del lado
              del retailer, ni cambios en estructuras de API. Los usuarios son responsables del
              cumplimiento de los términos de los retailers al realizar pedidos.
            </p>

            <h2>9. Limitación de Responsabilidad</h2>
            <p>
              El Servicio se proporciona "tal cual" sin garantía de ningún tipo. En la máxima
              medida permitida por la ley, la responsabilidad de CLI Market por cualquier
              reclamación se limita a las tarifas pagadas por ti en los 12 meses anteriores a la
              reclamación. CLI Market no es responsable de pérdidas comerciales, decisiones de
              inventario ni resultados empresariales basados en datos de precios, ni por retrasos
              o imprecisiones en los ciclos de actualización de datos.
            </p>

            <h2>10. Terminación</h2>
            <p>
              Cualquiera de las partes puede terminar con 30 días de aviso por escrito. CLI
              Market puede suspender o terminar de inmediato por violación de la Política de Uso
              Aceptable, falta de pago o requisito legal. Al terminar, puedes exportar tus datos
              durante 30 días, después de lo cual se eliminan permanentemente.
            </p>

            <h2>11. Cambios en los Términos</h2>
            <p>
              CLI Market puede actualizar estos Términos con 30 días de aviso por correo
              electrónico y el panel del Servicio. El uso continuado después de la fecha
              efectiva constituye aceptación.
            </p>

            <h2>12. Ley Aplicable</h2>
            <p>
              Estos Términos se rigen por las leyes del Perú, sin tener en cuenta los principios
              de conflicto de leyes. Cualquier disputa se resolverá en los tribunales de Lima,
              Perú.
            </p>

            <hr />
            <p>
              <strong>Sinapsis Innovadora S.A.C.</strong> · RUC 20613045563 · Lima, Perú ·{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
            </p>
          </>
        ) : (
          <>
            <p>
              <strong>Entity:</strong> Sinapsis Innovadora S.A.C. (operator of CLI Market) ·{" "}
              <strong>Contact:</strong>{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
            </p>
            <hr />

            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing or using the CLI Market API, MCP tools, CLI client, or any related
              data services (collectively, the "Service"), you agree to be bound by these Terms
              of Service ("Terms"). If you do not agree, do not use the Service.
            </p>

            <h2>2. Description of Service</h2>
            <p>
              CLI Market provides a programmable interface for product search, price comparison,
              and purchase execution across {MARKET_STATS.retailersDefined} retailers (
              {MARKET_STATS.retailersVerified} verified active) in {MARKET_STATS.countries}{" "}
              countries. The Service is delivered via PyPI package (
              <code>{MARKET_STATS.pipInstallCmd}</code>), MCP server ({MARKET_STATS.mcpTools} tools), a
              REST API, and data snapshots (PostgreSQL databases of pricing history and SKU
              mappings — licensed separately under a commercial data agreement upon request at{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>).
            </p>

            <h2>3. Account Registration</h2>
            <p>
              You must register an account to use the Service beyond rate-limited public access.
              You are responsible for maintaining the confidentiality of your API keys and
              account credentials, and must provide accurate and complete registration
              information.
            </p>

            <h2>4. Acceptable Use</h2>
            <p>You agree not to:</p>
            <ul>
              <li>Use the Service for any unlawful purpose or in violation of applicable retailer terms of service.</li>
              <li>Resell, redistribute, or sublicense raw data feeds without a Data License Agreement.</li>
              <li>Attempt to circumvent rate limits, authentication, or access controls.</li>
              <li>Use the Service to build a substantially similar competing product.</li>
              <li>Scrape or systematically extract data beyond your authorized access tier.</li>
              <li>Use the Service for automated purchasing that violates retailer terms, including inventory hoarding, price manipulation, or fraudulent transactions.</li>
            </ul>

            <h2>5. Data License</h2>
            <p>
              The CLI Market software is licensed under the MIT License. Pricing data, SKU
              mappings, historical snapshots, and retailer indexes ("Data") are licensed
              separately under the{" "}
              <a href="/legal/dla">Data License Agreement ("DLA")</a>. You retain ownership of your
              purchase history and cart data.
            </p>

            <h2>6. Fees and Payment</h2>
            <p>
              Current pricing tiers are published at{" "}
              <a href="https://cli-market.dev/#pricing">cli-market.dev/#pricing</a>. Fees are
              charged monthly or annually as selected at registration. CLI Market reserves the
              right to modify pricing with 30 days notice. Failure to pay may result in
              suspension; data exports are available for 30 days post-suspension.
            </p>

            <h3>6.1 Payments, subscriptions, and invoicing</h3>
            <ul>
              <li>
                Payments for the Pro plan (USD 39/mo or published annual option), Sinapsis
                Innovadora S.A.C. SaaS services, and retail product checkout use the same
                channels: PayPal, Mercado Pago, Yape, and Plin, depending on region and active
                tier.
              </li>
              <li>
                Pro tier activates automatically after payment confirmation. Verify with{" "}
                <code>market whoami</code>.
              </li>
              <li>
                You may cancel renewal anytime from the payment channel used (e.g. PayPal account
                for recurring subscriptions) or by emailing{" "}
                <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>. Cancellation stops
                future charges; it does not refund already-billed periods except as required by
                law or the payment processor&apos;s policy.
              </li>
              <li>
                Subscription and SaaS services are invoiced in US dollars (USD). Issuer:
                Sinapsis Innovadora S.A.C., tax ID 20613045563 — request receipts by email at{" "}
                <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a> after payment.
              </li>
            </ul>

            <h2>7. Intellectual Property</h2>
            <p>
              CLI Market and Sinapsis Innovadora S.A.C. retain all rights in the Service,
              including software, data schemas, aggregation logic, and branding. The MIT License
              governs the open-source software components only — it does not extend to the
              proprietary Data. "CLI Market" and the CLI Market logo are trademarks of Sinapsis
              Innovadora S.A.C.
            </p>

            <h2>8. Third-Party Retailers</h2>
            <p>
              CLI Market connects to third-party retailer APIs (VTEX, Shopify, Magento). CLI
              Market is not responsible for product availability or pricing accuracy as reported
              by retailers, failed transactions due to retailer-side errors, or changes to
              retailer API structures. Users are responsible for compliance with retailer terms
              when placing orders.
            </p>

            <h2>9. Limitation of Liability</h2>
            <p>
              The Service is provided "as is" without warranty of any kind. To the maximum
              extent permitted by law, CLI Market's liability for any claim is limited to the
              fees paid by you in the 12 months preceding the claim. CLI Market is not liable
              for trading losses, inventory decisions, or business outcomes based on pricing
              data, nor for delays or inaccuracies in data refresh cycles.
            </p>

            <h2>10. Termination</h2>
            <p>
              Either party may terminate with 30 days written notice. CLI Market may suspend or
              terminate immediately for violation of the Acceptable Use Policy, non-payment, or
              legal/regulatory requirement. Upon termination, you may export your data for 30
              days, after which it is permanently deleted.
            </p>

            <h2>11. Changes to Terms</h2>
            <p>
              CLI Market may update these Terms with 30 days notice via email and the Service
              dashboard. Continued use after the effective date constitutes acceptance.
            </p>

            <h2>12. Governing Law</h2>
            <p>
              These Terms are governed by the laws of Peru, without regard to conflict of law
              principles. Any disputes shall be resolved in the courts of Lima, Peru.
            </p>

            <hr />
            <p>
              <strong>Sinapsis Innovadora S.A.C.</strong> · RUC 20613045563 · Lima, Perú ·{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
            </p>
          </>
        )
      }
    </LegalPage>
  );
}
