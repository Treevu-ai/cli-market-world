"use client";
import { useLang } from "@/lib/LanguageContext";
import ContactForm from "./ContactForm";

export default function FinalCTA() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="contact" className="relative bg-[var(--wise-canvas-soft)] py-24 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <h2 className="text-[clamp(28px,4vw,40px)] leading-[1.1] font-black text-[var(--wise-ink)] mb-4 tracking-tight whitespace-pre-line">
          {isES ? "Listo para empezar.\nElegí tu plan." : "Ready to start.\nPick your plan."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] mb-10">
          {isES
            ? "Pro: email + link PayPal. Activamos en 24 h tras confirmar pago."
            : "Pro: email + PayPal link. We activate within 24 h after payment."}
        </p>
        <ContactForm initial="pro" />
      </div>
    </section>
  );
}
