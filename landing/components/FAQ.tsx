import { useLang } from "@/lib/LanguageContext";
"use client";
import { useState } from "react";

const faqs = [
  { question: "¿Qué es CLI Market?", answer: "Es una capa de infraestructura que convierte 3,600+ comercios VTEX en 67 países y 12 líneas de negocio en sistemas compatibles con agentes de inteligencia artificial. Stripe convirtió los pagos en APIs; nosotros convertimos el comercio en APIs.", defaultOpen: true },
  { question: "¿Con qué comercios funciona?", answer: "Con 3,600+ comercios en 12 líneas: supermercados (Wong, Metro, Plaza Vea, Carrefour, Jumbo, Coto, Dia, Pão de Açúcar, Chedraui, HEB, Olímpica, Éxito, Lider, Soriana), farmacias (Droga Raia, Drogasil, Inkafarma, Farmatodo), electro (Magazine Luiza, Samsung, Motorola, LG, Alkosto, Frávega), moda (Renner, C&A, Marisa, Riachuelo, Arturo Calle, Leonisa), deportes (Centauro, Nike, Adidas, Decathlon en 10 países), hogar (Homecenter, Sodimac, Easy, Promart, Leroy Merlin) y más." },
  { question: "¿Cómo se integra con agentes de IA?", answer: "El proyecto incluye un servidor MCP con 12 herramientas listas para usar: market_login, market_lines, market_search, market_compare, market_add, market_cart, market_cart_update, market_cart_remove, market_checkout, market_orders, market_reorder y market_ask. Compatible con DeepSeek, Claude y cualquier cliente MCP." },
  { question: "¿Necesito saber programar?", answer: "Para el CLI básico solo necesitas saber usar una terminal. Los comandos son simples: market search, market compare, market cart, market checkout. Para el modo agente, conectas el servidor MCP a tu asistente de IA y listo." },
  { question: "¿Cómo se manejan los pagos?", answer: "El checkout está diseñado para integrarse con métodos de pago locales de cada país: Yape y Plin en Perú, PIX en Brasil, Mercado Pago en Argentina, OXXO y SPEI en México, y tarjetas de crédito en toda la región. Las credenciales se almacenan localmente con PBKDF2." },
  { question: "¿Cuánto cuesta?", answer: "El CLI es open source y gratuito (licencia MIT). La API tiene un free tier disponible para que puedas probarla. Los planes pagos para escala enterprise estarán disponibles pronto. Si tienes un caso de uso específico, escríbenos." },
];

export default function FAQ() {
  const { t: _t } = useLang();
  const [openIndex, setOpenIndex] = useState(0);
  return (
    <section id="faq" className="flex flex-col w-full bg-[#060606] py-12 px-4 sm:py-16 sm:px-6 md:py-[80px] md:px-[120px] gap-8 sm:gap-10">
      <div className="flex flex-col gap-[12px] w-full">
        <span className="font-mono text-[9px] sm:text-[10px] md:text-[11px] font-bold text-[#FFD600] tracking-[2px] md:tracking-[3px] uppercase">FAQ</span>
        <h2 className="font-grotesk text-[26px] sm:text-[32px] md:text-[48px] font-bold text-[#F5F5F0] tracking-[-1px] leading-[1.05]">{_t("faq_title")}</h2>
      </div>
      <div className="flex flex-col w-full max-w-[640px]">
        {faqs.map((faq, i) => {
          const isOpen = openIndex === i;
          return (
            <div key={i} className="border-b border-[#1A1A1A]">
              <button onClick={() => setOpenIndex(isOpen ? -1 : i)} className="flex items-center justify-between w-full py-4 sm:py-5 text-left">
                <span className="font-mono text-[12px] sm:text-[13px] text-[#AAA] tracking-[0.5px] pr-4">{faq.question}</span>
                <span className="font-mono text-[16px] text-[#555] shrink-0">{isOpen ? "−" : "+"}</span>
              </button>
              {isOpen && <p className="font-mono text-[11px] sm:text-[12px] text-[#666] leading-[1.6] pb-4 sm:pb-5">{faq.answer}</p>}
            </div>
          );
        })}
      </div>
    </section>
  );
}
