"use client";

import { useState, useEffect } from "react";
import { CheckSquare, Square, Send, Copy, Check, BadgeAlert, ArrowRight } from "lucide-react";
import { API_URL } from "@/lib/api";
import { useLang } from "@/lib/LanguageContext";

export default function ContactSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [interestType, setInterestType] = useState<"A" | "B" | "C">("A");

  const [category, setCategory] = useState(isES ? "Champú Natural / Cuidado Orgánico" : "Natural Shampoo / Organic Care");
  const [country, setCountry] = useState(isES ? "Perú (PE)" : "Peru (PE)");
  const [references, setReferences] = useState("EcoSavia, Capilar Mass, Organix Pure");

  const [sessionDate, setSessionDate] = useState("2026-07-20");
  const [clientProfile, setClientProfile] = useState(isES ? "Marca emprendedora de cosmética capilar peruana" : "Peruvian hair-care startup brand");

  const [moatCountry, setMoatCountry] = useState(isES ? "Colombia (CO)" : "Colombia (CO)");
  const [moatLine, setMoatLine] = useState(isES ? "Línea Higiene / Cuidado de Hogar" : "Personal Care / Household line");
  const [cadence, setCadence] = useState(isES ? "Semanal (Radar de Góndola)" : "Weekly (Shelf Radar)");

  const [copiedText, setCopiedText] = useState(false);

  const [userName, setUserName] = useState("");
  const [userEmail, setUserEmail] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [userMessage, setUserMessage] = useState("");
  const [isMessageEdited, setIsMessageEdited] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({
    1: true,
    2: false,
    3: false,
  });

  const toggleCheck = (id: number) => {
    setCheckedItems((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const generateMessageText = () => {
    if (!isES) {
      let msg = "Hi CLI Market team,\n\n";
      if (interestType === "A") {
        msg += "I'm interested in scheduling a **Pack A Demo (Client Brief)** for one of my active clients.\n\n";
        msg += "**Request details:**\n";
        msg += `* **Category:** ${category}\n`;
        msg += `* **Country:** ${country}\n`;
        msg += `* **Anchor products / references:** ${references}\n\n`;
        msg += "Please confirm you have active collector coverage to run the comparison and share the shelf-evidence markdown.";
      } else if (interestType === "B") {
        msg += "I'm interested in scheduling a **live Assisted Advisory Session (Pack B)**.\n\n";
        msg += "**Session details:**\n";
        msg += `* **Suggested date:** ${sessionDate}\n`;
        msg += `* **End-client profile (no confidential data):** ${clientProfile}\n\n`;
        msg += "I'd like to walk through the CLI Market console live to resolve pricing and channel questions during our advisory meeting.";
      } else {
        msg += "I'd like information on the **Monthly Intelligence Retainer (Pack C)** for ongoing research.\n\n";
        msg += "**Suggested pilot subscription details:**\n";
        msg += `* **Country of interest:** ${moatCountry}\n`;
        msg += `* **Retail line or channel:** ${moatLine}\n`;
        msg += `* **Executive report cadence:** ${cadence}\n\n`;
        msg += "I'd like to start the 30-day pilot to automate the signal radar and data series feeding our dashboard.";
      }
      return msg;
    }

    let msg = "Hola equipo de CLI Market,\n\n";
    if (interestType === "A") {
      msg += "Estoy interesado en coordinar un **Demo de Pack A (Brief de Cliente)** para uno de mis clientes activos.\n\n";
      msg += "**Detalles de la solicitud:**\n";
      msg += `* **Categoría:** ${category}\n`;
      msg += `* **País:** ${country}\n`;
      msg += `* **Productos / Referencias ancla:** ${references}\n\n`;
      msg += "Por favor, confírmenme si tienen cobertura del collect activa para correr la comparativa y coordinar la entrega del Markdown de evidencia de góndola.";
    } else if (interestType === "B") {
      msg += "Estoy interesado en programar una **Sesión de Asesoría Asistida en vivo (Pack B)**.\n\n";
      msg += "**Detalles de la sesión:**\n";
      msg += `* **Fecha sugerida:** ${sessionDate}\n`;
      msg += `* **Perfil del cliente final (sin datos confidenciales):** ${clientProfile}\n\n`;
      msg += "Quisiera revisar cómo podemos operar la consola de CLI Market en vivo para resolver las hipótesis de precios y plaza ante mi cliente durante nuestra reunión de consultoría.";
    } else {
      msg += "Quisiera solicitar información sobre el **Retainer de Inteligencia Mensual (Pack C)** para estructurar un research continuo.\n\n";
      msg += "**Detalles de la suscripción piloto sugerida:**\n";
      msg += `* **País de interés:** ${moatCountry}\n`;
      msg += `* **Línea o canal de retail:** ${moatLine}\n`;
      msg += `* **Cadencia del reporte ejecutivo:** ${cadence}\n\n`;
      msg += "Me gustaría activar el piloto de 30 días para automatizar el radar de señales y la serie de datos para alimentar nuestro dashboard.";
    }
    return msg;
  };

  useEffect(() => {
    if (!isMessageEdited) {
      setUserMessage(generateMessageText());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [interestType, category, country, references, sessionDate, clientProfile, moatCountry, moatLine, cadence, isMessageEdited, isES]);

  const handleCopyMessage = () => {
    navigator.clipboard.writeText(userMessage);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userName.trim() || !userEmail.trim() || !companyName.trim() || !userMessage.trim()) {
      alert(isES
        ? "Por favor, completa todos los campos del formulario (Nombre, Correo, Empresa y Mensaje)."
        : "Please fill in all form fields (Name, Email, Company, and Message).");
      return;
    }

    setLoading(true);

    const subject = encodeURIComponent(`Contacto CLI Market - ${companyName}`);
    const body = encodeURIComponent(
      `Nombre: ${userName}\n` +
      `Email: ${userEmail}\n` +
      `Empresa: ${companyName}\n\n` +
      `Mensaje:\n${userMessage}`
    );

    try {
      const res = await fetch(`${API_URL}/v1/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan: "advisor",
          name: userName,
          email: userEmail,
          profile: companyName,
          use_case: userMessage,
          lang: isES ? "es" : "en",
        }),
      });

      if (res.ok) {
        setIsSubmitted(true);
        return;
      }
      throw new Error("Server error");
    } catch {
      window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${body}`;
      setIsSubmitted(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section id="contact-form" className="landing-section scroll-mt-24">
      <div className="landing-container-wide">
      <div className="landing-section-header text-center">
        <p className="section-eyebrow mb-4">
          {isES ? "Acceso y demo" : "Access and demo"}
        </p>
        <h2 className="section-title">
          {isES ? "Súmate al ecosistema de asesores" : "Join the advisor ecosystem"}
        </h2>
        <p className="section-intro">
          {isES
            ? "Canal cerrado: no competimos contigo ni vendemos de forma directa a las marcas que asesoras."
            : "Closed channel: we don't compete with you or sell directly to the brands you advise."}
        </p>
      </div>

      <div className="grid lg:grid-cols-12 gap-8 items-start mt-10">
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-[var(--cm-surface)] rounded-2xl border border-[var(--cm-outline-variant)] p-6 shadow-xs">
            <span className="text-[10px] font-mono font-bold tracking-widest text-[var(--cm-mint)] uppercase block mb-1">
              {isES ? "Oferta de entrada" : "Starter offer"}
            </span>
            <h3 className="text-xl font-display font-bold text-[var(--cm-on-surface)] mb-4">
              {isES ? "Oferta de entrada (esta semana)" : "Starter offer (this week)"}
            </h3>

            <p className="text-xs text-[var(--cm-text-secondary)] mb-4">
              {isES
                ? "Sigue esta ruta de 3 pasos para probar la plataforma sin compromiso:"
                : "Follow this 3-step path to try the platform with no commitment:"}
            </p>

            <div className="space-y-3.5">
              {[1, 2, 3].map((id) => (
                <button
                  key={id}
                  onClick={() => toggleCheck(id)}
                  className="w-full flex items-start gap-3 p-3 rounded-lg hover:bg-[var(--cm-surface-high)] border border-transparent hover:border-[var(--cm-hairline-soft)] transition-all text-left"
                >
                  {checkedItems[id] ? (
                    <CheckSquare className="w-5 h-5 text-[var(--cm-on-surface)] shrink-0 mt-0.5" />
                  ) : (
                    <Square className="w-5 h-5 text-[var(--cm-outline-variant)] shrink-0 mt-0.5" />
                  )}
                  <div>
                    <span className="text-xs font-mono font-bold text-[var(--cm-text-secondary)] block uppercase">
                      {isES ? `Paso ${id}` : `Step ${id}`}
                    </span>
                    <span className="text-sm font-semibold text-[var(--cm-on-surface)]">
                      {id === 1
                        ? isES ? "Elegir 1 caso del asesor" : "Pick 1 advisor case"
                        : id === 2
                          ? isES ? "Correr Pack A gratis" : "Run Pack A for free"
                          : isES ? "Coordinar Pack B o Pack C" : "Schedule Pack B or Pack C"}
                    </span>
                    <p className="text-xs text-[var(--cm-text-secondary)] mt-0.5">
                      {id === 1
                        ? isES
                          ? "Identifica una categoría real y un país clave de un cliente actual."
                          : "Identify a real category and a key country from a current client."
                        : id === 2
                          ? isES
                            ? "Te regalamos un piloto corto de Brief para que sientas el impacto de los hechos."
                            : "We give you a short Brief pilot so you can feel the impact of the data firsthand."
                          : isES
                            ? "Si hay fit con el cliente final, avanzas a la consultoría recurrente."
                            : "If it fits the end client, you move into a recurring engagement."}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-[var(--cm-surface-high)] rounded-2xl border border-[var(--cm-outline-variant)] p-6">
            <h4 className="text-sm font-mono uppercase tracking-wider text-[var(--cm-text-secondary)] mb-3 block">
              {isES ? "Sectores prioritarios (ciclo 1)" : "Priority sectors (cycle 1)"}
            </h4>
            <div className="space-y-2.5 text-xs text-[var(--cm-on-surface-variant)]">
              {(isES
                ? [
                    { label: "Asesores de", strong: "Inteligencia de Mercados", rest: "y análisis" },
                    { label: "Asesores de", strong: "Marketing y Estrategia", rest: "(pricing / lanzamiento)" },
                    { label: "Asesores", strong: "Empresariales / Incubadoras", rest: "(UX simple y 4P)" },
                  ]
                : [
                    { label: "", strong: "Market intelligence", rest: "advisors and analysts" },
                    { label: "", strong: "Marketing and strategy", rest: "advisors (pricing / launch)" },
                    { label: "", strong: "Business / incubator", rest: "advisors (simple UX & 4Ps)" },
                  ]
              ).map((item) => (
                <div key={item.strong} className="p-2.5 rounded bg-[var(--cm-surface)] border border-[var(--cm-hairline-soft)] flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--cm-on-surface)]" />
                  <span>
                    {item.label ? `${item.label} ` : ""}
                    <strong>{item.strong}</strong> {item.rest}
                  </span>
                </div>
              ))}
            </div>
            <div className="mt-4 p-3 bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/15 rounded-lg text-[10px] text-[var(--cm-action-deep)] flex items-start gap-1.5">
              <BadgeAlert className="w-3.5 h-3.5 shrink-0 mt-0.5" />
              <span>
                <em>{isES ? "Minimarkets o tienditas:" : "Corner stores / minimarkets:"}</em>{" "}
                {isES
                  ? "se sugiere abordarlos de forma indirecta como caso vía distribuidores o retailers aliados, no como usuario directo de la CLI."
                  : "best approached indirectly as a case via distributors or partner retailers, not as a direct CLI user."}
              </span>
            </div>
          </div>
        </div>

        <div className="lg:col-span-7">
          {isSubmitted ? (
            <div className="bg-[var(--cm-surface)] rounded-2xl border border-[var(--cm-outline-variant)] p-8 shadow-xs text-center flex flex-col items-center justify-center min-h-[500px]">
              <div className="w-16 h-16 bg-[var(--cm-action-soft)] text-[var(--cm-mint)] rounded-full flex items-center justify-center mb-6 border border-[var(--cm-mint)]/20">
                <Check className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold text-[var(--cm-on-surface)] mb-3">
                {isES ? "¡Formulario enviado!" : "Form sent!"}
              </h3>
              <p className="text-[var(--cm-on-surface-variant)] text-sm max-w-md mb-6 leading-relaxed">
                {isES ? "Recibimos tu mensaje en " : "We received your message at "}
                <strong className="text-[var(--cm-mint)] font-semibold">hello@cli-market.dev</strong>.{" "}
                {isES ? "Te responderemos a la brevedad." : "We'll reply shortly."}
              </p>

              <div className="bg-[var(--cm-surface-high)] rounded-xl p-4 border border-[var(--cm-outline-variant)] text-left w-full max-w-md mb-6">
                <p className="text-[10px] font-bold text-[var(--cm-text-secondary)] uppercase tracking-widest mb-2">
                  {isES ? "Resumen del contacto" : "Contact summary"}
                </p>
                <div className="text-xs space-y-1.5 text-[var(--cm-on-surface-variant)]">
                  <p><strong>{isES ? "Nombre:" : "Name:"}</strong> {userName}</p>
                  <p><strong>{isES ? "Correo electrónico:" : "Email:"}</strong> {userEmail}</p>
                  <p><strong>{isES ? "Empresa:" : "Company:"}</strong> {companyName}</p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 w-full max-w-md">
                <button
                  type="button"
                  onClick={() => {
                    const subject = encodeURIComponent(`Contacto CLI Market - ${companyName}`);
                    const body = encodeURIComponent(
                      `Nombre: ${userName}\n` +
                      `Email: ${userEmail}\n` +
                      `Empresa: ${companyName}\n\n` +
                      `Mensaje:\n${userMessage}`
                    );
                    window.location.href = `mailto:hello@cli-market.dev?subject=${subject}&body=${body}`;
                  }}
                  className="flex-1 py-2.5 bg-[var(--cm-mint)] hover:bg-[var(--cm-action-deep)] text-[var(--cm-on-mint)] text-xs font-bold rounded-lg transition-all shadow-md cursor-pointer text-center"
                >
                  {isES ? "Reabrir correo" : "Reopen email"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsSubmitted(false);
                    setUserName("");
                    setUserEmail("");
                    setCompanyName("");
                    setIsMessageEdited(false);
                  }}
                  className="flex-1 py-2.5 bg-[var(--cm-surface)] hover:bg-[var(--cm-surface-high)] text-[var(--cm-on-surface-variant)] border border-[var(--cm-outline-variant)] text-xs font-bold rounded-lg transition-all cursor-pointer text-center"
                >
                  {isES ? "Enviar otro mensaje" : "Send another message"}
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="bg-[var(--cm-surface)] rounded-2xl border border-[var(--cm-outline-variant)] p-6 sm:p-8 shadow-xs">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-[var(--cm-hairline-soft)]">
                <div className="p-2 bg-[var(--cm-action-soft)] text-[var(--cm-mint)] rounded-lg">
                  <Send className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xl font-display font-bold text-[var(--cm-on-surface)]">
                    {isES ? "Formulario de contacto directo" : "Direct contact form"}
                  </h3>
                  <p className="text-xs text-[var(--cm-text-secondary)]">
                    {isES
                      ? "Ingresa tus datos y personaliza el mensaje para hello@cli-market.dev"
                      : "Enter your details and customize the message to hello@cli-market.dev"}
                  </p>
                </div>
              </div>

              <div className="space-y-4 mb-6 pb-6 border-b border-[var(--cm-hairline-soft)]">
                <p className="text-[10px] font-mono font-bold tracking-widest text-[var(--cm-text-secondary)] uppercase">
                  {isES ? "1. Tus datos de contacto" : "1. Your contact details"}
                </p>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                      {isES ? "Nombre" : "Name"} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      required
                      value={userName}
                      onChange={(e) => setUserName(e.target.value)}
                      className="w-full text-sm bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg p-2.5 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                      placeholder={isES ? "Ej. Sofía Rodríguez" : "e.g. Sofia Rodriguez"}
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                      {isES ? "Correo electrónico" : "Email"} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="email"
                      required
                      value={userEmail}
                      onChange={(e) => setUserEmail(e.target.value)}
                      className="w-full text-sm bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg p-2.5 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                      placeholder="sofia@empresa.com"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                    {isES ? "Nombre de la empresa o consultora" : "Company or consultancy name"} <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full text-sm bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg p-2.5 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                    placeholder={isES ? "Ej. Consultora LATAM Retail o Independiente" : "e.g. LATAM Retail Consulting, or Independent"}
                  />
                </div>
                <div className="flex items-start gap-2.5 pt-1.5">
                  <input
                    type="checkbox"
                    required
                    defaultChecked
                    className="mt-1 w-4 h-4 accent-[var(--cm-mint)] rounded border-[var(--cm-outline-variant)] focus:ring-[var(--cm-mint)] cursor-pointer shrink-0"
                  />
                  <span className="text-[11px] text-[var(--cm-text-secondary)] leading-normal">
                    {isES ? (
                      <>
                        Declaro que soy consultor independiente, mentor de negocios o firma de asesoría corporativa.
                        Entiendo que <strong className="text-[var(--cm-on-surface-variant)]">CLI Market es un canal cerrado</strong> y no otorga licencias directas a marcas de retail, para no competir con los asesores.{" "}
                        <span className="text-red-500">*</span>
                      </>
                    ) : (
                      <>
                        I confirm I&apos;m an independent consultant, business mentor, or corporate advisory firm.
                        I understand <strong className="text-[var(--cm-on-surface-variant)]">CLI Market is a closed channel</strong> and does not license directly to retail brands, so it doesn&apos;t compete with advisors.{" "}
                        <span className="text-red-500">*</span>
                      </>
                    )}
                  </span>
                </div>
              </div>

              <div className="space-y-4 mb-6">
                <div className="flex items-center justify-between">
                  <p className="text-[10px] font-mono font-bold tracking-widest text-[var(--cm-text-secondary)] uppercase">
                    {isES ? "2. Configurar propuesta de caso (opcional)" : "2. Configure a case proposal (optional)"}
                  </p>
                  <span className="text-[10px] bg-[var(--cm-action-soft)] text-[var(--cm-action-deep)] font-bold px-2 py-0.5 rounded-full font-sans">
                    {isES ? "Pre-llena el mensaje" : "Pre-fills the message"}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2.5 bg-[var(--cm-surface-high)] p-1 rounded-xl border border-[var(--cm-outline-variant)]/60">
                  {(["A", "B", "C"] as const).map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setInterestType(t)}
                      className={`py-2 px-2 rounded-lg text-xs font-bold text-center transition-all cursor-pointer ${
                        interestType === t
                          ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)] shadow-sm"
                          : "text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)]"
                      }`}
                    >
                      {isES ? "Pack" : "Pack"} {t} {t === "A" ? (isES ? "(Brief)" : "(Brief)") : t === "B" ? (isES ? "(Sesión)" : "(Session)") : (isES ? "(Retainer)" : "(Retainer)")}
                    </button>
                  ))}
                </div>

                <div className="space-y-4 bg-[var(--cm-surface-high)]/50 p-4 rounded-xl border border-[var(--cm-hairline-soft)]">
                  {interestType === "A" && (
                    <>
                      <div className="grid sm:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                            {isES ? "Categoría real del cliente" : "Client's real category"}
                          </label>
                          <input
                            type="text"
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full text-xs bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                            placeholder={isES ? "Ej. Champú Natural" : "e.g. Natural Shampoo"}
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                            {isES ? "País de análisis" : "Country of analysis"}
                          </label>
                          <input
                            type="text"
                            value={country}
                            onChange={(e) => setCountry(e.target.value)}
                            className="w-full text-xs bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                            placeholder={isES ? "Ej. Perú (PE)" : "e.g. Peru (PE)"}
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                          {isES ? "3–5 marcas o referencias ancla sugeridas" : "3–5 suggested anchor brands or references"}
                        </label>
                        <input
                          type="text"
                          value={references}
                          onChange={(e) => setReferences(e.target.value)}
                          className="w-full text-xs bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                          placeholder={isES ? "Ej. Marca Premium, Marca Mass" : "e.g. Premium Brand, Mass Brand"}
                        />
                      </div>
                    </>
                  )}

                  {interestType === "B" && (
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                          {isES ? "Fecha sugerida para la sesión" : "Suggested session date"}
                        </label>
                        <input
                          type="date"
                          value={sessionDate}
                          onChange={(e) => setSessionDate(e.target.value)}
                          className="w-full text-xs bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                          {isES ? "Perfil general del cliente final" : "End client's general profile"}
                        </label>
                        <input
                          type="text"
                          value={clientProfile}
                          onChange={(e) => setClientProfile(e.target.value)}
                          className="w-full text-xs bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                          placeholder={isES ? "Ej. Distribuidor de lácteos en Lima" : "e.g. Dairy distributor in Lima"}
                        />
                      </div>
                    </div>
                  )}

                  {interestType === "C" && (
                    <div className="grid sm:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                          {isES ? "País del moat" : "Moat country"}
                        </label>
                        <input
                          type="text"
                          value={moatCountry}
                          onChange={(e) => setMoatCountry(e.target.value)}
                          className="w-full text-xs bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                          placeholder={isES ? "Ej. México" : "e.g. Mexico"}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                          {isES ? "Línea de retail" : "Retail line"}
                        </label>
                        <input
                          type="text"
                          value={moatLine}
                          onChange={(e) => setMoatLine(e.target.value)}
                          className="w-full text-xs bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                          placeholder={isES ? "Ej. Supermercados" : "e.g. Supermarkets"}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)] mb-1">
                          {isES ? "Cadencia de alertas" : "Alert cadence"}
                        </label>
                        <select
                          value={cadence}
                          onChange={(e) => setCadence(e.target.value)}
                          className="w-full text-xs bg-[var(--cm-surface)] border border-[var(--cm-outline-variant)] rounded-lg p-2 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] transition-colors"
                        >
                          <option value={isES ? "Semanal (Radar de Góndola)" : "Weekly (Shelf Radar)"}>
                            {isES ? "Semanal (Radar)" : "Weekly (Radar)"}
                          </option>
                          <option value={isES ? "Mensual (Brief Ejecutivo)" : "Monthly (Executive Brief)"}>
                            {isES ? "Mensual (Brief)" : "Monthly (Brief)"}
                          </option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-2 mb-6">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-semibold text-[var(--cm-on-surface-variant)]">
                    {isES ? "3. Área de mensaje / propuesta" : "3. Message / proposal area"} <span className="text-red-500">*</span>
                  </label>
                  <button
                    type="button"
                    onClick={handleCopyMessage}
                    className="flex items-center gap-1 text-[10px] text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors cursor-pointer"
                  >
                    {copiedText ? (
                      <>
                        <Check className="w-3 h-3 text-[var(--cm-mint)]" />
                        <span className="text-[var(--cm-mint)] font-bold">{isES ? "¡Copiado!" : "Copied!"}</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>{isES ? "Copiar texto" : "Copy text"}</span>
                      </>
                    )}
                  </button>
                </div>

                <textarea
                  required
                  rows={5}
                  value={userMessage}
                  onChange={(e) => {
                    setUserMessage(e.target.value);
                    setIsMessageEdited(true);
                  }}
                  className="w-full text-sm bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg p-3 outline-none focus:ring-1 focus:ring-[var(--cm-mint)] focus:border-[var(--cm-mint)] font-sans leading-relaxed transition-colors resize-y min-h-[120px]"
                  placeholder={isES ? "Escribe tu mensaje aquí..." : "Write your message here..."}
                />
              </div>

              <div className="mt-6 flex flex-col sm:flex-row items-center gap-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-mint w-full sm:w-auto gap-2"
                >
                  <span>{loading ? (isES ? "Enviando..." : "Sending...") : (isES ? "Enviar formulario" : "Send form")}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <div className="text-center sm:text-left text-xs text-[var(--cm-text-secondary)] font-sans">
                  {isES ? "El formulario enviará los datos directamente a " : "The form will send your details directly to "}
                  <a href="mailto:hello@cli-market.dev" className="text-[var(--cm-mint)] hover:underline font-bold">
                    hello@cli-market.dev
                  </a>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>
      </div>
    </section>
  );
}
