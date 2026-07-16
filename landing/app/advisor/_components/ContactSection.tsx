"use client";

import { useState, useEffect } from "react";
import { CheckSquare, Square, Send, Copy, Check, BadgeAlert, ArrowRight } from "lucide-react";
import { API_URL } from "@/lib/api";
import { useLang } from "@/lib/LanguageContext";

export default function ContactSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [interestType, setInterestType] = useState<"A" | "B" | "C">("A");

  const [category, setCategory] = useState("Champú Natural / Cuidado Orgánico");
  const [country, setCountry] = useState("Perú (PE)");
  const [references, setReferences] = useState("EcoSavia, Capilar Mass, Organix Pure");

  const [sessionDate, setSessionDate] = useState("2026-07-20");
  const [clientProfile, setClientProfile] = useState("Marca emprendedora de cosmética capilar peruana");

  const [moatCountry, setMoatCountry] = useState("Colombia (CO)");
  const [moatLine, setMoatLine] = useState("Línea Higiene / Cuidado de Hogar");
  const [cadence, setCadence] = useState("Semanal (Radar de Góndola)");

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
  }, [interestType, category, country, references, sessionDate, clientProfile, moatCountry, moatLine, cadence, isMessageEdited]);

  const handleCopyMessage = () => {
    navigator.clipboard.writeText(userMessage);
    setCopiedText(true);
    setTimeout(() => setCopiedText(false), 2000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userName.trim() || !userEmail.trim() || !companyName.trim() || !userMessage.trim()) {
      alert("Por favor, completa todos los campos del formulario (Nombre, Correo, Empresa y Mensaje).");
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
    <section id="contact-form" className="mb-16 scroll-mt-24">
      <div className="text-center mb-10">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-50 border border-emerald-100 text-emerald-800 uppercase tracking-widest mb-3">
          ACCESO Y DEMO EXCLUSIVA
        </span>
        <h2 className="text-3xl font-display font-bold text-slate-900 tracking-tight mb-2">
          Aplica al Ecosistema Exclusivo de Asesores
        </h2>
        <p className="text-slate-600 max-w-2xl mx-auto">
          Garantizamos canal cerrado: no competimos contigo ni vendemos de forma directa a las marcas que asesoras.
        </p>
      </div>

      <div className="grid lg:grid-cols-12 gap-8 items-start">
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
            <span className="text-[10px] font-mono font-bold tracking-widest text-emerald-700 uppercase block mb-1">Oferta Exclusiva</span>
            <h3 className="text-xl font-display font-bold text-slate-900 mb-4">
              Oferta de Entrada (Esta Semana)
            </h3>

            <p className="text-xs text-slate-500 mb-4">
              Sigue esta ruta ágil de 3 pasos para probar la plataforma sin compromisos financieros:
            </p>

            <div className="space-y-3.5">
              {[1, 2, 3].map((id) => (
                <button
                  key={id}
                  onClick={() => toggleCheck(id)}
                  className="w-full flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-all text-left"
                >
                  {checkedItems[id] ? (
                    <CheckSquare className="w-5 h-5 text-slate-900 shrink-0 mt-0.5" />
                  ) : (
                    <Square className="w-5 h-5 text-slate-300 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <span className="text-xs font-mono font-bold text-slate-400 block uppercase">Paso {id}</span>
                    <span className="text-sm font-semibold text-slate-900">
                      {id === 1 ? "Elegir 1 caso del asesor" : id === 2 ? "Correr Pack A gratis" : "Coordinar Pack B o Pack C"}
                    </span>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {id === 1
                        ? "Identifica una categoría real y un país clave de un cliente actual."
                        : id === 2
                          ? "Te regalamos un piloto corto de Brief para que sientas el impacto de los hechos."
                          : "Si hay fit con el cliente final, avanzas a la consultoría recurrente."}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="bg-slate-50 rounded-2xl border border-slate-200 p-6">
            <h4 className="text-sm font-mono uppercase tracking-wider text-slate-400 mb-3 block">
              Sectores Prioritarios (Ciclo 1)
            </h4>
            <div className="space-y-2.5 text-xs text-slate-600">
              {[
                "Asesores de Inteligencia de Mercados y análisis",
                "Asesores de Marketing y Estrategia (Pricing / Lanzamiento)",
                "Asesores Empresariales / Incubadoras (UX Simple & 4P)",
              ].map((label) => (
                <div key={label} className="p-2.5 rounded bg-white border border-slate-200/60 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-slate-900" />
                  <span dangerouslySetInnerHTML={{ __html: label.replace(/(Inteligencia de Mercados|Marketing y Estrategia|Empresariales \/ Incubadoras)/, "<strong>$1</strong>") }} />
                </div>
              ))}
            </div>
            <div className="mt-4 p-3 bg-emerald-50 border border-emerald-100/60 rounded-lg text-[10px] text-emerald-950 flex items-start gap-1.5">
              <BadgeAlert className="w-3.5 h-3.5 text-emerald-800 shrink-0 mt-0.5" />
              <span><em>Minimarkets o tienditas:</em> Se sugiere abordar de forma indirecta como caso a través de distribuidores o retailers aliados, no como usuario directo de la CLI.</span>
            </div>
          </div>
        </div>

        <div className="lg:col-span-7">
          {isSubmitted ? (
            <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs text-center flex flex-col items-center justify-center min-h-[500px]">
              <div className="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mb-6 border border-emerald-100">
                <Check className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-bold text-slate-900 mb-3">¡Formulario Enviado!</h3>
              <p className="text-slate-600 text-sm max-w-md mb-6 leading-relaxed">
                Hemos recibido tu mensaje en <strong className="text-emerald-700 font-semibold">hello@cli-market.dev</strong>. Te responderemos a la brevedad.
              </p>

              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-left w-full max-w-md mb-6">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Resumen del contacto</p>
                <div className="text-xs space-y-1.5 text-slate-700">
                  <p><strong>Nombre:</strong> {userName}</p>
                  <p><strong>Correo electrónico:</strong> {userEmail}</p>
                  <p><strong>Nombre de la empresa:</strong> {companyName}</p>
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
                  className="flex-1 py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white text-xs font-bold rounded-lg transition-all shadow-md shadow-emerald-100 cursor-pointer text-center"
                >
                  Reabrir Correo
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
                  className="flex-1 py-2.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-bold rounded-lg transition-all cursor-pointer text-center"
                >
                  Enviar Otro Mensaje
                </button>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs">
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-slate-100">
                <div className="p-2 bg-emerald-50 text-emerald-700 rounded-lg">
                  <Send className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xl font-display font-bold text-slate-900">
                    Formulario de Contacto Directo
                  </h3>
                  <p className="text-xs text-slate-500">
                    Ingresa tus datos y personaliza el mensaje de interés para hello@cli-market.dev
                  </p>
                </div>
              </div>

              <div className="space-y-4 mb-6 pb-6 border-b border-slate-100">
                <p className="text-[10px] font-mono font-bold tracking-widest text-slate-400 uppercase">1. Tus Datos de Contacto</p>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Nombre <span className="text-red-500">*</span></label>
                    <input
                      type="text"
                      required
                      value={userName}
                      onChange={(e) => setUserName(e.target.value)}
                      className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                      placeholder="Ej. Sofía Rodríguez"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 mb-1">Correo Electrónico <span className="text-red-500">*</span></label>
                    <input
                      type="email"
                      required
                      value={userEmail}
                      onChange={(e) => setUserEmail(e.target.value)}
                      className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                      placeholder="sofia@empresa.com"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Nombre de la Empresa o Consultora <span className="text-red-500">*</span></label>
                  <input
                    type="text"
                    required
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-2.5 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                    placeholder="Ej. Consultora LATAM Retail o Independiente"
                  />
                </div>
                <div className="flex items-start gap-2.5 pt-1.5">
                  <input
                    type="checkbox"
                    required
                    defaultChecked
                    className="mt-1 w-4 h-4 accent-emerald-700 rounded text-emerald-700 border-slate-300 focus:ring-emerald-500 cursor-pointer shrink-0"
                  />
                  <span className="text-[11px] text-slate-500 leading-normal">
                    Declaro que soy consultor independiente, mentor de negocios o firma de asesoría corporativa. Entiendo que <strong className="text-slate-800">CLI Market es un ecosistema tecnológico de canal cerrado</strong> y no otorga licencias directas a marcas de retail para blindar el mercado y evitar la desintermediación de los asesores. <span className="text-red-500">*</span>
                  </span>
                </div>
              </div>

              <div className="space-y-4 mb-6">
                <div className="flex items-center justify-between">
                  <p className="text-[10px] font-mono font-bold tracking-widest text-slate-400 uppercase">2. Configurar Propuesta de Caso (Opcional)</p>
                  <span className="text-[10px] bg-emerald-50 text-emerald-800 font-bold px-2 py-0.5 rounded-full font-sans">Pre-llena el mensaje</span>
                </div>

                <div className="grid grid-cols-3 gap-2.5 bg-slate-50 p-1 rounded-xl border border-slate-200/60">
                  {(["A", "B", "C"] as const).map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setInterestType(t)}
                      className={`py-2 px-2 rounded-lg text-xs font-bold text-center transition-all cursor-pointer ${
                        interestType === t
                          ? "bg-emerald-700 text-white shadow-sm"
                          : "text-slate-600 hover:text-slate-900"
                      }`}
                    >
                      Pack {t} {t === "A" ? "(Brief)" : t === "B" ? "(Sesión)" : "(Retainer)"}
                    </button>
                  ))}
                </div>

                <div className="space-y-4 bg-slate-50/50 p-4 rounded-xl border border-slate-100">
                  {interestType === "A" && (
                    <>
                      <div className="grid sm:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-xs font-semibold text-slate-600 mb-1">Categoría real del cliente</label>
                          <input
                            type="text"
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                            placeholder="Ej. Champú Natural"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-slate-600 mb-1">País de análisis</label>
                          <input
                            type="text"
                            value={country}
                            onChange={(e) => setCountry(e.target.value)}
                            className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                            placeholder="Ej. Perú (PE)"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">3-5 Marcas o referencias ancla sugeridas</label>
                        <input
                          type="text"
                          value={references}
                          onChange={(e) => setReferences(e.target.value)}
                          className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                          placeholder="Ej. Marca Premium, Marca Mass"
                        />
                      </div>
                    </>
                  )}

                  {interestType === "B" && (
                    <div className="grid sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">Fecha sugerida para la sesión</label>
                        <input
                          type="date"
                          value={sessionDate}
                          onChange={(e) => setSessionDate(e.target.value)}
                          className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">Perfil general del cliente final</label>
                        <input
                          type="text"
                          value={clientProfile}
                          onChange={(e) => setClientProfile(e.target.value)}
                          className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                          placeholder="Ej. Distribuidor de lácteos en Lima"
                        />
                      </div>
                    </div>
                  )}

                  {interestType === "C" && (
                    <div className="grid sm:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">País del Moat</label>
                        <input
                          type="text"
                          value={moatCountry}
                          onChange={(e) => setMoatCountry(e.target.value)}
                          className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                          placeholder="Ej. México"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">Línea de retail</label>
                        <input
                          type="text"
                          value={moatLine}
                          onChange={(e) => setMoatLine(e.target.value)}
                          className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                          placeholder="Ej. Supermercados"
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-semibold text-slate-600 mb-1">Cadencia de alertas</label>
                        <select
                          value={cadence}
                          onChange={(e) => setCadence(e.target.value)}
                          className="w-full text-xs bg-white border border-slate-200 rounded-lg p-2 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 transition-colors"
                        >
                          <option value="Semanal (Radar de Góndola)">Semanal (Radar)</option>
                          <option value="Mensual (Brief Ejecutivo)">Mensual (Brief)</option>
                        </select>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-2 mb-6">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-semibold text-slate-600">3. Área de Mensaje / Propuesta <span className="text-red-500">*</span></label>
                  <button
                    type="button"
                    onClick={handleCopyMessage}
                    className="flex items-center gap-1 text-[10px] text-slate-500 hover:text-emerald-700 transition-colors cursor-pointer"
                  >
                    {copiedText ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-500" />
                        <span className="text-emerald-600 font-bold">¡Copiado!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copiar texto</span>
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
                  className="w-full text-sm bg-slate-50 border border-slate-200 rounded-lg p-3 outline-none focus:ring-1 focus:ring-emerald-700 focus:border-emerald-700 font-sans leading-relaxed transition-colors resize-y min-h-[120px]"
                  placeholder="Escribe tu mensaje aquí..."
                />
              </div>

              <div className="mt-6 flex flex-col sm:flex-row items-center gap-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-60 text-white font-bold rounded-lg text-sm transition-all shadow-md shadow-emerald-100 cursor-pointer"
                >
                  <span>{loading ? "Enviando..." : "Enviar Formulario"}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <div className="text-center sm:text-left text-xs text-slate-500 font-sans">
                  El formulario enviará los datos directamente a{" "}
                  <a href="mailto:hello@cli-market.dev" className="text-emerald-700 hover:underline font-bold">
                    hello@cli-market.dev
                  </a>
                </div>
              </div>
            </form>
          )}
        </div>
      </div>
    </section>
  );
}
