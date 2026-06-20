"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { useLang } from "@/lib/LanguageContext";

export default function CinematicVision() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const section = sectionRef.current;
    const text = textRef.current;
    if (!section || !text) return;

    gsap.set(text, { opacity: 0, y: 40 });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            gsap.to(text, { opacity: 1, y: 0, duration: 1.2, ease: "power3.out" });
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.25 }
    );

    observer.observe(section);
    return () => observer.disconnect();
  }, []);

  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section
      id="cinematic"
      ref={sectionRef}
      className="landing-section"
      style={{ background: "#0a0a0a", position: "relative", zIndex: 2 }}
    >
      <div className="landing-container-wide">
        <div className="mb-6">
          <span className="text-[11px] font-mono uppercase tracking-[3px] text-[var(--cm-on-surface-variant)]/60">
            {isES ? "Infraestructura" : "Infrastructure"}
          </span>
        </div>
        <div className="mb-12 w-full h-px bg-white/10" />

        <div className="relative">
          <div
            className="relative overflow-hidden mx-auto"
            style={{ width: "100%", maxWidth: "80vw", aspectRatio: "21/9" }}
          >
            <video
              autoPlay
              muted
              loop
              playsInline
              className="w-full h-full object-cover"
              style={{ display: "block" }}
            >
              <source src="/cli-market-hero.webm" type="video/webm" />
              <source src="/cli-market-hero.mp4" type="video/mp4" />
            </video>
            <div
              className="absolute inset-0 pointer-events-none"
              style={{ background: "linear-gradient(to bottom, transparent 60%, #0a0a0a 100%)" }}
            />
          </div>

          <div
            ref={textRef}
            className="flex flex-col md:flex-row md:items-start mt-16 sm:mt-24 gap-8 md:gap-16"
          >
            <h2
              className="font-garamond m-0 text-white"
              style={{
                fontFamily: "var(--font-garamond), 'EB Garamond', Georgia, serif",
                fontWeight: 400,
                fontSize: "clamp(28px, 4vw, 60px)",
                lineHeight: 1.15,
                letterSpacing: "-1px",
                flex: "0 0 50%",
                textWrap: "balance",
              }}
            >
              {isES
                ? "Precios verificados. Sin scraping. Para agentes."
                : "Verified prices. Zero scraping. For agents."}
            </h2>
            <p
              className="m-0 text-[#dadada]"
              style={{
                fontFamily: "var(--font-inter), Inter, sans-serif",
                fontWeight: 200,
                fontSize: 17,
                lineHeight: 1.85,
                flex: "1 1 50%",
                textWrap: "pretty",
              }}
            >
              {isES
                ? "CLI Market normaliza precios por kg/L en 41 retailers de 8 países. Cada price point pasa por validación de calidad — sin valores atípicos, sin precios stale. Tu agente recibe datos limpios, listos para comparar canastas o disparar flujos de procurement."
                : "CLI Market normalizes prices per kg/L across 41 retailers in 8 countries. Every price point passes quality validation — no outliers, no stale data. Your agent gets clean data, ready to compare baskets or trigger procurement workflows."}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
