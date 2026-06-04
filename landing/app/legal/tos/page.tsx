import LegalPage from "@/components/LegalPage";

export default function TermsOfService() {
  return (
    <LegalPage title="Terms of Service" updated="May 20, 2026">
      <p>
        <strong>Entity:</strong> Sinapsis Innovadora S.A.C. (operator of CLI Market) ·{" "}
        <strong>Contact:</strong>{" "}
        <a href="mailto:hello@cli-market.dev">hello@cli-market.dev</a>
      </p>

      <hr />

      <h2>1. Acceptance of Terms</h2>
      <p>
        By accessing or using the CLI Market API, MCP tools, CLI client, or any related data
        services (collectively, the "Service"), you agree to be bound by these Terms of Service
        ("Terms"). If you do not agree, do not use the Service.
      </p>

      <h2>2. Description of Service</h2>
      <p>
        CLI Market provides a programmable interface for product search, price comparison, and
        purchase execution across 66 retailers (36 verified active) in 11 countries. The Service
        is delivered via PyPI package (<code>pip install cli-market</code>), MCP server (43
        tools), a REST API, and data snapshots (PostgreSQL databases of pricing history and SKU
        mappings — licensed separately under the Data License Agreement).
      </p>

      <h2>3. Account Registration</h2>
      <p>
        You must register an account to use the Service beyond rate-limited public access. You
        are responsible for maintaining the confidentiality of your API keys and account
        credentials, and must provide accurate and complete registration information.
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
        The CLI Market software is licensed under the MIT License. Pricing data, SKU mappings,
        historical snapshots, and retailer indexes ("Data") are licensed separately under the
        Data License Agreement ("DLA"). You retain ownership of your purchase history and cart
        data.
      </p>

      <h2>6. Fees and Payment</h2>
      <p>
        Current pricing tiers are published at{" "}
        <a href="https://cli-market.dev/#pricing">cli-market.dev/#pricing</a>. Fees are charged
        monthly or annually as selected at registration. CLI Market reserves the right to modify
        pricing with 30 days notice. Failure to pay may result in suspension; data exports are
        available for 30 days post-suspension.
      </p>

      <h2>7. Intellectual Property</h2>
      <p>
        CLI Market and Sinapsis Innovadora S.A.C. retain all rights in the Service, including
        software, data schemas, aggregation logic, and branding. The MIT License governs the
        open-source software components only — it does not extend to the proprietary Data.
        "CLI Market" and the CLI Market logo are trademarks of Sinapsis Innovadora S.A.C.
      </p>

      <h2>8. Third-Party Retailers</h2>
      <p>
        CLI Market connects to third-party retailer APIs (VTEX, Shopify, Magento). CLI Market is
        not responsible for product availability or pricing accuracy as reported by retailers,
        failed transactions due to retailer-side errors, or changes to retailer API structures.
        Users are responsible for compliance with retailer terms when placing orders.
      </p>

      <h2>9. Limitation of Liability</h2>
      <p>
        The Service is provided "as is" without warranty of any kind. To the maximum extent
        permitted by law, CLI Market's liability for any claim is limited to the fees paid by you
        in the 12 months preceding the claim. CLI Market is not liable for trading losses,
        inventory decisions, or business outcomes based on pricing data, nor for delays or
        inaccuracies in data refresh cycles.
      </p>

      <h2>10. Termination</h2>
      <p>
        Either party may terminate with 30 days written notice. CLI Market may suspend or
        terminate immediately for violation of the Acceptable Use Policy, non-payment, or
        legal/regulatory requirement. Upon termination, you may export your data for 30 days,
        after which it is permanently deleted.
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
    </LegalPage>
  );
}
