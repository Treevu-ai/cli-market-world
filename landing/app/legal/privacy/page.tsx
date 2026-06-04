import LegalPage from "@/components/LegalPage";

export default function PrivacyPolicy() {
  return (
    <LegalPage title="Privacy Policy" updated="June 4, 2026">
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
          <strong>Account data:</strong> email address, name (optional), and the plan or role
          you select when signing up or submitting a contact form.
        </li>
        <li>
          <strong>Usage data:</strong> API request counts, timestamps, and the API key tier
          associated with each request. We do not log query content beyond what is necessary
          for rate limiting and billing.
        </li>
        <li>
          <strong>Transaction data:</strong> order details and payment confirmation events
          (via PayPal webhook). We do not store card numbers or full payment credentials.
        </li>
        <li>
          <strong>Technical data:</strong> IP address (for rate limiting and abuse prevention),
          user agent, and referrer for the current session only.
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
          <strong>Cloudflare Pages:</strong> static landing page hosting. Cloudflare may log
          anonymized request metadata per their standard infrastructure practices.
        </li>
      </ul>
      <p>We do not integrate advertising networks, analytics platforms, or social tracking pixels.</p>

      <h2>5. Cookies</h2>
      <p>
        The landing page does not use tracking cookies. The API uses a session token stored in
        your local CLI configuration (~/.cli-market/config.json), not in browser cookies.
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
        <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>. We respond within 5
        business days.
      </p>

      <h2>7. Children</h2>
      <p>
        The Service is not directed to children under 16. We do not knowingly collect data from
        minors. If you believe a minor has provided us data, contact us for immediate deletion.
      </p>

      <h2>8. Changes to This Policy</h2>
      <p>
        We will notify registered users by email at least 14 days before material changes take
        effect. Continued use of the Service after the effective date constitutes acceptance.
      </p>

      <h2>9. Governing Law</h2>
      <p>
        This Privacy Policy is governed by the laws of Peru. For users in the European Economic
        Area, you may also lodge a complaint with your local data protection authority.
      </p>

      <hr />
      <p>
        <strong>Sinapsis Innovadora S.A.C.</strong> · RUC 20613045563 · Lima, Perú ·{" "}
        <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
      </p>
    </LegalPage>
  );
}
