"use client";
import { useLang } from "@/lib/LanguageContext";

const tiers = [
  {
    name: "Free", price: "$0", period_es: "para siempre", period_en: "forever",
    f_es: ["60 req/min · 1,000 req/día", "1 API key (read)", "Dashboard en tiempo real", "Pago con Yape, Plin, Wise o PayPal"],
    f_en: ["60 req/min · 1,000 req/day", "1 API key (read)", "Live dashboard", "Pay with Yape, Plin, Wise or PayPal"],
    cta_es: "Empezar gratis", cta_en: "Start free", dark: false,
  },
  {
    name: "Pro", price: "$49", period_es: "/mes", period_en: "/month",
    f_es: ["300 req/min · 10,000 req/día", "10 API keys (read + write)", "Checkout habilitado", "Data moat export (JSON/CSV)", "Soporte prioritario"],
    f_en: ["300 req/min · 10,000 req/day", "10 API keys (read + write)", "Checkout enabled", "Data moat export (JSON/CSV)", "Priority support"],
    cta_es: "Suscribirse", cta_en: "Subscribe", dark: false,
  },
  {
    name: "Enterprise", price: "Custom", period_es: "", period_en: "",
    f_es: ["Rate limits custom", "API keys ilimitadas", "Endpoints dedicados", "Webhooks + SLA 99.5%", "Onboarding asistido"],
    f_en: ["Custom rate limits", "Unlimited API keys", "Dedicated endpoints", "Webhooks + SLA 99.5%", "Assisted onboarding"],
    cta_es: "Contactar", cta_en: "Contact", dark: true,
  },
];

export default function Pricing() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="pricing" className="relative bg-white py-20 border-t border-[#e5e5e5]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#a3a3a3] font-mono uppercase tracking-[0.15em] mb-8">
          {isES ? "Planes" : "Plans"}
        </p>
        <h2 className="text-[24px] font-medium text-black mb-3 tracking-tight">
          {isES ? "Empieza gratis.\nEscala cuando quieras." : "Start free.\nScale when ready."}
        </h2>
        <p className="text-sm text-[#737373] max-w-md mx-auto mb-12">
          {isES ? "Sin tarjeta de crédito. Sin compromiso. Cancela cuando quieras." : "No credit card. No commitment. Cancel anytime."}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {tiers.map((tier) => (
            <div key={tier.name}
              className={`rounded-lg border p-6 text-left flex flex-col ${tier.dark ? "bg-[#171717] border-[#171717] text-white" : "bg-white border-[#e5e5e5]"}`}>
              <h3 className={`text-lg font-medium ${tier.dark ? "text-white" : "text-black"}`}>{tier.name}</h3>
              <div className="mt-2 mb-4">
                <span className={`text-2xl font-medium ${tier.dark ? "text-white" : "text-black"}`}>{tier.price}</span>
                {(isES ? tier.period_es : tier.period_en) && (
                  <span className={`text-sm ${tier.dark ? "text-white/50" : "text-[#737373]"}`}>
                    {isES ? tier.period_es : tier.period_en}
                  </span>
                )}
              </div>
              <ul className="space-y-2 mb-6 flex-1">
                {(isES ? tier.f_es : tier.f_en).map((f, i) => (
                  <li key={i} className={`flex items-start gap-2 text-sm ${tier.dark ? "text-white/60" : "text-[#525252]"}`}>
                    <span className="mt-0.5 shrink-0">—</span>
                    {f}
                  </li>
                ))}
              </ul>
              <a href={tier.name === "Enterprise" ? "mailto:hello@cli-market.dev" : "https://wise.com/pay/me/ricardoantonioc68"}
                 className={`inline-flex items-center justify-center rounded-full text-sm font-medium px-5 py-2.5 h-9 transition-colors w-full ${tier.dark ? "bg-white text-black hover:bg-[#fafafa]" : "bg-black text-white hover:bg-[#090909]"}`}>
                {isES ? tier.cta_es : tier.cta_en}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
