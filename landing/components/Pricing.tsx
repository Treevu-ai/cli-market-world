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
    name: "Pro", price: "$49", period_es: "/ mes", period_en: "/ month",
    f_es: ["10,000 consultas / día", "10 claves API (lectura y escritura)", "Checkout automatizado", "Exportación de precios (JSON/CSV)", "Soporte prioritario por email"],
    f_en: ["10,000 requests / day", "10 API keys (read + write)", "Automated checkout", "Price data export (JSON/CSV)", "Priority email support"],
    cta_es: "Obtener Pro", cta_en: "Get Pro", dark: false, featured: true,
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
    <section id="pricing" className="relative bg-[var(--wise-canvas-soft)] py-24">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-8">
          {isES ? "Planes" : "Plans"}
        </p>
        <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-3 tracking-tight">
          {isES ? "Empieza gratis. Escala cuando quieras." : "Start free. Scale when ready."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-md mx-auto mb-12">
          {isES ? "Sin tarjeta. Sin permanencia. Cancela cuando quieras." : "No credit card. No lock-in. Cancel anytime."}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {tiers.map((tier) => (
            <div key={tier.name}
              className={`rounded-3xl p-6 text-left flex flex-col relative ${
                tier.dark
                  ? "bg-[var(--wise-ink)] text-white"
                  : tier.featured
                    ? "bg-[var(--wise-canvas)] border-2 border-[var(--wise-green)] shadow-lg"
                    : "bg-[var(--wise-canvas)] border border-[var(--wise-green-pale)]"
              }`}>
              {tier.featured && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--wise-green)] text-[var(--wise-ink)] text-[11px] font-semibold px-4 py-1 rounded-full">
                  {isES ? "Más popular" : "Most popular"}
                </span>
              )}
              <h3 className={`text-lg font-bold ${tier.dark ? "text-[var(--wise-green)]" : "text-[var(--wise-ink)]"}`}>
                {tier.name}
              </h3>
              <div className="mt-3 mb-5">
                <span className={`text-3xl font-black ${tier.dark ? "text-white" : "text-[var(--wise-ink)]"}`}>
                  {tier.price}
                </span>
                {(tier.period_es || tier.period_en) && (
                  <span className={`text-sm ml-1 ${tier.dark ? "text-white/60" : "text-[var(--wise-mute)]"}`}>
                    {isES ? tier.period_es : tier.period_en}
                  </span>
                )}
              </div>
              <ul className="space-y-2.5 mb-8 flex-1">
                {(isES ? tier.f_es : tier.f_en).map((f, i) => (
                  <li key={i} className={`flex items-start gap-2.5 text-sm ${tier.dark ? "text-white/80" : "text-[var(--wise-body)]"}`}>
                    <svg className="w-4 h-4 mt-0.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke={tier.dark ? "#9fe870" : "var(--wise-green)"} strokeWidth="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                    {f}
                  </li>
                ))}
              </ul>
              <a href={tier.name === "Enterprise" ? "mailto:hello@cli-market.dev" : tier.name === "Pro" ? "https://wise.com/pay/me/ricardoantonioc68" : "https://cli-market-api.onrender.com/auth/keys"}
                 className={`inline-flex items-center justify-center rounded-3xl text-sm font-semibold px-6 py-3 transition-colors w-full ${
                   tier.dark
                     ? "bg-white text-[var(--wise-ink)] hover:bg-[var(--wise-green-pale)]"
                     : tier.featured
                       ? "bg-[var(--wise-green)] text-[var(--wise-ink)] hover:bg-[var(--wise-green-hover)]"
                       : "bg-[var(--wise-ink)] text-[var(--wise-canvas)] hover:bg-[var(--wise-body)]"
                 }`}>
                {isES ? tier.cta_es : tier.cta_en}
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
