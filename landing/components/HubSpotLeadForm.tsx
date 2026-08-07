"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

type ProductLine = "CLI Market Pro" | "Procure Starter" | "Procure Pro" | "Intelligence" | "Custom";
type TierIntent = "Starter $9" | "Pro $39" | "Enterprise" | "Procure Starter $29" | "Procure Pro $79" | "Custom";

interface HubSpotLeadFormProps {
  productLine?: ProductLine;
  tierIntent?: TierIntent;
  onSuccess?: () => void;
  buttonLabel?: string;
  buttonClassName?: string;
}

export default function HubSpotLeadForm({
  productLine = "CLI Market Pro",
  tierIntent = "Pro $39",
  onSuccess,
  buttonLabel,
  buttonClassName = "btn-mint w-full",
}: HubSpotLeadFormProps) {
  const { lang } = useLang();
  const isES = lang === "es";
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // 1. Submit to HubSpot form
      const hubspotFormData = {
        submittedAt: Date.now(),
        fields: [
          { name: "email", value: email },
          { name: "product_line", value: productLine },
          { name: "tier_intent", value: tierIntent },
          { name: "lead_source", value: "Landing" },
        ],
      };

      const hubspotResponse = await fetch(
        `https://api.hsforms.com/submissions/v3/integration/submit/${process.env.NEXT_PUBLIC_HUBSPOT_PORTAL_ID}/${process.env.NEXT_PUBLIC_HUBSPOT_FORM_ID}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(hubspotFormData),
        }
      );

      if (!hubspotResponse.ok) {
        throw new Error("HubSpot submission failed");
      }

      // 2. Trigger n8n workflow
      const n8nWebhookUrl = process.env.NEXT_PUBLIC_N8N_LEAD_SYNC_WEBHOOK_URL;
      if (n8nWebhookUrl) {
        await fetch(n8nWebhookUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email,
            product_line: productLine,
            tier_intent: tierIntent,
            lead_source: "Landing",
          }),
        });
      }

      setSuccess(true);
      onSuccess?.();
    } catch (err) {
      setError(isES ? "Error al enviar. Intenta nuevamente." : "Error submitting. Please try again.");
      console.error("Form submission error:", err);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="text-center p-4 rounded-lg bg-[var(--cm-mint)]/10 border border-[var(--cm-mint)]/30">
        <p className="text-[var(--cm-mint)] font-semibold text-sm">
          {isES ? "¡Gracias! Te contactaremos pronto." : "Thank you! We'll be in touch soon."}
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={isES ? "tu@email.com" : "your@email.com"}
          required
          className="w-full px-4 py-3 rounded-lg bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] text-[var(--cm-on-surface)] placeholder:text-[var(--cm-on-surface-variant)]/50 focus:outline-none focus:border-[var(--cm-mint)] focus:ring-1 focus:ring-[var(--cm-mint)] transition-all text-sm"
          disabled={loading}
        />
      </div>

      {error && (
        <p className="text-xs text-[var(--cm-error)] font-medium">{error}</p>
      )}

      <button
        type="submit"
        disabled={loading || !email}
        className={`${buttonClassName} ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        {loading
          ? isES
            ? "Enviando..."
            : "Sending..."
          : buttonLabel || (isES ? "Comenzar prueba gratis" : "Start free trial")}
      </button>

      <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 text-center">
        {isES ? "Sin compromiso · Cancela cuando quieras" : "No commitment · Cancel anytime"}
      </p>
    </form>
  );
}
