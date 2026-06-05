"use client";

import { useLang } from "@/lib/LanguageContext";
import UnifiedContactForm from "@/components/UnifiedContactForm";

export default function ContactSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="contact" className="landing-section scroll-mt-24 animate-fade-in">
      <div className="landing-container-wide">
        <p className="section-eyebrow mb-2 text-center">{isES ? "Contacto" : "Contact"}</p>
        <h2 className="section-title mb-2 text-center">{isES ? "Hablemos" : "Let's talk"}</h2>
        <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-xl mx-auto mb-10 text-center">
          {isES
            ? "Enterprise, retailers, prensa o consulta general — un solo formulario."
            : "Enterprise, retailers, press, or general inquiry — one form."}
        </p>
        <div id="contact-general" className="scroll-mt-24">
          <UnifiedContactForm />
        </div>
        <div id="contact-retailers" className="scroll-mt-24" />
      </div>
    </section>
  );
}
