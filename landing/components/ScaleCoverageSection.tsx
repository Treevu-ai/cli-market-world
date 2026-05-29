"use client";

import { useEffect, useRef } from "react";
import { motion, useInView, useSpring, useTransform } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import { MARKET_STATS } from "@/lib/marketStats";
import { useLiveStats, refreshLabel } from "@/hooks/useLiveStats";
import { API_URL } from "@/lib/api";

const vtexLines = {
  supermercados: ["Carrefour AR/BR", "Jumbo AR", "Vea AR", "Chedraui MX", "HEB MX", "Exito CO", "Carulla CO", "Olimpica CO", "Sams Club BR", "Mambo BR", "Wong PE", "Metro PE", "Plaza Vea PE"],
  farmacias: ["Drogaria Pacheco BR", "Farmatodo MX", "Cruz Verde CO/CL"],
  electro: ["Motorola AR/BR/MX/CL", "Electrolux AR/CL", "Whirlpool AR/IT/FR", "Samsung"],
  moda: ["C&A Brasil", "Hering Brasil"],
};

const magentoStores = ["Falabella PE/CL/CO", "Paris CL", "Ripley CL", "Liverpool MX", "El Palacio MX"];

function Counter({ end, label, delay }: { end: number; label: string; delay: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "0px 0px -80px 0px" });
  const spring = useSpring(0, { stiffness: 60, damping: 20 });
  const display = useTransform(spring, (v) => Math.round(v).toLocaleString());

  useEffect(() => {
    if (inView) {
      const timer = setTimeout(() => spring.set(end), delay);
      return () => clearTimeout(timer);
    }
  }, [inView, end, delay, spring]);

  return (
    <div className="flex flex-col items-center gap-1">
      <motion.span ref={ref} className="text-[28px] font-medium text-[var(--wise-ink)] tracking-tight tabular-nums">{display}</motion.span>
      <span className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-widest text-center">{label}</span>
    </div>
  );
}

