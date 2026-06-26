"use client";

import { useLang } from "@/lib/LanguageContext";
import { CTA } from "@/lib/ctaCopy";

export default function ProcureCopilotSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  const bullets = isES
    ? ["Aprobaciones y audit trail", "Checkout: Yape, PayPal, Mercado Pago"]
    : ["Approvals and audit trail", "Checkout: Yape, PayPal, Mercado Pago"];

  return (
    <section id="procure" className="landing-section scroll-mt-24" style={{ backgroundColor: "#f8fafc" }}>
      <div className="landing-container-wide">
        <div className="max-w-[640px] mx-auto text-center">
          <p className="section-eyebrow mb-4">PROCURE COPILOT</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES
              ? <>Para equipos que compran a <span className="text-gradient-orange">escala</span></>
              : <>For teams that purchase at <span className="text-gradient-orange">scale</span></>}
          </h2>
          <p className="section-intro text-[var(--cm-on-surface-variant)]">
            {isES
              ? "Construido sobre CLI Market. Compara precios, aprueba internamente, paga y audita — todo en un solo flujo. Sin hojas de cálculo. Sin WhatsApp."
              : "Built on CLI Market. Compare prices, approve internally, pay, and audit — all in one flow. No spreadsheets. No WhatsApp."}
          </p>
          <div className="flex flex-wrap justify-center gap-4 mb-8 text-sm text-[var(--cm-on-surface-variant)]">
            {bullets.map((b) => (
              <span key={b} className="flex items-center gap-1.5">
                <svg className="w-3.5 h-3.5 shrink-0 text-[var(--cm-mint)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
                {b}
              </span>
            ))}
          </div>
          <div className="flex flex-wrap justify-center gap-3">
            <a
              href={CTA.viewProcurePlans.href}
              className="btn-mint"
              target="_blank"
              rel="noopener noreferrer"
            >
              {isES ? CTA.viewProcurePlans.es : CTA.viewProcurePlans.en}
            </a>
            <a href={CTA.bookProcureDemo.href} className="btn-outline">
              {isES ? CTA.bookProcureDemo.es : CTA.bookProcureDemo.en}
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
