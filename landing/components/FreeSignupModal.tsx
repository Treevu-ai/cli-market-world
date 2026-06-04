"use client";
import { useEffect, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";

const PYPI_URL = "https://pypi.org/project/cli-market/";

type Profile = "dev" | "business" | "other";

const PROFILES = [
  {
    id: "dev" as Profile,
    emoji: "⚡",
    label_es: "Developer / Builder",
    label_en: "Developer / Builder",
    desc_es: "Integro la API o MCP en un agente o app",
    desc_en: "Integrating the API or MCP into an agent or app",
  },
  {
    id: "business" as Profile,
    emoji: "📊",
    label_es: "Negocio / Equipo comercial",
    label_en: "Business / Commercial team",
    desc_es: "Analizo precios para decisiones comerciales",
    desc_en: "Analyzing prices for commercial decisions",
  },
  {
    id: "other" as Profile,
    emoji: "🔍",
    label_es: "Explorar / Investigar",
    label_en: "Exploring / Researching",
    desc_es: "Quiero conocer el producto",
    desc_en: "Checking out the product",
  },
];

export default function FreeSignupModal({
  open,
  onClose,
  plan = "free",
}: {
  open: boolean;
  onClose: () => void;
  plan?: string;
}) {
  const { lang } = useLang();
  const isES = lang === "es";

  const [step, setStep] = useState<1 | 2>(1);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [legal, setLegal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (open) {
      setStep(1);
      setProfile(null);
      setEmail("");
      setName("");
      setCompany("");
      setLegal(false);
      setLoading(false);
      setDone(false);
      setError("");
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!legal) {
      setError(isES ? "Debes aceptar los términos para continuar." : "You must accept the terms to continue.");
      return;
    }
    setLoading(true);
    setError("");

    const useCaseParts = [
      profile ? `profile=${profile}` : "",
      name ? `name=${name}` : "",
      company ? `company=${company}` : "",
    ].filter(Boolean);

    try {
      await fetch(`${API_URL}/v1/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan,
          profile,
          email,
          name: name || undefined,
          company: company || undefined,
          use_case: useCaseParts.join(" · "),
          lang: isES ? "es" : "en",
        }),
      });
    } catch {
      // Never block the user on network failure
    }

    setDone(true);
    if (plan === "free") {
      setTimeout(() => {
        onClose();
        window.open(PYPI_URL, "_blank", "noopener,noreferrer");
      }, 1400);
    }
  };

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="card-cyber w-full max-w-md p-6 sm:p-8 relative animate-fade-in">
        <button
          onClick={onClose}
          aria-label={isES ? "Cerrar" : "Close"}
          className="absolute top-4 right-4 text-[var(--cm-on-surface-variant)] hover:text-white transition-colors text-lg leading-none"
        >
          ✕
        </button>

        {done ? (
          <div className="text-center py-8 space-y-3">
            <p className="text-3xl">✅</p>
            <p className="text-lg font-semibold text-white">
              {isES ? "¡Listo!" : "All set!"}
            </p>
            <p className="text-sm text-[var(--cm-on-surface-variant)]">
              {plan === "free"
                ? isES ? "Redirigiendo a PyPI…" : "Redirecting to PyPI…"
                : isES ? "Te escribiremos pronto con el acceso de prueba." : "We'll reach out shortly with your trial access."}
            </p>
            {plan !== "free" && (
              <button onClick={onClose} className="btn-mint mt-4">
                {isES ? "Cerrar" : "Close"}
              </button>
            )}
          </div>
        ) : step === 1 ? (
          <>
            <div className="mb-6 text-center">
              <p className="section-eyebrow text-[var(--cm-mint)] mb-2">{plan.charAt(0).toUpperCase() + plan.slice(1)}</p>
              <h3 className="text-lg font-bold text-white">
                {isES ? "¿Cómo usarás CLI Market?" : "How will you use CLI Market?"}
              </h3>
              <p className="text-sm text-[var(--cm-on-surface-variant)] mt-1">
                {isES
                  ? "Nos ayuda a darte la mejor experiencia."
                  : "Helps us give you the best experience."}
              </p>
            </div>
            <div className="space-y-3">
              {PROFILES.map((p) => (
                <button
                  key={p.id}
                  onClick={() => { setProfile(p.id); setStep(2); }}
                  className="w-full text-left rounded-xl border border-[var(--cm-outline-variant)]/40 hover:border-[var(--cm-mint)]/60 hover:bg-white/5 transition-all p-4"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl shrink-0">{p.emoji}</span>
                    <div>
                      <p className="text-sm font-semibold text-white">
                        {isES ? p.label_es : p.label_en}
                      </p>
                      <p className="text-xs text-[var(--cm-on-surface-variant)] mt-0.5">
                        {isES ? p.desc_es : p.desc_en}
                      </p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </>
        ) : (
          <form onSubmit={submit} className="space-y-4">
            <div>
              <button
                type="button"
                onClick={() => setStep(1)}
                className="text-xs text-[var(--cm-on-surface-variant)] hover:text-white flex items-center gap-1 mb-5 transition-colors"
              >
                ← {isES ? "Volver" : "Back"}
              </button>
              <p className="section-eyebrow text-[var(--cm-mint)] mb-1">{plan.charAt(0).toUpperCase() + plan.slice(1)}</p>
              <h3 className="text-lg font-bold text-white">
                {isES ? "Casi listo" : "Almost there"}
              </h3>
              {profile && (
                <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
                  {PROFILES.find((p) => p.id === profile)?.[isES ? "label_es" : "label_en"]}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-1">
                Email *
              </label>
              <input
                type="email"
                required
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-cyber"
                placeholder="tu@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-white mb-1">
                {isES ? "Nombre" : "Name"}{" "}
                <span className="text-[var(--cm-on-surface-variant)] font-normal">
                  ({isES ? "opcional" : "optional"})
                </span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input-cyber"
                placeholder={isES ? "Tu nombre" : "Your name"}
              />
            </div>

            {profile === "business" && (
              <div>
                <label className="block text-sm font-medium text-white mb-1">
                  {isES ? "Empresa / Rol" : "Company / Role"}{" "}
                  <span className="text-[var(--cm-on-surface-variant)] font-normal">
                    ({isES ? "opcional" : "optional"})
                  </span>
                </label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="input-cyber"
                  placeholder={
                    isES
                      ? "Ej. Gerente de Pricing, Retail S.A."
                      : "e.g. Pricing Manager, Retail Co."
                  }
                />
              </div>
            )}

            <label className="flex items-start gap-3 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={legal}
                onChange={(e) => setLegal(e.target.checked)}
                required
                className="mt-0.5 accent-[var(--cm-mint)] shrink-0"
              />
              <span className="text-sm text-[var(--cm-on-surface-variant)]">
                {isES ? (
                  <>
                    Acepto los{" "}
                    <a
                      href="/legal/tos"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[var(--cm-mint)] hover:underline"
                    >
                      Términos de Servicio
                    </a>{" "}
                    y la{" "}
                    <a
                      href="/legal/privacy"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[var(--cm-mint)] hover:underline"
                    >
                      Política de Privacidad
                    </a>
                    .
                  </>
                ) : (
                  <>
                    I agree to the{" "}
                    <a
                      href="/legal/tos"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[var(--cm-mint)] hover:underline"
                    >
                      Terms of Service
                    </a>{" "}
                    and{" "}
                    <a
                      href="/legal/privacy"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[var(--cm-mint)] hover:underline"
                    >
                      Privacy Policy
                    </a>
                    .
                  </>
                )}
              </span>
            </label>

            {error && (
              <p className="text-sm text-[#ffb4ab]">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading || !legal}
              className="btn-mint w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading
                ? isES ? "Procesando…" : "Processing…"
                : plan === "free"
                  ? isES ? "Continuar a PyPI →" : "Continue to PyPI →"
                  : isES ? "Solicitar acceso de prueba →" : "Request trial access →"}
            </button>

            <p className="text-xs text-center text-[var(--cm-on-surface-variant)]/60">
              {plan === "free"
                ? isES ? "Gratuito para siempre · MIT · Sin tarjeta de crédito" : "Free forever · MIT · No credit card required"
                : isES ? "14 días gratis · Sin tarjeta de crédito" : "14-day free trial · No credit card required"}
            </p>
          </form>
        )}
      </div>
    </div>
  );
}
