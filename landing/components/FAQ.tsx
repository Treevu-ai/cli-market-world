"use client";
import { useLang } from "@/lib/LanguageContext";

const faqs_es = [
  { q: "¿Qué es CLI Market?", a: "CLI Market es una API y CLI que permite a agentes de inteligencia artificial buscar, comparar y comprar productos en 60 retailers de 11 países. Una sola API. Cero scraping." },
  { q: "¿Con qué retailers funciona?", a: "Trabajamos con 60 retailers verificados en 6 líneas: supermercados, farmacias, electro, moda, hogar y departamentales. Abarcamos VTEX, Shopify y Magento en 11 países de Latinoamérica y Europa." },
  { q: "¿Cómo funciona el pago?", a: "Aceptamos Yape, Plin y Wise. El checkout genera un QR que escaneas desde tu app de pagos. El webhook confirma la transacción y actualiza el estado de tu orden automáticamente." },
  { q: "¿Mis agentes pueden usar esto sin intervención humana?", a: "Sí. Las 36 herramientas MCP están diseñadas para que tu agente busque, compare, arme canastas y complete compras de forma autónoma. El pago requiere aprobación humana por ahora." },
  { q: "¿Los precios son reales?", a: "Sí. Nuestro collector corre cada 8 horas contra los 60 retailers y extrae precios reales de góndola. No son estimaciones. Tenemos más de 4,400 precios verificados." },
  { q: "¿Cuánto cuesta?", a: "La CLI es open source y gratuita (licencia MIT). La API tiene un tier gratuito de 1,000 consultas al día. El plan Pro cuesta USD 49 al mes con checkout habilitado y data export. Si tienes un caso más grande, escríbenos." },
];

const faqs_en = [
  { q: "What is CLI Market?", a: "CLI Market is an API and CLI that lets AI agents search, compare, and buy products across 60 retailers in 11 countries. One API. Zero scraping." },
  { q: "Which retailers do you support?", a: "60 verified retailers across 6 lines: supermarkets, pharmacies, electronics, fashion, home, and department stores. We cover VTEX, Shopify, and Magento in 11 countries across Latin America and Europe." },
  { q: "How does payment work?", a: "We support Yape, Plin, and Wise. Checkout generates a QR code you scan from your payment app. A webhook confirms the transaction and updates your order status automatically." },
  { q: "Can my agents use this autonomously?", a: "Yes. All 36 MCP tools are designed for agents to search, compare, build baskets, and complete purchases autonomously. Payment requires human approval for now." },
  { q: "Are the prices real?", a: "Yes. Our collector runs every 8 hours against all 60 retailers and extracts real shelf prices. Not estimates. We have 4,400+ verified prices." },
  { q: "How much does it cost?", a: "The CLI is open source and free (MIT license). The API has a free tier of 1,000 requests per day. The Pro plan is USD 49/month with checkout enabled and data export. For larger use cases, contact us." },
];

export default function FAQ() {
  const { lang } = useLang();
  const faqs = lang === "es" ? faqs_es : faqs_en;

  return (
    <section id="faq" className="relative bg-white py-20 border-t border-[#e5e5e5]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#a3a3a3] font-mono uppercase tracking-[0.15em] mb-8">FAQ</p>
        <h2 className="text-[24px] font-medium text-black mb-12 tracking-tight">
          {lang === "es" ? "Preguntas frecuentes." : "Frequently asked questions."}
        </h2>

        <div className="text-left divide-y divide-[#e5e5e5]">
          {faqs.map((faq, i) => (
            <div key={i} className="py-4">
              <h3 className="text-sm font-medium text-black mb-1">{faq.q}</h3>
              <p className="text-sm text-[#737373] leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
