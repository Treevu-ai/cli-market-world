"use client";
import { useLang } from "@/lib/LanguageContext";

const tiers = [
  {
    name: "Free", price: "$0", period: "para siempre",
    features: ["60 req/min · 1,000 req/día", "1 API key (read)", "30 retailers · 6 líneas", "Dashboard en tiempo real", "Pago con Yape, Plin o Wise"],
    cta: "Empezar gratis", dark: false,
  },
  {
    name: "Pro", price: "$49", period: "/mes",
    features: ["300 req/min · 10,000 req/día", "10 API keys (read + write)", "Checkout habilitado", "Data moat export (JSON/CSV)", "Soporte prioritario"],
    cta: "Suscribirse", dark: false,
  },
  {
    name: "Enterprise", price: "Custom", period: "",
    features: ["Rate limits custom", "API keys ilimitadas", "Endpoints dedicados", "Webhooks + SLA 99.5%", "Onboarding asistido"],
    cta: "Contactar", dark: true,
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
                {tier.period && <span className={`text-sm ${tier.dark ? "text-white/50" : "text-[#737373]"}`}>{tier.period}</span>}
              </div>
              <ul className="space-y-2 mb-6 flex-1">
                {tier.features.map((f, i) => (
                  <li key={i} className={`flex items-start gap-2 text-sm ${tier.dark ? "text-white/60" : "text-[#525252]"}`}>
                    <span className="mt-0.5 shrink-0">—</span>
                    {f}
                  </li>
                ))}
              </ul>
              <a href={tier.name === "Enterprise" ? "mailto:hello@cli-market.dev" : "https://wise.com/pay/me/ricardoantonioc68"}
                 className={`inline-flex items-center justify-center rounded-full text-sm font-medium px-5 py-2.5 h-9 transition-colors w-full ${tier.dark ? "bg-white text-black hover:bg-[#fafafa]" : "bg-black text-white hover:bg-[#090909]"}`}>
                {tier.cta}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
