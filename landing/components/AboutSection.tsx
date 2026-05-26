"use client";
import { useLang } from "@/lib/LanguageContext";

export default function AboutSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="about" className="relative bg-[#0e0f0c] py-24">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#454745] font-medium uppercase tracking-[0.15em] mb-8">
          {isES ? "Sobre nosotros" : "About us"}
        </p>
        <h2 className="text-[clamp(32px,5vw,48px)] leading-[1.1] font-black text-[#9fe870] mb-6 tracking-tight">
          {isES ? "Construido en Perú.\nPara el mundo." : "Built in Peru.\nFor the world."}
        </h2>
        <p className="text-base text-[#c5edab] max-w-lg mx-auto mb-12 leading-relaxed">
          {isES
            ? "CLI Market nace de una convicción simple: el comercio minorista en Latinoamérica necesita infraestructura programable. No otro marketplace. No otro agregador. Una capa de software que permita a cualquier agente de IA buscar, comparar y comprar en el retail físico como si fuera una API."
            : "CLI Market was born from a simple conviction: Latin American retail needs programmable infrastructure. Not another marketplace. Not another aggregator. A software layer that lets any AI agent search, compare, and buy from physical retail as if it were an API."}
        </p>

        {/* Founder card */}
        <div className="bg-[#e2f6d5] rounded-3xl p-8 text-left max-w-[480px] mx-auto">
          <div className="flex items-start gap-4 mb-4">
            <div className="w-12 h-12 rounded-full bg-[#0e0f0c] flex items-center justify-center shrink-0">
              <span className="text-[#9fe870] text-lg font-black">A</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="text-lg font-bold text-[#0e0f0c]">Antonio Cuba</h3>
                <svg width="18" height="18" viewBox="0 0 22 22" fill="#1d9bf0" aria-label="Verified">
                  <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.706-1.443 1.248-.355.54-.553 1.17-.57 1.814.018.645.216 1.273.57 1.814.356.54.856.97 1.444 1.242-.224.607-.274 1.263-.144 1.894.13.633.436 1.22.882 1.692.47.445 1.053.75 1.687.882.633.13 1.29.08 1.9-.14.27.586.702 1.084 1.24 1.438.54.355 1.168.55 1.815.568.646-.018 1.273-.216 1.814-.57.543-.354.974-.852 1.245-1.44.608.22 1.26.27 1.89.14.633-.13 1.22-.436 1.692-.882.446-.47.75-1.055.88-1.688.13-.634.085-1.293-.14-1.896.586-.274 1.084-.706 1.44-1.248.355-.54.55-1.17.567-1.814zM9.78 15.67l-3.39-3.39 1.41-1.41 1.98 1.98 4.6-4.6 1.41 1.41-6.01 6.01z"/>
                </svg>
              </div>
              <p className="text-sm text-[#454745]">
                Founder & Product Owner · CLI Market
              </p>
              <p className="text-sm text-[#454745]">
                {isES ? "Gerente General · SINAPSIS INNOVADORA S.A.C." : "General Manager · SINAPSIS INNOVADORA S.A.C."}
              </p>
              <div className="flex items-center gap-4 mt-2">
                <a href="https://instagram.com/cli.market" target="_blank" rel="noopener"
                   className="inline-flex items-center gap-1.5 text-xs text-[#454745] hover:text-[#0e0f0c] transition-colors">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
                  </svg>
                  Instagram
                </a>
                <a href="https://www.linkedin.com/company/cli-market/" target="_blank" rel="noopener"
                   className="inline-flex items-center gap-1.5 text-xs text-[#454745] hover:text-[#0e0f0c] transition-colors">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                  LinkedIn
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Contact CTA */}
        <div className="mt-10">
          <a href="#contact"
             className="inline-flex items-center gap-2 rounded-3xl bg-[#9fe870] text-[#0e0f0c] text-base font-semibold px-8 py-3.5 hover:bg-[#cdffad] transition-colors">
            {isES ? "Trabajemos juntos" : "Let's work together"}
            <span className="opacity-60">→</span>
          </a>
        </div>
      </div>
    </section>
  );
}

