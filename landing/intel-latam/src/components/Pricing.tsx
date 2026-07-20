import React, { useState } from "react";
import { Check, Info, HelpCircle, ArrowRight } from "lucide-react";
import ScrollReveal from "./ScrollReveal";
import CheckoutModal from "./CheckoutModal";

export default function Pricing() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("annual");
  const [checkoutPlan, setCheckoutPlan] = useState<"starter" | "pro" | null>(null);

  const pricingTiers = [
    {
      name: "Starter",
      plan: "starter" as const,
      description: "Ideal para validación de mercado y análisis tácticos de un solo rol o país.",
      priceMonthly: "9",
      priceAnnual: "9",
      features: [
        "Acceso limitado a base de SKUs",
        "Consultas básicas por WhatsApp (150/mes)",
        "Monitoreo de hasta 2 Competidores",
        "Refresco de datos diario (24H)",
        "Soporte de comunidad por correo",
        "Reportes básicos en PDF"
      ],
      ctaText: "Iniciar Starter Gratis",
      highlighted: false,
      badge: "Validación"
    },
    {
      name: "Pro",
      plan: "pro" as const,
      description: "Diseñado para equipos operativos que necesitan automatización de canastas y APIs.",
      priceMonthly: "39",
      priceAnnual: "33",
      features: [
        "Resolución de Entidades ilimitada",
        "Procure Copilot integrado",
        "Consultas de WhatsApp ilimitadas",
        "Monitoreo de hasta 10 Competidores",
        "Refresco de datos de 4 Horas",
        "Acceso API REST completo (Sandbox)",
        "Soporte prioritario por WhatsApp"
      ],
      ctaText: "Probar Pro Gratis",
      highlighted: true,
      badge: "Más Elegido"
    },
    {
      name: "Enterprise",
      plan: null,
      description: "Para equipos de Revenue, Growth y Compras que requieren todo el Data Moat de LATAM.",
      priceMonthly: "Consultar",
      priceAnnual: "Consultar",
      features: [
        "Data Moat completo regional",
        "Reportes especializados Price Pulse",
        "Procure Copilot multilocal",
        "Competidores ilimitados",
        "Refresco en tiempo real custom",
        "Acceso API Dedicada de alto caudal",
        "Soporte de un Analista Dedicado",
        "SLA garantizado por contrato"
      ],
      ctaText: "Contactar Ventas",
      highlighted: false,
      badge: "Corporativo"
    }
  ];

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <section className="bg-[#0a0a0a] text-[#f5f5f5] py-20 lg:py-28 border-b border-white/10" id="pricing-section">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
        
        {/* Header Block */}
        <ScrollReveal duration={0.8}>
          <div className="mx-auto max-w-3xl">
            <span className="font-mono text-[10px] font-bold text-[#bef264] uppercase tracking-widest bg-[#bef264]/5 border border-[#bef264]/20 px-3 py-1.5 rounded-sm">
              Precios Claros
            </span>
            <h2 className="mt-6 text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Un plan para cada etapa de tu crecimiento.
            </h2>
            <p className="mt-3 text-white/60 text-xs sm:text-sm max-w-xl mx-auto">
              Comienza gratis con nuestra de WhatsApp interactiva y escala según la frecuencia y el volumen de datos de tu góndola.
            </p>
          </div>
        </ScrollReveal>

        {/* Toggle Billing Cycle */}
        <ScrollReveal delay={0.1} duration={0.8}>
          <div className="mt-10 flex items-center justify-center space-x-4">
            <span className={`text-[10px] font-bold font-mono uppercase tracking-wider transition-colors duration-150 ${billingCycle === "monthly" ? "text-[#bef264]" : "text-white/40"}`}>
              Facturación Mensual
            </span>
            
            <button
              onClick={() => setBillingCycle(billingCycle === "monthly" ? "annual" : "monthly")}
              className="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-sm border border-white/20 bg-white/5 transition-colors duration-200 ease-in-out focus:outline-none"
              id="billing-cycle-toggle"
              aria-label="Toggle billing cycle"
            >
              <span
                className={`pointer-events-none inline-block h-4.5 w-4.5 transform rounded-sm bg-[#bef264] shadow transition duration-200 ease-in-out mt-[1px] ml-[1px] ${
                  billingCycle === "annual" ? "translate-x-5" : "translate-x-0"
                }`}
              />
            </button>

            <span className={`text-[10px] font-bold font-mono uppercase tracking-wider flex items-center space-x-2 transition-colors duration-150 ${billingCycle === "annual" ? "text-[#bef264]" : "text-white/40"}`}>
              <span>Anual</span>
              <span className="bg-[#bef264]/10 text-[#bef264] text-[9px] font-mono px-2 py-0.5 rounded-sm font-bold border border-[#bef264]/20 uppercase tracking-wider">
                20% Ahorro
              </span>
            </span>
          </div>
        </ScrollReveal>

        {/* Pricing Cards Grid */}
        <div className="mt-16 grid grid-cols-1 gap-8 lg:grid-cols-3 max-w-6xl mx-auto items-stretch animate-once">
          
          {pricingTiers.map((tier, index) => {
            const isEnterprise = tier.priceMonthly === "Consultar";
            
            return (
              <ScrollReveal
                key={index}
                delay={index * 0.12}
                duration={0.8}
                className={`flex flex-col justify-between rounded-sm p-8 text-left transition-all duration-300 relative ${
                  tier.highlighted
                    ? "bg-white/5 border border-[#bef264]/40 shadow-2xl lg:scale-105 z-10"
                    : "bg-white/5 border border-white/10 hover:border-white/20"
                }`}
              >
                
                {/* Badge layout */}
                {tier.badge && (
                  <span className={`absolute top-4 right-4 text-[9px] font-mono font-bold uppercase tracking-widest px-2.5 py-1 rounded-sm ${
                    tier.highlighted
                      ? "bg-[#bef264] text-black shadow-sm"
                      : "bg-white/10 text-white/85"
                  }`}>
                    {tier.badge}
                  </span>
                )}

                {/* Info Block */}
                <div>
                  <h3 className="text-base font-bold font-mono uppercase tracking-wider text-white">
                    {tier.name}
                  </h3>
                  
                  <p className="text-xs mt-3 leading-relaxed min-h-[40px] text-white/50">
                    {tier.description}
                  </p>

                  {/* Price display */}
                  <div className="mt-6 flex items-baseline">
                    {isEnterprise ? (
                      <span className="text-3xl font-extrabold tracking-tight text-white font-sans">
                        Consultar
                      </span>
                    ) : (
                      <>
                        <span className="text-4xl font-extrabold tracking-tight font-sans text-white">
                          ${billingCycle === "annual" ? tier.priceAnnual : tier.priceMonthly}
                        </span>
                        <span className="text-[10px] ml-2 font-mono uppercase tracking-wider text-white/40">
                          USD / mes
                        </span>
                      </>
                    )}
                  </div>

                  {billingCycle === "annual" && !isEnterprise && tier.priceMonthly !== tier.priceAnnual && (
                    <div className="mt-1.5 text-[9px] font-mono text-[#bef264] font-bold uppercase tracking-wider">
                      Facturado anual (ahorras ${parseInt(tier.priceMonthly) * 12 - parseInt(tier.priceAnnual) * 12} USD al año)
                    </div>
                  )}

                  <hr className="my-6 border-white/10" />

                  {/* Features List */}
                  <ul className="space-y-3.5 text-xs">
                    {tier.features.map((feature, fIdx) => (
                      <li key={fIdx} className="flex items-start">
                        <Check className="h-4 w-4 text-[#bef264] mr-2.5 shrink-0 stroke-[3]" />
                        <span className="text-white/70 font-sans">
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Call To Action button */}
                <div className="mt-8">
                  <button
                    onClick={() => {
                      if (isEnterprise) {
                        scrollToSection("contacto-footer");
                      } else if (tier.plan) {
                        setCheckoutPlan(tier.plan);
                      }
                    }}
                    className={`w-full inline-flex items-center justify-center rounded-sm py-3 px-4 text-xs font-mono font-bold uppercase tracking-widest shadow-sm transition-all active:scale-[0.98] cursor-pointer ${
                      tier.highlighted
                        ? "bg-[#bef264] text-black hover:bg-[#d9f99d]"
                        : "bg-white/5 text-white border border-white/10 hover:bg-white/10"
                    }`}
                  >
                    <span>{tier.ctaText}</span>
                    <ArrowRight className="ml-2 h-3.5 w-3.5" />
                  </button>
                </div>

              </ScrollReveal>
            );
          })}

        </div>

        {/* Simple trust footnote */}
        <ScrollReveal delay={0.4} duration={0.8}>
          <p className="mt-12 text-[10px] text-white/40 font-mono uppercase tracking-wider flex items-center justify-center space-x-1.5">
            <Info className="h-3.5 w-3.5 text-[#bef264]" />
            <span>Todos los planes de prueba incluyen un Sandbox de datos de prueba de LATAM por 14 días.</span>
          </p>
        </ScrollReveal>

      </div>

      <CheckoutModal
        open={checkoutPlan !== null}
        onClose={() => setCheckoutPlan(null)}
        plan={checkoutPlan ?? "starter"}
      />
    </section>
  );
}
