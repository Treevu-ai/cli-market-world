"use client";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import UnifiedContactForm from "@/components/UnifiedContactForm";
import { useLang } from "@/lib/LanguageContext";

export default function ContactPage() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <main className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />
      <div className="relative z-10 pt-24 pb-16">
        <section id="contact" className="landing-section scroll-mt-24">
          <div className="landing-container-wide">
            <div className="landing-section-header">
              <p className="section-eyebrow mb-2">{isES ? "Contacto" : "Contact"}</p>
              <h1 className="section-title">{isES ? "Hablemos" : "Let's talk"}</h1>
              <p className="section-intro">
                {isES
                  ? "Intelligence, Procure, enterprise, retailers o consulta general — un solo formulario."
                  : "Intelligence, Procure, enterprise, retailers, or general inquiry — one form."}
              </p>
            </div>
            <div id="contact-general" className="scroll-mt-24">
              <UnifiedContactForm />
            </div>
            <div className="scroll-mt-24 mt-12 text-center">
              <p className="text-sm text-[var(--cm-on-surface-variant)] mb-4">
                {isES
                  ? "¿Es retailer VTEX, Shopify, Magento o WooCommerce? Formulario dedicado — listado gratis, sin letra chica."
                  : "VTEX, Shopify, Magento, or WooCommerce retailer? Dedicated form — free listing."}
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
        <Footer />
      </div>
    </main>
  );
}
