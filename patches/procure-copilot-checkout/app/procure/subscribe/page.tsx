"use client";

import Link from "next/link";
import PaymentReturnBanner from "@/components/PaymentReturnBanner";
import ProcurePricingPanel from "@/components/ProcurePricingPanel";
import LangToggle from "@/components/LangToggle";

export default function SubscribePage() {
  return (
    <main
      id="main-content"
      className="relative min-h-screen bg-[var(--cm-background)] brand-mode-operations"
    >
      <LangToggle className="fixed top-4 right-4 z-50" />
      <div className="landing-container-wide py-12 sm:py-16">
        <p className="text-center mb-6">
          <Link
            href="/procure"
            className="text-sm text-[var(--cm-mint)] font-semibold hover:underline"
          >
            ← Procure Copilot
          </Link>
        </p>
        <div className="text-center mb-10">
          <p className="section-eyebrow mb-3">Procure Copilot</p>
          <h1 className="section-title text-balance">Suscríbete · Compare, Ops o Scale</h1>
          <p className="section-intro max-w-xl mx-auto">
            Pago seguro vía PayPal (USD) o soles (Mercado Pago · Yape · Plin). Sinapsis Innovadora
            S.A.C.
          </p>
        </div>
        <PaymentReturnBanner />
        <ProcurePricingPanel />
      </div>
    </main>
  );
}
