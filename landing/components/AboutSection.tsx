"use client";
import { useLang } from "@/lib/LanguageContext";

export default function AboutSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="about" className="relative bg-[var(--wise-ink)] py-16">
      <div className="landing-container text-center">
        <p className="text-xs text-[var(--wise-green)] font-medium uppercase tracking-[0.15em] mb-8">
          {isES ? "Sobre nosotros" : "About us"}
        </p>
        <h2 className="text-[clamp(32px,5vw,48px)] leading-[1.1] font-black text-[#9fe870] mb-6 tracking-tight">
          {isES ? <>Construido en Perú.<br />Para el mundo.</> : <>Built in Peru.<br />For the world.</>}
        </h2>
        <p className="text-base text-[#e2f6d5] max-w-lg mx-auto mb-12 leading-relaxed">
          {isES
            ? "CLI Market nace de una convicción simple: el comercio minorista en Latinoamérica necesita infraestructura programable. No otro marketplace. No otro agregador. Una capa de software que permita a cualquier agente de IA buscar, comparar y comprar en el retail físico como si fuera una API."
            : "CLI Market was born from a simple conviction: Latin American retail needs programmable infrastructure. Not another marketplace. Not another aggregator. A software layer that lets any AI agent search, compare, and buy from physical retail as if it were an API."}
        </p>

        {/* Founder card */}
        <div className="bg-[var(--wise-green-pale)] rounded-3xl p-6 sm:p-8 w-full max-w-md mx-auto min-w-0 overflow-hidden">
          <div className="flex flex-col items-center sm:flex-row sm:items-start gap-4 sm:gap-5">
            <img
              src="/grok-image-b03d62b8-7a6d-4610-82f0-1475243924d3.png"
              alt="Antonio Cuba, founder de CLI Market"
              className="w-16 h-16 sm:w-14 sm:h-14 rounded-full object-cover shrink-0 ring-2 ring-white/80"
            />
            <div className="min-w-0 w-full text-center sm:text-left">
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-x-1.5 gap-y-1">
                <h3 className="text-lg font-bold text-[var(--wise-ink)] leading-tight">Antonio Cuba</h3>
                <svg width="18" height="18" viewBox="0 0 22 22" fill="#1d9bf0" aria-hidden="true" className="shrink-0">
                  <title>Verified</title>
                  <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.706-1.443 1.248-.355.54-.553 1.17-.57 1.814.018.645.216 1.273.57 1.814.356.54.856.97 1.444 1.242-.224.607-.274 1.263-.144 1.894.13.633.436 1.22.882 1.692.47.445 1.053.75 1.687.882.633.13 1.29.08 1.9-.14.27.586.702 1.084 1.24 1.438.54.355 1.168.55 1.815.568.646-.018 1.273-.216 1.814-.57.543-.354.974-.852 1.245-1.44.608.22 1.26.27 1.89.14.633-.13 1.22-.436 1.692-.882.446-.47.75-1.055.88-1.688.13-.634.085-1.293-.14-1.896.586-.274 1.084-.706 1.44-1.248.355-.54.55-1.17.567-1.814zM9.78 15.67l-3.39-3.39 1.41-1.41 1.98 1.98 4.6-4.6 1.41 1.41-6.01 6.01z"/>
                </svg>
              </div>
              <p className="mt-1 text-sm text-[var(--wise-body)] leading-snug">
                Founder &amp; Product Owner · CLI Market
              </p>
              <p className="mt-0.5 text-sm text-[var(--wise-body)] leading-snug break-words">
                {isES ? "Gerente General · SINAPSIS INNOVADORA S.A.C." : "General Manager · SINAPSIS INNOVADORA S.A.C."}
              </p>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[#c5edab]/60 flex flex-col sm:flex-row sm:flex-wrap gap-2 sm:gap-3">
            <a
              href="https://instagram.com/cli.market"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex w-full sm:w-auto items-center justify-center sm:justify-start gap-2 rounded-full bg-white/60 px-4 py-2 text-xs font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] hover:bg-white transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
              </svg>
              Instagram
            </a>
            <a
              href="https://x.com/cli_market_dev"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex w-full sm:w-auto items-center justify-center sm:justify-start gap-2 rounded-full bg-white/60 px-4 py-2 text-xs font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] hover:bg-white transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
              </svg>
              X / Twitter
            </a>
            <a
              href="https://www.linkedin.com/company/cli-market/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex w-full sm:w-auto items-center justify-center sm:justify-start gap-2 rounded-full bg-white/60 px-4 py-2 text-xs font-medium text-[var(--wise-body)] hover:text-[var(--wise-ink)] hover:bg-white transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
              LinkedIn
            </a>
          </div>
        </div>

        {/* Contact CTA */}
        <div className="mt-10">
          <a href="#contact"
             className="inline-flex items-center gap-2 rounded-3xl bg-[#9fe870] text-[var(--wise-ink)] text-base font-semibold px-8 py-3.5 hover:bg-[#cdffad] transition-colors">
            {isES ? "Trabajemos juntos" : "Let's work together"}
            <span className="opacity-60">→</span>
          </a>
        </div>
      </div>
    </section>
  );
}

