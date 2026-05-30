"use client";

import { useLang } from "@/lib/LanguageContext";
import ContactForm from "@/components/ContactForm";
import RetailerApplyForm from "@/components/RetailerApplyForm";

export default function ContactSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="contact" className="relative bg-[var(--wise-canvas-soft)] py-16 border-t border-[#c5edab] scroll-mt-24">
      <div className="landing-container">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-2 text-center">
          {isES ? "Contacto" : "Contact"}
        </p>
        <h2 className="text-[clamp(22px,4vw,28px)] font-medium text-[var(--wise-ink)] mb-2 tracking-tight text-center">
          {isES ? "Hablemos" : "Let's talk"}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-xl mx-auto mb-12 text-center">
          {isES
            ? "Listado retailer gratis abajo. Intelligence, Enterprise o alianzas — formulario general."
            : "Free retailer listing below. Intelligence, Enterprise, or partnerships — general form."}
        </p>

        <div id="contact-retailers" className="scroll-mt-24 mb-16">
          <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)] mb-3 text-center">
            {isES ? "Puerta B · Retailers" : "Door B · Retailers"}
          </p>
          <RetailerApplyForm />
        </div>

        <div id="contact-general" className="scroll-mt-24 border-t border-[#c5edab] pt-12">
          <ContactForm
            plan="enterprise"
            eyebrow={isES ? "General" : "General"}
            title={isES ? "¿Otra consulta o alianza?" : "Other inquiry or partnership?"}
            subtitle={
              isES
                ? "Intelligence, volumen Enterprise o prensa — le respondemos en 48 h."
                : "Intelligence, Enterprise volume, or press — we reply within 48 h."
            }
          />
        </div>
      </div>
    </section>
  );
}
