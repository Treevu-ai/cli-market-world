"use client";

import { useLang } from "@/lib/LanguageContext";
import RetailerApplyForm from "@/components/RetailerApplyForm";
import UnifiedContactForm from "@/components/UnifiedContactForm";

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
            ? "Listado retailer gratis abajo. Enterprise, prensa o consulta general — formulario unificado."
            : "Free retailer listing below. Enterprise, press, or general inquiry — unified form."}
        </p>

        {/* Door B — Retailers */}
        <div id="contact-retailers" className="scroll-mt-24 mb-16">
          <p className="font-label-caps text-[var(--cm-on-surface-variant)]/60 mb-3 text-center">
            {isES ? "Puerta B · Retailers" : "Door B · Retailers"}
          </p>
          <RetailerApplyForm />
        </div>

        {/* Unified contact form */}
        <div id="contact-general" className="scroll-mt-24 border-t border-[var(--cm-outline-variant)]/30 pt-12">
          <UnifiedContactForm />
        </div>
      </div>
    </section>
  );
}
