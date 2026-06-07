"use client";
import LegalPage from "@/components/LegalPage";

export default function PrivacyPolicy() {
  return (
    <LegalPage
      titleES="Política de Privacidad"
      titleEN="Privacy Policy"
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

            <h2>1. Qué Datos Recopilamos</h2>
            <p>Recopilamos únicamente lo necesario para operar el Servicio:</p>
            <ul>
              <li>
                <strong>Datos de cuenta:</strong> correo electrónico, nombre (opcional) y el plan
                o rol que seleccionas al registrarte o enviar un formulario de contacto.
              </li>
              <li>
                <strong>Datos de uso:</strong> conteos de solicitudes a la API, marcas de tiempo
                y el nivel de clave API asociado a cada solicitud. No registramos el contenido de
                las consultas más allá de lo necesario para la limitación de tasa y facturación.
              </li>
              <li>
                <strong>Datos de transacción:</strong> detalles del pedido y eventos de
                confirmación de pago de PayPal. No almacenamos números de tarjeta
                ni credenciales de pago completas.
              </li>
              <li>
                <strong>Datos técnicos:</strong> dirección IP (para limitación de tasa y
                prevención de abusos), agente de usuario y referrer solo para la sesión actual.
              </li>
            </ul>

            <h2>2. Cómo Usamos tus Datos</h2>
            <ul>
              <li>Para operar y mejorar el Servicio.</li>
              <li>Para responder a tus consultas y solicitudes de soporte.</li>
              <li>Para enviar correos transaccionales (confirmaciones de pedido, alertas de cuenta). No enviamos correos de marketing sin consentimiento explícito.</li>
              <li>Para detectar y prevenir abusos, fraude y accesos no autorizados.</li>
              <li>Para cumplir obligaciones legales.</li>
            </ul>
            <p>No vendemos, alquilamos ni compartimos tus datos personales con terceros con fines de marketing.</p>

            <h2>3. Almacenamiento y Seguridad</h2>
            <p>
              Los datos se almacenan en Railway (infraestructura en la nube). Usamos TLS en
              tránsito y bases de datos con control de acceso en reposo. Las claves API se
              hashean antes del almacenamiento. Conservamos los datos de contacto y cuenta
              mientras tu cuenta esté activa, más 30 días tras la baja para permitir la
              exportación de datos.
            </p>

            <h2>4. Servicios de Terceros</h2>
            <ul>
              <li>
                <strong>Railway:</strong> infraestructura de alojamiento y base de datos.
              </li>
              <li>
                <strong>PayPal:</strong> procesamiento de pagos. La{" "}
                <a href="https://www.paypal.com/webapps/mpp/ua/privacy-full" target="_blank" rel="noopener noreferrer">
                  Política de Privacidad de PayPal
                </a>{" "}
                aplica a los datos de pago.
              </li>
              <li>
                <strong>Cloudflare Pages:</strong> alojamiento de la landing estática. Cloudflare
                puede registrar metadatos de solicitudes según sus prácticas de infraestructura.
              </li>
              <li>
                <strong>Cloudflare Web Analytics:</strong> métricas agregadas de visitas (páginas
                vistas, referrer, país aproximado) sin cookies de terceros para publicidad.{" "}
                <a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener noreferrer">
                  Política de Cloudflare
                </a>
                .
              </li>
              <li>
                <strong>Plausible Analytics:</strong> analítica respetuosa con la privacidad (sin
                cookies de seguimiento cross-site, datos agregados).{" "}
                <a href="https://plausible.io/privacy-focused-web-analytics" target="_blank" rel="noopener noreferrer">
                  Política de Plausible
                </a>
                .
              </li>
              <li>
                <strong>Mercado Pago:</strong> procesamiento de pagos locales (Perú/LatAm) cuando
                utiliza checkout de productos en tier Pro.
              </li>
            </ul>
            <p>
              No integramos redes publicitarias ni píxeles de seguimiento social. La analítica de
              la landing se usa únicamente para medir tráfico agregado y mejorar el producto.
            </p>

            <h2>5. Cookies y almacenamiento local</h2>
            <p>
              La landing no utiliza cookies de publicidad. Cloudflare y Plausible pueden usar
              almacenamiento mínimo técnico según su documentación. La API usa un token de sesión
              almacenado en su configuración local del CLI (~/.cli-market/config.json), no en
              cookies del navegador.
            </p>

            <h2>6. Tus Derechos</h2>
            <p>Puedes en cualquier momento:</p>
            <ul>
              <li>Solicitar una copia de tus datos personales.</li>
              <li>Solicitar la corrección de datos inexactos.</li>
              <li>Solicitar la eliminación de tus datos (sujeto a requisitos legales de retención).</li>
              <li>Retirar el consentimiento para cualquier tratamiento basado en consentimiento.</li>
            </ul>
            <p>
              Para ejercer estos derechos, escríbenos a{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>. Respondemos en un
              plazo de 5 días hábiles.
            </p>

            <h2>7. Menores de Edad</h2>
            <p>
              El Servicio no está dirigido a menores de 16 años. No recopilamos datos de menores
              de forma consciente. Si crees que un menor nos ha proporcionado datos, contáctanos
              para su eliminación inmediata.
            </p>

            <h2>8. Cambios en esta Política</h2>
            <p>
              Notificaremos a los usuarios registrados por correo electrónico con al menos 14
              días de anticipación antes de que los cambios materiales entren en vigor. El uso
              continuado del Servicio después de la fecha efectiva constituye aceptación.
            </p>

            <h2>9. Ley Aplicable</h2>
            <p>
              Esta Política de Privacidad se rige por las leyes del Perú. Los usuarios en el
              Espacio Económico Europeo también pueden presentar una queja ante su autoridad
              local de protección de datos.
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

            <h2>1. What We Collect</h2>
            <p>We collect only what is necessary to operate the Service:</p>
            <ul>
              <li>
                <strong>Account data:</strong> email address, name (optional), and the plan or
                role you select when signing up or submitting a contact form.
              </li>
              <li>
                <strong>Usage data:</strong> API request counts, timestamps, and the API key tier
                associated with each request. We do not log query content beyond what is
                necessary for rate limiting and billing.
              </li>
              <li>
                <strong>Transaction data:</strong> order details and payment confirmation events
                (via PayPal). We do not store card numbers or full payment credentials.
              </li>
              <li>
                <strong>Technical data:</strong> IP address (for rate limiting and abuse
                prevention), user agent, and referrer for the current session only.
              </li>
            </ul>

            <h2>2. How We Use Your Data</h2>
            <ul>
              <li>To operate and improve the Service.</li>
              <li>To respond to your inquiries and support requests.</li>
              <li>To send transactional emails (order confirmations, account alerts). We do not send marketing emails without explicit opt-in.</li>
              <li>To detect and prevent abuse, fraud, and unauthorized access.</li>
              <li>To fulfill legal obligations.</li>
            </ul>
            <p>We do not sell, rent, or share your personal data with third parties for marketing purposes.</p>

            <h2>3. Data Storage and Security</h2>
            <p>
              Data is stored on Railway (cloud infrastructure). We use TLS in transit and
              access-controlled databases at rest. API keys are hashed before storage. We retain
              contact and account data for as long as your account is active, plus 30 days after
              termination to allow data export.
            </p>

            <h2>4. Third-Party Services</h2>
            <ul>
              <li>
                <strong>Railway:</strong> hosting and database infrastructure.
              </li>
              <li>
                <strong>PayPal:</strong> payment processing. PayPal's{" "}
                <a href="https://www.paypal.com/webapps/mpp/ua/privacy-full" target="_blank" rel="noopener noreferrer">
                  Privacy Policy
                </a>{" "}
                applies to payment data.
              </li>
              <li>
                <strong>Cloudflare Pages:</strong> static landing page hosting. Cloudflare may
                log request metadata per their infrastructure practices.
              </li>
              <li>
                <strong>Cloudflare Web Analytics:</strong> aggregated visit metrics (page views,
                referrer, approximate country) without third-party advertising cookies.{" "}
                <a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener noreferrer">
                  Cloudflare Privacy Policy
                </a>
                .
              </li>
              <li>
                <strong>Plausible Analytics:</strong> privacy-friendly analytics (no cross-site
                tracking cookies, aggregated data).{" "}
                <a href="https://plausible.io/privacy-focused-web-analytics" target="_blank" rel="noopener noreferrer">
                  Plausible policy
                </a>
                .
              </li>
              <li>
                <strong>Mercado Pago:</strong> local payment processing (Peru/LatAm) when using
                product checkout on the Pro tier.
              </li>
            </ul>
            <p>
              We do not integrate advertising networks or social tracking pixels. Landing
              analytics is used only for aggregated traffic measurement and product improvement.
            </p>

            <h2>5. Cookies and local storage</h2>
            <p>
              The landing page does not use advertising cookies. Cloudflare and Plausible may use
              minimal technical storage per their documentation. The API uses a session token
              stored in your local CLI configuration (~/.cli-market/config.json), not in browser
              cookies.
            </p>

            <h2>6. Your Rights</h2>
            <p>You may at any time:</p>
            <ul>
              <li>Request a copy of your personal data.</li>
              <li>Request correction of inaccurate data.</li>
              <li>Request deletion of your data (subject to legal retention requirements).</li>
              <li>Withdraw consent for any processing based on consent.</li>
            </ul>
            <p>
              To exercise these rights, email{" "}
              <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>. We respond within
              5 business days.
            </p>

            <h2>7. Children</h2>
            <p>
              The Service is not directed to children under 16. We do not knowingly collect data
              from minors. If you believe a minor has provided us data, contact us for immediate
              deletion.
            </p>

            <h2>8. Changes to This Policy</h2>
            <p>
              We will notify registered users by email at least 14 days before material changes
              take effect. Continued use of the Service after the effective date constitutes
              acceptance.
            </p>

            <h2>9. Governing Law</h2>
            <p>
              This Privacy Policy is governed by the laws of Peru. For users in the European
              Economic Area, you may also lodge a complaint with your local data protection
              authority.
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
