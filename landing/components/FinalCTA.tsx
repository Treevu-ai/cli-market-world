"use client";
import { useLang } from "@/lib/LanguageContext";
import ContactForm from "./ContactForm";

export default function FinalCTA() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section className="relative bg-[#e8ebe6] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <h2 className="text-[clamp(28px,4vw,40px)] leading-[1.1] font-black text-[#0e0f0c] mb-4 tracking-tight">
          {isES ? "Tu agente puede comprar solo.\nHoy." : "Your agent can buy on its own.\nToday."}
        </h2>
        <p className="text-sm text-[#454745] mb-10">pip install cli-market</p>
        <ContactForm initial="pro" />
      </div>
    </section>
  );
}
