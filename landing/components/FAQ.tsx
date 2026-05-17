"use client";

import { useState } from "react";
import SectionHeader from "./SectionHeader";

const faqs = [
  {
    question: "¿Qué es CLI Market LATAM?",
    answer:
      "ES UNA CAPA DE INFRAESTRUCTURA QUE TRANSFORMA SUPERMERCADOS DE LATAM EN SISTEMAS DE COMERCIO COMPATIBLES CON AGENTES DE INTELIGENCIA ARTIFICIAL. STRIPE CONVIRTIÓ LOS PAGOS EN APIs; NOSOTROS CONVERTIMOS LOS SUPERMERCADOS EN APIs.",
    defaultOpen: true,
  },
  {
    question: "¿Con qué supermercados funciona?",
    answer:
      "ACTUALMENTE CON 17 COMERCIOS EN 6 LÍNEAS DE NEGOCIO: SUPERMERCADOS (WONG, METRO, PLAZA VEA, CARREFOUR, JUMBO, CHEDRAUI, HEB, OLÍMPICA, ÉXITO), FARMACIAS (DROGA RAIA, DROGASIL), ELECTRO (MAGAZINE LUIZA, MOTOROLA), MODA (RENNER), DEPORTES (CENTAURO) Y HOGAR (HOMECENTER). ADEMÁS, +3M DE PRODUCTOS VÍA OPEN FOOD FACTS.",
  },
  {
    question: "¿Cómo se integra con agentes de IA?",
    answer:
      "EL PROYECTO INCLUYE UN SERVIDOR MCP CON 12 HERRAMIENTAS LISTAS PARA USAR: MARKET_LOGIN, MARKET_LINES, MARKET_SEARCH, MARKET_COMPARE, MARKET_ADD, MARKET_CART, MARKET_CART_UPDATE, MARKET_CART_REMOVE, MARKET_CHECKOUT, MARKET_ORDERS, MARKET_REORDER Y MARKET_ASK. COMPATIBLE CON DEEPSEEK, CLAUDE Y CUALQUIER CLIENTE MCP.",
  },
  {
    question: "¿Necesito conocimientos de programación para usarlo?",
    answer:
      "PARA EL CLI BÁSICO, SOLO NECESITAS SABER USAR UNA TERMINAL. LOS COMANDOS SON SIMPLES: MARKET SEARCH, MARKET COMPARE, MARKET CART, MARKET CHECKOUT. PARA EL MODO AGENTE, CONECTAS EL SERVIDOR MCP A TU ASISTENTE DE IA Y LISTO.",
  },
  {
    question: "¿Cómo se manejan los pagos y la seguridad?",
    answer:
      "EL CHECKOUT SOPORTA MÉTODOS DE PAGO LOCALES COMO YAPE (PERÚ). LAS CREDENCIALES SE ALMACENAN LOCALMENTE. EL SISTEMA ESTÁ DISEÑADO PARA QUE LOS AGENTES DE IA PUEDAN COMPRAR DE FORMA AUTÓNOMA PERO SEGURA, CON CONFIRMACIÓN EXPLÍCITA EN CADA TRANSACCIÓN.",
  },
  {
    question: "¿Cuál es el modelo de negocio?",
    answer:
      "SAAS B2B CON PLANES DESDE $499/MES (STARTER) HASTA $1,999/MES (GROWTH). PLAN EMPRESARIAL PERSONALIZADO. TAMBIÉN OFRECEMOS PRECIOS POR USO DE API Y UNA COMISIÓN DE 1-5% POR TRANSACCIÓN COMPLETADA. WHITE-LABEL DISPONIBLE PARA RETAILERS.",
  },
];

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <section id="faq" className="flex flex-col w-full bg-[#060606] py-12 px-4 sm:py-16 sm:px-6 md:py-[100px] md:px-[120px]">
      <div className="w-full max-w-[480px]">
        <SectionHeader
          label="[07] // PREGUNTAS FRECUENTES"
          title={"¿TIENES\nPREGUNTAS?"}
          subtitle="TODO LO QUE NECESITAS SABER SOBRE CLI MARKET LATAM Y LA INTEGRACIÓN CON AGENTES IA."
          titleWidth="w-full"
          subtitleWidth="w-full"
        />
      </div>

      <div className="h-10 md:h-[64px]" />

      <div className="flex flex-col w-full">
        {faqs.map((faq, i) => {
          const isOpen = openIndex === i;
          return (
            <div key={i} className="flex flex-col w-full border-t border-t-[#1D1D1D]">
              <button
                className="flex items-center justify-between w-full py-5 md:h-[72px] text-left gap-4"
                onClick={() => setOpenIndex(isOpen ? -1 : i)}
              >
                <span className="font-grotesk text-[14px] md:text-[16px] font-bold text-[#F5F5F0] tracking-[1px]">
                  {faq.question}
                </span>
                <div
                  className="flex items-center justify-center w-[32px] h-[32px] shrink-0"
                  style={{ backgroundColor: isOpen ? "#00FF88" : "#1A1A1A", border: isOpen ? "none" : "1px solid #3D3D3D" }}
                >
                  <span
                    className="font-ibm-mono text-[14px] font-bold"
                    style={{ color: isOpen ? "#0A0A0A" : "#888888" }}
                  >
                    {isOpen ? "—" : "+"}
                  </span>
                </div>
              </button>
              {isOpen && faq.answer && (
                <div className="pb-8">
                  <p className="font-ibm-mono text-[12px] md:text-[13px] text-[#888888] tracking-[1px] leading-[1.6]">
                    {faq.answer}
                  </p>
                </div>
              )}
            </div>
          );
        })}
        <div className="border-t border-t-[#1D1D1D]" />
      </div>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-[16px] pt-10 md:pt-[48px]">
        <span className="font-ibm-mono text-[13px] text-[#555555] tracking-[1px]">
          ¿TIENES MÁS PREGUNTAS?
        </span>
        <a
          href="https://github.com/Treevu-ai/cli-market-latam"
          className="font-ibm-mono text-[13px] font-bold text-[#00FF88] tracking-[1px] hover:underline"
        >
          VISITA EL REPOSITORIO &gt;
        </a>
      </div>
    </section>
  );
}
