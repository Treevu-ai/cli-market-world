"use client";
import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";

const PLANS = [
  { key: "free", es: "Free", en: "Free", price: "$0" },
  { key: "pro", es: "Pro", en: "Pro", price: "$29/mes" },
  { key: "enterprise", es: "Enterprise", en: "Enterprise", price: "Custom" },
];

export default function ContactForm({ initial = "pro" }: { initial?: string }) {
  const { lang } = useLang();
  const [plan, setPlan] = useState(initial);
  const [email, setEmail] = useState("");
  const [useCase, setUseCase] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const tt = (es: string, en: string) => (lang === "es" ? es : en);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !useCase) { setError(tt("Completa todos los campos", "Fill all fields")); return; }
    setLoading(true); setError("");
    try {
      await fetch("https://cli-market-api.onrender.com/v1/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan, email, use_case: useCase }),
      });
      setSent(true);
    } catch {
      setSent(true); // fallback
    }
    setLoading(false);
  };

  if (sent) {
    return (
      <div className="bg-[#131313] border border-[#3cffd0]/30 p-8 text-center flex flex-col items-center gap-4">
        <span className="text-3xl">{tt("✅", "✅")}</span>
        <h3 className="font-grotesk text-xl font-bold text-white">{tt("Mensaje recibido", "Message received")}</h3>
        <p className="font-mono text-sm text-[#888] max-w-[400px]">{tt("Nos pondremos en contacto en menos de 24 horas.", "We will get back to you within 24 hours.")}</p>
        <p className="font-mono text-[10px] text-[#555]">{tt("— Equipo CLI Market", "— CLI Market team")}</p>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="bg-[#131313] border border-[#2d2d2d] p-6 flex flex-col gap-4">
      <h3 className="font-grotesk text-lg font-bold text-white">{tt("Solicita acceso", "Request access")}</h3>

      <div>
        <label className="font-mono text-[10px] text-[#555] uppercase tracking-wider mb-2 block">{tt("Plan", "Plan")}</label>
        <div className="grid grid-cols-3 gap-2">
          {PLANS.map((p) => (
            <button key={p.key} type="button" onClick={() => setPlan(p.key)}
              className={`font-mono text-[11px] py-2 px-3 border text-center transition-all ${plan === p.key ? "border-[#3cffd0] text-[#3cffd0] bg-[#3cffd0]/5" : "border-[#2d2d2d] text-[#555] hover:border-[#333]"}`}>
              <div>{lang === "es" ? p.es : p.en}</div><div className="text-[9px] opacity-60">{p.price}</div>
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="font-mono text-[10px] text-[#555] uppercase tracking-wider mb-2 block">Email</label>
        <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
          placeholder={tt("tu@email.com", "you@email.com")}
          className="w-full bg-[#1a1a1a] border border-[#2d2d2d] px-4 py-2 font-mono text-sm text-white placeholder:text-[#444] focus:border-[#3cffd0]/40 focus:outline-none" />
      </div>

      <div>
        <label className="font-mono text-[10px] text-[#555] uppercase tracking-wider mb-2 block">{tt("Caso de uso", "Use case")}</label>
        <textarea required value={useCase} onChange={(e) => setUseCase(e.target.value)}
          placeholder={tt("Ej: comparar canasta basica entre Peru y Argentina para mi app.", "E.g. compare basic basket prices between Peru and Argentina for my app.")}
          rows={3} className="w-full bg-[#1a1a1a] border border-[#2d2d2d] px-4 py-2 font-mono text-sm text-white placeholder:text-[#444] focus:border-[#3cffd0]/40 focus:outline-none resize-none" />
      </div>

      {error && <p className="font-mono text-[11px] text-[#FF6B35]">{error}</p>}

      <button type="submit" disabled={loading}
        className="bg-[#3cffd0] text-black font-bold px-6 py-3 font-mono text-sm uppercase tracking-widest hover:bg-[#309875] transition-colors disabled:opacity-50">
        {loading ? "..." : tt("Enviar solicitud", "Send request")}
      </button>
    </form>
  );
}
