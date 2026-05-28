"use client";
import { useLang } from "@/lib/LanguageContext";

const lines = {
  supermercados: ["Carrefour AR/BR", "Jumbo AR", "Vea AR", "Chedraui MX", "HEB MX", "Exito CO", "Carulla CO", "Olimpica CO", "Sams Club BR", "Mambo BR", "Wong PE", "Metro PE", "Plaza Vea PE"],
  farmacias: ["Drogaria Pacheco BR", "Farmatodo MX"],
  electro: ["Motorola AR/BR/MX/CL", "Electrolux AR/CL", "Whirlpool AR/IT/FR"],
  moda: ["C&A Brasil", "Hering Brasil"],
  hogar: ["Easy AR", "Promart PE"],
  departamentales: ["Coppel AR", "Falabella PE/CL/CO", "Paris CL", "Ripley CL", "Liverpool MX", "El Palacio MX"],
};

const countries = ["PE", "AR", "BR", "MX", "CO", "CL", "IT", "FR", "US"];

export default function CoverageSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="coverage" className="relative bg-[var(--wise-canvas-soft)] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-[0.15em] mb-8">
          {isES ? "Cobertura" : "Coverage"}
        </p>
        <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-3 tracking-tight">
          {isES ? "41 retailers, 8 países, 6 líneas." : "41 retailers, 8 countries, 6 lines."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-md mx-auto mb-10">
          {isES ? "VTEX públicos funcionando hoy. Sin scraping. Sin tokens." : "Public VTEX stores working today. No scraping. No tokens."}
        </p>

        {/* Lines grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-left">
          {Object.entries(lines).map(([lineKey, stores]) => (
            <div key={lineKey} className="bg-[var(--wise-canvas-soft)] border border-[#c5edab] rounded-lg p-4">
              <h3 className="text-xs font-bold text-[var(--wise-ink)] mb-2 uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--wise-green)]"></span>
                {lineKey}
              </h3>
              <ul className="space-y-1">
                {stores.map((s) => (
                  <li key={s} className="text-[11px] text-[var(--wise-body)] leading-relaxed">{s}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Country tags */}
        <div className="mt-8 flex flex-wrap justify-center gap-2">
          {countries.map((c) => (
            <span key={c} className="text-[10px] font-mono text-[var(--wise-body)] bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-full px-2.5 py-1">{c}</span>
          ))}
        </div>

        {/* Note: Shopify/Magento stores need outreach */}
        <p className="text-[10px] text-[var(--wise-mute)] mt-6 max-w-md mx-auto leading-relaxed">
          {isES
            ? "+8 retailers adicionales en Magento requieren token de API. Gratis para ellos."
            : "+8 additional retailers on Magento need API tokens. Free for them."}
        </p>
      </div>
    </section>
  );
}
