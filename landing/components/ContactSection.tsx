"use client";

import { useLang } from "@/lib/LanguageContext";
import UnifiedContactForm from "@/components/UnifiedContactForm";

export default function ContactSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="contact" className="landing-section scroll-mt-24 animate-fade-in">
      <div className="landing-container-wide">
        <div className="landing-section-header">
          <p className="section-eyebrow mb-2">{isES ? "Contacto" : "Contact"}</p>
          <h2 className="section-title">{isES ? "Hablemos" : "Let's talk"}</h2>
          <p className="section-intro">
            {isES
              ? "Enterprise, retailers, prensa o consulta general — un solo formulario."
              : "Enterprise, retailers, press, or general inquiry — one form."}
          </p>
        </div>
        <div id="contact-general" className="scroll-mt-24">
          <UnifiedContactForm />
        </div>
        <div id="contact-retailers" className="scroll-mt-24 mt-12 text-center">
          <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4">
            {isES
              ? "¿Es retailer VTEX/Shopify? Formulario dedicado — listado gratis, sin letra chica."
              : "VTEX/Shopify retailer? Dedicated form — free listing."}
          </p>
          <a
            href="/retailers"
            className="inline-block border border-[var(--cm-mint)]/50 text-[var(--cm-mint)] font-semibold text-sm px-6 py-2 rounded-full hover:bg-[var(--cm-mint)]/10 transition-colors"
          >
            {isES ? "Aplicar como retailer →" : "Apply as retailer →"}
          </a>
        </div>
      </div>
    </section>
  );
}
