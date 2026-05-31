"use client";

import { useLang } from "@/lib/LanguageContext";
import ContactForm from "@/components/ContactForm";
import RetailerApplyForm from "@/components/RetailerApplyForm";

export default function ContactSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="contact" className="landing-section scroll-mt-24 animate-fade-in">
      <div className="landing-container-wide">
        <p className="section-eyebrow mb-2 text-center">{isES ? "Contacto" : "Contact"}</p>
        <h2 className="section-title mb-2 text-center">{isES ? "Hablemos" : "Let's talk"}</h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-xl mx-auto mb-12 text-center">
          {isES
            ? "Listado retailer gratis abajo. Intelligence, Enterprise o alianzas — formulario general."
            : "Free retailer listing below. Intelligence, Enterprise, or partnerships — general form."}
        </p>

        <div id="contact-retailers" className="scroll-mt-24 mb-16">
          <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-3 text-center">
            {isES ? "Puerta B · Retailers" : "Door B · Retailers"}
          </p>
          <RetailerApplyForm />
        </div>

        <div id="contact-general" className="scroll-mt-24 border-t border-[var(--cm-outline-variant)]/30 pt-12">
          <ContactForm
            plan="enterprise"
            eyebrow={isES ? "General" : "General"}
            title={isES ? "¿Otra consulta o alianza?" : "Other inquiry or partnership?"}
            subtitle={
              isES
                ? "Intelligence, volumen Enterprise o prensa — le respondemos en menos de 30 min."
                : "Intelligence, Enterprise volume, or press — we reply within 30 min."
            }
          />
        </div>
      </div>
    </section>
  );
}
