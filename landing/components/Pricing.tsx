"use client";
import { useLang } from "@/lib/LanguageContext";

const tiers = [
  {
    name: "Free", price: "$0", period_es: "sin costo", period_en: "no cost",
    f_es: ["1,000 consultas / día", "1 clave API (lectura)", "Dashboard de precios", "Todos los métodos de pago"],
    f_en: ["1,000 requests / day", "1 API key (read-only)", "Live price dashboard", "All payment methods included"],
    cta_es: "Comenzar ahora", cta_en: "Start now", dark: false,
  },
  {
    name: "Pro", price: "$49", period_es: "/ al mes", period_en: "/ month",
    f_es: ["10,000 consultas / día", "10 claves API (lectura y escritura)", "Checkout automatizado", "Exportación de precios (JSON/CSV)", "Soporte prioritario por email"],
    f_en: ["10,000 requests / day", "10 API keys (read + write)", "Automated checkout", "Price data export (JSON/CSV)", "Priority email support"],
    cta_es: "Obtener Pro", cta_en: "Get Pro", dark: false,
  },
  {
    name: "Enterprise", price: "A medida", period_es: "", period_en: "",
    f_es: ["Límites personalizados", "Claves API ilimitadas", "Endpoints dedicados + webhooks", "SLA 99.5 % + soporte 24/7", "Onboarding y consultoría"],
    f_en: ["Custom rate limits", "Unlimited API keys", "Dedicated endpoints + webhooks", "99.5% SLA + 24/7 support", "Onboarding and consulting"],
    cta_es: "Hablar con ventas", cta_en: "Talk to sales", dark: true,
  },
];

export default function Pricing() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="pricing" className="relative bg-[#e8ebe6] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#868685] font-mono uppercase tracking-[0.15em] mb-8">
          {isES ? "Planes" : "Plans"}
        </p>
        <h2 className="text-[24px] font-medium text-[#0e0f0c] mb-3 tracking-tight">
          {isES ? "Empieza gratis.\nEscala cuando quieras." : "Start free.\nScale when ready."}
        </h2>
        <p className="text-sm text-[#454745] max-w-md mx-auto mb-12">
          {isES ? "Sin tarjeta. Sin permanencia. Cancela cuando quieras." : "No credit card. No lock-in. Cancel anytime."}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {tiers.map((tier) => (
            <div key={tier.name}
              className={`rounded-3xl border p-6 text-left flex flex-col ${tier.dark ? "bg-[#0e0f0c] border-[#0e0f0c] text-white" : "bg-white border-[#c5edab]"}`}>
              <h3 className={`text-lg font-medium ${tier.dark ? "text-white" : "text-[#0e0f0c]"}`}>{tier.name}</h3>
              <div className="mt-2 mb-4">
                <span className={`text-2xl font-medium ${tier.dark ? "text-white" : "text-[#0e0f0c]"}`}>{tier.price}</span>
                {(isES ? tier.period_es : tier.period_en) && (
                  <span className={`text-sm ${tier.dark ? "text-white/50" : "text-[#454745]"}`}>
                    {isES ? tier.period_es : tier.period_en}
                  </span>
                )}
              </div>
              <ul className="space-y-2 mb-6 flex-1">
                {(isES ? tier.f_es : tier.f_en).map((f, i) => (
                  <li key={i} className={`flex items-start gap-2 text-sm ${tier.dark ? "text-white/60" : "text-[#454745]"}`}>
                    <span className="mt-0.5 shrink-0">—</span>
                    {f}
                  </li>
                ))}
              </ul>
              <a href={tier.name === "Enterprise" ? "mailto:hello@cli-market.dev" : "https://wise.com/pay/me/ricardoantonioc68"}
                 className={`inline-flex items-center justify-center rounded-full text-sm font-medium px-5 py-2.5 h-9 transition-colors w-full ${tier.dark ? "bg-white text-[#0e0f0c] hover:bg-[#e2f6d5]" : "bg-[#9fe870] text-[#0e0f0c] hover:bg-[#cdffad]"}`}>
                {isES ? tier.cta_es : tier.cta_en}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
