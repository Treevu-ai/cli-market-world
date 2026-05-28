"use client";
import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import ContactForm from "./ContactForm";

export default function FinalCTA() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [paid, setPaid] = useState(false);

  useEffect(() => {
    if (window.location.search.includes("sub=success")) {
      setPaid(true);
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, []);

  if (paid) return (
    <section id="contact" className="relative bg-[var(--wise-canvas-soft)] py-24 border-t border-[#c5edab]">
      <div className="max-w-[480px] mx-auto px-6 text-center">
        <div className="bg-[var(--wise-green-pale)] rounded-3xl p-8">
          <p className="text-2xl mb-2">🎉</p>
          <h2 className="text-xl font-black text-[var(--wise-ink)] mb-2">
            {isES ? "Suscripcion confirmada" : "Subscription confirmed"}
          </h2>
          <p className="text-sm text-[var(--wise-body)]">
            {isES ? "Gracias por suscribirte a CLI Market Pro." : "Thanks for subscribing to CLI Market Pro."}
          </p>
        </div>
      </div>
    </section>
  );

  return (
    <section id="contact" className="relative bg-[var(--wise-canvas-soft)] py-24 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <h2 className="text-[clamp(28px,4vw,40px)] leading-[1.1] font-black text-[var(--wise-ink)] mb-4 tracking-tight">
          {isES ? "Listo para empezar.\nElegi tu plan." : "Ready to start.\nPick your plan."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] mb-10">
          {isES ? "Sin permanencia. Cancela cuando quieras." : "No commitment. Cancel anytime."}
        </p>
        <ContactForm initial="pro" />
      </div>
    </section>
  );
}
