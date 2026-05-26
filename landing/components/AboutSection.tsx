"use client";
import { useLang } from "@/lib/LanguageContext";

export default function AboutSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="about" className="relative bg-[#0e0f0c] py-24">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#868685] font-medium uppercase tracking-[0.15em] mb-8">
          {isES ? "Sobre nosotros" : "About us"}
        </p>
        <h2 className="text-[clamp(32px,5vw,48px)] leading-[1.1] font-black text-[#9fe870] mb-6 tracking-tight">
          {isES ? "Construido en Lima.\nPara el mundo." : "Built in Lima.\nFor the world."}
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
              <h3 className="text-lg font-bold text-[#0e0f0c]">Antonio Cuba</h3>
              <p className="text-sm text-[#454745]">
                Founder & Product Owner · CLI Market
              </p>
              <p className="text-sm text-[#454745]">
                {isES ? "Gerente General · SINAPSIS INNOVADORA S.A.C." : "General Manager · SINAPSIS INNOVADORA S.A.C."}
              </p>
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