export default function ScaleCoverageSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const { priceLong, priceChip, stats, retailersVerified, retailersDefined } = useLiveStats();

  const scaleStats = [
    { end: retailersDefined, label: isES ? "retailers catálogo" : "retailers in catalog" },
    { end: retailersVerified, label: isES ? "verificados activos" : "verified active" },
    { end: MARKET_STATS.countries, label: isES ? "países" : "countries" },
    { end: MARKET_STATS.platforms, label: isES ? "plataformas" : "platforms" },
  ];

  return (
    <section id="coverage" className="relative bg-[var(--wise-canvas-soft)] py-16 border-t border-[#c5edab]">
      <div className="landing-container px-6 text-center">
        <p className="text-xs text-[var(--wise-body)] font-mono uppercase tracking-[0.15em] mb-4">
          {isES ? "Escala y cobertura" : "Scale and coverage"}
        </p>
        <h2 className="text-[clamp(22px,4vw,28px)] font-medium text-[var(--wise-ink)] mb-2 tracking-tight">
          {isES
            ? `${retailersDefined} retailers · ${retailersVerified} verificados · ${MARKET_STATS.countries} países`
            : `${retailersDefined} retailers · ${retailersVerified} verified · ${MARKET_STATS.countries} countries`}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-2xl mx-auto mb-8">
          {isES ? MARKET_STATS.platformsPhraseEs : MARKET_STATS.platformsPhraseEn}
          {" · "}
          <span className="tabular-nums">{priceLong}</span> {isES ? "precios verificados" : "verified prices"}
          {" · "}
          {refreshLabel(isES)}
        </p>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {scaleStats.map((s, i) => (
            <Counter key={s.label} end={s.end} label={s.label} delay={i * 100} />
          ))}
        </div>

        {/* Data moat snapshot — canonical labels only */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12 text-left">
          <div className="bg-[var(--wise-canvas)] border border-[#c5edab] rounded-2xl p-5">
            <p className="text-[10px] uppercase tracking-widest text-[var(--wise-mute)] mb-1">
              {isES ? "Inventario" : "Inventory"}
            </p>
            <p className="text-3xl font-black text-[var(--wise-ink)] tabular-nums">{priceLong}</p>
            <p className="text-xs text-[var(--wise-mute)] mt-1">
              {isES ? "precios indexados · normalizados kg/L" : "indexed prices · kg/L normalized"}
            </p>
          </div>
          <div className="bg-[var(--wise-canvas)] border border-[#c5edab] rounded-2xl p-5">
            <p className="text-[10px] uppercase tracking-widest text-[var(--wise-mute)] mb-1">
              {isES ? "Frescura" : "Freshness"}
            </p>
            <p className="text-3xl font-black text-[var(--wise-ink)] tabular-nums">
              {stats.snapshots24h != null ? stats.snapshots24h.toLocaleString() : "—"}
            </p>
            <p className="text-xs text-[var(--wise-mute)] mt-1">
              {isES ? `snapshots 24h · collector ${refreshLabel(isES)}` : `24h snapshots · collector ${refreshLabel(isES)}`}
            </p>
          </div>
          <div className="bg-[var(--wise-canvas)] border border-[#c5edab] rounded-2xl p-5">
            <p className="text-[10px] uppercase tracking-widest text-[var(--wise-mute)] mb-1">
              {isES ? "Retailers" : "Retailers"}
            </p>
            <p className="text-3xl font-black text-[var(--wise-ink)] tabular-nums">{retailersVerified}</p>
            <p className="text-xs text-[var(--wise-mute)] mt-1">
              {isES
                ? `verificados activos (${retailersDefined} en catálogo)`
                : `verified active (${retailersDefined} in catalog)`}
            </p>
          </div>
        </div>

        {/* Platforms */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-10 text-left">
          {[
            { name: "VTEX", count: MARKET_STATS.platformVtex, note: isES ? "supermercados, electro, moda LatAm" : "supermarkets, electronics, LatAm fashion" },
            { name: "Shopify", count: MARKET_STATS.platformShopify, note: isES ? "moda & beauty global" : "global fashion & beauty" },
            { name: "Magento", count: MARKET_STATS.platformMagento, note: isES ? "departamentales" : "department stores" },
          ].map((p) => (
            <div key={p.name} className="bg-[var(--wise-canvas)] border border-[#c5edab] rounded-lg p-4">
              <p className="text-lg font-bold text-[var(--wise-ink)]">{p.name}</p>
              <p className="text-2xl font-black text-[var(--wise-ink)] tabular-nums">{p.count}</p>
              <p className="text-[11px] text-[var(--wise-mute)] mt-1">{p.note}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-left mb-8">
          <div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)] mb-3">VTEX</p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(vtexLines).map(([line, stores]) => (
                <div key={line} className="bg-[var(--wise-canvas)] border border-[#c5edab] rounded-lg p-3">
                  <h3 className="text-[10px] font-bold uppercase text-[var(--wise-ink)] mb-1">{line}</h3>
                  <p className="text-[10px] text-[var(--wise-body)] leading-relaxed">{stores.slice(0, 4).join(" · ")}{stores.length > 4 ? "…" : ""}</p>
                </div>
              ))}
            </div>
          </div>
          <div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)] mb-3">
              Shopify · {isES ? "marcas moda & beauty" : "fashion & beauty brands"}
            </p>
            <div className="flex flex-wrap gap-2 mb-4">
              {MARKET_STATS.shopifyBrands.map((brand) => (
                <span key={brand} className="text-[10px] font-mono text-[var(--wise-body)] bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-full px-2.5 py-1">
                  {brand}
                </span>
              ))}
            </div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-[var(--wise-mute)] mb-2">Magento</p>
            <div className="flex flex-wrap gap-2">
              {magentoStores.map((store) => (
                <span key={store} className="text-[10px] font-mono text-[var(--wise-body)] bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-full px-2.5 py-1">
                  {store}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="flex flex-wrap justify-center gap-2 mb-6">
          {MARKET_STATS.countryCodes.map((c) => (
            <span key={c} className="text-[10px] font-mono text-[var(--wise-body)] bg-[var(--wise-green-pale)] border border-[#c5edab] rounded-full px-2.5 py-1">{c}</span>
          ))}
        </div>

        <a
          href={`${API_URL}/dashboard`}
          target="_blank"
          rel="noopener"
          className="inline-flex items-center gap-2 rounded-3xl bg-[var(--wise-green)] text-[var(--wise-ink)] text-sm font-semibold px-6 py-3 hover:bg-[var(--wise-green-hover)] transition-colors"
        >
          {isES ? "Ver dashboard en vivo" : "View live dashboard"}
          <span className="opacity-60 tabular-nums">({priceChip})</span>
        </a>
      </div>
    </section>
  );
}
