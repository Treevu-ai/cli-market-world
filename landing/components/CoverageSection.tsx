"use client";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";

const vtexLines = {
  supermercados: ["Carrefour AR/BR", "Jumbo AR", "Vea AR", "Chedraui MX", "HEB MX", "Exito CO", "Carulla CO", "Olimpica CO", "Sams Club BR", "Mambo BR", "Wong PE", "Metro PE", "Plaza Vea PE"],
  farmacias: ["Drogaria Pacheco BR", "Farmatodo MX", "Cruz Verde CO/CL"],
  electro: ["Motorola AR/BR/MX/CL", "Electrolux AR/CL", "Whirlpool AR/IT/FR", "Samsung"],
  moda: ["C&A Brasil", "Hering Brasil"],
  hogar: ["Easy AR", "Promart PE"],
  departamentales: ["Coppel AR"],
};

const magentoStores = ["Falabella PE/CL/CO", "Paris CL", "Ripley CL", "Liverpool MX", "El Palacio MX"];

export default function CoverageSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="coverage" className="relative bg-[var(--wise-canvas-soft)] py-20 border-t border-[#c5edab]">
      <div className="max-w-[900px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-[0.15em] mb-8">
          {isES ? "Cobertura" : "Coverage"}
        </p>
        <h2 className="text-[24px] font-medium text-[var(--wise-ink)] mb-3 tracking-tight">
          {isES
            ? `${MARKET_STATS.retailersDefined} retailers (${MARKET_STATS.retailersVerified} verificados), ${MARKET_STATS.countries} países, ${MARKET_STATS.businessLines} líneas.`
            : `${MARKET_STATS.retailersDefined} retailers (${MARKET_STATS.retailersVerified} verified), ${MARKET_STATS.countries} countries, ${MARKET_STATS.businessLines} lines.`}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-lg mx-auto mb-10">
          {isES ? MARKET_STATS.platformsPhraseEs : MARKET_STATS.platformsPhraseEn}
          {" · "}
          {isES ? "Sin scraping. APIs públicas y conectores unificados." : "No scraping. Public APIs and unified connectors."}
        </p>

        {/* Platform breakdown */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-10 text-left">
          {[
            { name: "VTEX", count: MARKET_STATS.platformVtex, note: isES ? "supermercados, electro, moda LatAm" : "supermarkets, electronics, LatAm fashion" },
            { name: "Shopify", count: MARKET_STATS.platformShopify, note: isES ? "moda & beauty global" : "global fashion & beauty" },
            { name: "Magento", count: MARKET_STATS.platformMagento, note: isES ? "departamentales multi-país" : "multi-country department stores" },
          ].map((p) => (
            <div key={p.name} className="bg-[var(--wise-canvas)] border border-[#c5edab] rounded-lg p-4">
              <p className="text-lg font-bold text-[var(--wise-ink)]">{p.name}</p>
              <p className="text-2xl font-black text-[var(--wise-green)] tabular-nums">{p.count}</p>
              <p className="text-[11px] text-[var(--wise-mute)] mt-1">{p.note}</p>
            </div>
          ))}
        </div>

        {/* VTEX lines */}
        <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)] mb-4 text-left">
          VTEX · {isES ? "por línea" : "by line"}
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-left mb-10">
          {Object.entries(vtexLines).map(([lineKey, stores]) => (
            <div key={lineKey} className="bg-[var(--wise-canvas-soft)] border border-[#c5edab] rounded-lg p-4">
              <h3 className="text-xs font-bold text-[var(--wise-ink)] mb-2 uppercase tracking-wider flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--wise-green)]" />
                {lineKey}
              </h3>
              <ul className="space-y-1">
                {stores.map((store) => (
                  <li key={store} className="text-[11px] text-[var(--wise-body)] leading-relaxed">{store}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Shopify fashion & beauty */}
        <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)] mb-4 text-left">
          Shopify · {isES ? "15 marcas moda & beauty" : "15 fashion & beauty brands"}
        </p>
        <div className="bg-[var(--wise-canvas)] border border-[#c5edab] rounded-lg p-5 text-left mb-10">
          <p className="text-xs text-[var(--wise-body)] mb-3 leading-relaxed">
            {isES
              ? "Marcas globales de moda, beauty y lifestyle — amplía el ICP más allá de supermercados LatAm."
              : "Global fashion, beauty, and lifestyle brands — expands ICP beyond LatAm supermarkets."}
          </p>
          <div className="flex flex-wrap gap-2">
            {MARKET_STATS.shopifyBrands.map((brand) => (
              <span
                key={brand}
                className="text-[10px] font-mono text-[var(--wise-body)] bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-full px-2.5 py-1"
              >
                {brand}
              </span>
            ))}
          </div>
        </div>

        {/* Magento */}
        <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)] mb-4 text-left">
          Magento · {MARKET_STATS.platformMagento} stores
        </p>
        <div className="flex flex-wrap gap-2 justify-start mb-8">
          {magentoStores.map((store) => (
            <span key={store} className="text-[10px] font-mono text-[var(--wise-body)] bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-full px-2.5 py-1">
              {store}
            </span>
          ))}
        </div>

        {/* Country tags */}
        <div className="flex flex-wrap justify-center gap-2">
          {MARKET_STATS.countryCodes.map((c) => (
            <span key={c} className="text-[10px] font-mono text-[var(--wise-body)] bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-full px-2.5 py-1">{c}</span>
          ))}
        </div>

        <p className="text-[10px] text-[var(--wise-mute)] mt-6 max-w-lg mx-auto leading-relaxed">
          {isES
            ? `${MARKET_STATS.retailersVerified} retailers verificados activos hoy. ${MARKET_STATS.retailersDefined - MARKET_STATS.retailersVerified} adicionales en catálogo (Magento token / Shopify onboarding).`
            : `${MARKET_STATS.retailersVerified} verified active retailers today. ${MARKET_STATS.retailersDefined - MARKET_STATS.retailersVerified} more in catalog (Magento token / Shopify onboarding).`}
        </p>
      </div>
    </section>
  );
}
