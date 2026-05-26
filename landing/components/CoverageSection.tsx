"use client";
import { useLang } from "@/lib/LanguageContext";

const lines = {
  supermercados: ["Wong PE", "Metro PE", "Plaza Vea PE", "Carrefour AR/BR", "Jumbo AR", "Vea AR", "Chedraui MX", "HEB MX", "Éxito CO", "Carulla CO", "Olímpica CO", "Sam's Club BR", "Mambo BR"],
  farmacias: ["Drogaria Pacheco BR", "Farmatodo MX", "Farmatodo CO", "Cruz Verde CO", "Cruz Verde CL"],
  electro: ["Motorola AR/BR/MX/CL/ES", "Electrolux AR/MX/CL", "Whirlpool AR/IT/FR", "Samsung BR/MX"],
  moda: ["C&A Brasil", "Hering Brasil", "Gymshark US", "Allbirds US", "ColourPop US", "Alo Yoga US", "Glossier US", "Fenty Beauty US", "Kylie Cosmetics US", "On Running CH"],
  hogar: ["Easy AR", "Promart PE", "Brooklinen US", "Parachute US", "Casper US"],
  departamentales: ["Coppel AR", "Ripley PE", "Falabella PE/CL/CO", "Paris CL", "Liverpool MX", "El Palacio MX"],
};

const countries = ["PE", "AR", "BR", "MX", "CO", "CL", "ES", "IT", "FR", "US", "CH"];

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
          {isES ? "60 retailers, 11 países, 6 líneas." : "60 retailers, 11 countries, 6 lines."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-md mx-auto mb-12">
          {isES ? "Un solo conector para supermercados, farmacias, electro, moda, hogar y tiendas por departamento en LatAm y Europa." : "A single connector for supermarkets, pharmacies, electronics, fashion, home, and department stores across LatAm and Europe."}
        </p>

        {/* Bullets */}
        <div className="flex flex-col sm:flex-row justify-center gap-4 text-xs text-[var(--wise-body)] mb-8">
          <span className="bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-lg px-4 py-2">
            {isES ? "Canasta básica · monitoreo de inflación · cross border" : "Basic basket · inflation tracking · cross border"}
          </span>
          <span className="bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-lg px-4 py-2">
            {isES ? "Datos estructurados: retailer, país, línea, moneda · BI-ready" : "Structured data: retailer, country, line, currency · BI-ready"}
          </span>
        </div>

        {/* Lines grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-left">
          {Object.entries(lines).map(([lineKey, stores]) => (
            <div key={lineKey} className="bg-[var(--wise-canvas-soft)] border border-[#c5edab] rounded-lg p-4">
              <h3 className="text-xs font-medium text-[var(--wise-ink)] mb-2 uppercase tracking-wider">{lineKey}</h3>
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
      </div>
    </section>
  );
}
