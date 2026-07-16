"use client";

import { useState } from "react";
import { Megaphone, TrendingUp, Copy, Check } from "lucide-react";
import { useLang } from "@/lib/LanguageContext";

export default function ExamplesSection() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [activeExample, setActiveExample] = useState<"A" | "B">("A");
  const [copiedScript, setCopiedScript] = useState(false);

  const handleCopyScript = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedScript(true);
    setTimeout(() => setCopiedScript(false), 2000);
  };

  const scriptA_es = `1. Elegí país + categoría (ej. PE · higiene/supermercados).
2. Corré comparativa de 3–5 referencias (natural, mass, premium).
3. Salí con rango de precio + 1 recomendación de canal + 1 caveat de frescura.`;
  const scriptA_en = `1. Pick country + category (e.g. PE · personal care/supermarkets).
2. Run a comparison across 3–5 reference brands (natural, mass, premium).
3. Come out with a price range + 1 channel recommendation + 1 freshness caveat.`;

  const scriptB_es = `1. Fijá país + línea (ej. PE · supermercados) y ventana (7 o 30 días).
2. Corré brief + inflación (+ risk si el cliente es procurement).
3. Entregá 5 bullets + 1 acción recomendada + frescura del dato.`;
  const scriptB_en = `1. Set country + line (e.g. PE · supermarkets) and window (7 or 30 days).
2. Run brief + inflation (+ risk if the client is procurement).
3. Deliver 5 bullets + 1 recommended action + data freshness.`;

  const script = activeExample === "A" ? (isES ? scriptA_es : scriptA_en) : isES ? scriptB_es : scriptB_en;

  return (
    <section id="ejemplos-casos" className="landing-section scroll-mt-24">
      <div className="landing-container-wide">
      <div className="landing-section-header text-center">
        <p className="section-eyebrow mb-4">
          {isES ? "Casos de aplicación práctica" : "Applied use cases"}
        </p>
        <h2 className="section-title">
          {isES ? "Ejemplos con negocios reales" : "Examples with real businesses"}
        </h2>
        <p className="section-intro">
          {isES
            ? "Cómo asesores combinan su criterio estratégico con evidencia empírica de CLI Market para entregar valor concreto."
            : "How advisors combine strategic judgment with CLI Market's empirical evidence to deliver concrete value."}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto mt-10 mb-8 bg-[var(--cm-surface-high)] p-1.5 rounded-2xl border border-[var(--cm-outline-variant)]">
        <button
          onClick={() => { setActiveExample("A"); setCopiedScript(false); }}
          className={`py-3 px-4 rounded-xl font-medium text-sm sm:text-base transition-all flex items-center justify-center gap-2 ${
            activeExample === "A"
              ? "bg-[var(--cm-surface)] text-[var(--cm-on-surface)] shadow-sm border border-[var(--cm-outline-variant)]/80"
              : "text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)]"
          }`}
        >
          <Megaphone className="w-4 h-4 text-[var(--cm-mint)]" />
          <span>{isES ? "Ejemplo A: Lanzamiento" : "Example A: Launch"}</span>
        </button>
        <button
          onClick={() => { setActiveExample("B"); setCopiedScript(false); }}
          className={`py-3 px-4 rounded-xl font-medium text-sm sm:text-base transition-all flex items-center justify-center gap-2 ${
            activeExample === "B"
              ? "bg-[var(--cm-surface)] text-[var(--cm-on-surface)] shadow-sm border border-[var(--cm-outline-variant)]/80"
              : "text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)]"
          }`}
        >
          <TrendingUp className="w-4 h-4 text-[var(--cm-mint)]" />
          <span>{isES ? "Ejemplo B: Inteligencia" : "Example B: Intelligence"}</span>
        </button>
      </div>

      <div className="bg-[var(--cm-surface)] rounded-2xl border border-[var(--cm-outline-variant)] shadow-sm overflow-hidden grid lg:grid-cols-12">
        <div className="lg:col-span-5 bg-[var(--cm-surface-high)] p-6 sm:p-8 border-b lg:border-b-0 lg:border-r border-[var(--cm-outline-variant)] flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-mono font-bold tracking-widest text-[var(--cm-text-secondary)] uppercase block mb-1">
              {activeExample === "A"
                ? isES ? "Marketing / Posicionamiento" : "Marketing / Positioning"
                : isES ? "Macro-análisis / Inteligencia de consumo" : "Macro-analysis / CPG intelligence"}
            </span>
            <h3 className="text-2xl font-display font-bold text-[var(--cm-on-surface)] mb-2">
              {activeExample === "A"
                ? isES ? "Caso: champú natural / orgánico (PE)" : "Case: natural/organic shampoo (PE)"
                : isES ? "Caso: inflación de estantería (PE)" : "Case: shelf inflation (PE)"}
            </h3>

            <div className="space-y-4 mt-6">
              <div className="bg-[var(--cm-surface)] p-4 rounded-xl border border-[var(--cm-hairline-soft)]">
                <span className="text-xs font-semibold text-[var(--cm-text-secondary)] block mb-0.5">
                  {isES ? "Perfil del asesor:" : "Advisor profile:"}
                </span>
                <span className="text-sm font-medium text-[var(--cm-on-surface)]">
                  {activeExample === "A"
                    ? isES ? "Consultor de marketing o de negocio" : "Marketing or business consultant"
                    : isES ? "Analista de inteligencia de mercados o consultor financiero" : "Market intelligence analyst or financial consultant"}
                </span>
              </div>
              <div className="bg-[var(--cm-surface)] p-4 rounded-xl border border-[var(--cm-hairline-soft)]">
                <span className="text-xs font-semibold text-[var(--cm-text-secondary)] block mb-0.5">
                  {isES ? "Cliente del asesor:" : "Advisor's client:"}
                </span>
                <span className="text-sm font-medium text-[var(--cm-on-surface)]">
                  {activeExample === "A"
                    ? isES ? "Emprendedor o marca mediana lanzando línea de higiene" : "Founder or mid-size brand launching a personal-care line"
                    : isES ? "Director comercial, retailer, consumo masivo o fintech" : "Commercial director, retailer, CPG, or fintech"}
                </span>
              </div>
              <div className="bg-[var(--cm-surface)] p-4 rounded-xl border border-[var(--cm-hairline-soft)]">
                <span className="text-xs font-semibold text-[var(--cm-text-secondary)] block mb-0.5">
                  {isES ? "Pack recomendado:" : "Recommended pack:"}
                </span>
                <span className="text-xs font-mono font-bold uppercase text-[var(--cm-action-deep)] bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/20 px-2 py-0.5 rounded inline-block mt-1">
                  {activeExample === "A"
                    ? isES ? "Pack A (Brief) o Pack B (Sesión)" : "Pack A (Brief) or Pack B (Session)"
                    : isES ? "Pack C (Retainer mensual) o Pack A (Brief)" : "Pack C (Monthly retainer) or Pack A (Brief)"}
                </span>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-[var(--cm-outline-variant)]">
              <h4 className="text-sm font-bold text-[var(--cm-on-surface)] mb-2">
                {isES ? "Problema del cliente final:" : "The end client's problem:"}
              </h4>
              <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
                {activeExample === "A"
                  ? isES
                    ? "No tiene certeza de a qué precio entrar al mercado peruano, si le conviene competir en supermercados masivos o cadenas de especialidad, ni si su competencia directa está quemando margen con promociones agresivas."
                    : "No certainty on what price to enter the Peruvian market at, whether to compete in mass supermarkets or specialty chains, or whether direct competitors are burning margin on aggressive promotions."
                  : isES
                    ? "Percibe que la canasta básica está subiendo de precio, pero no tiene datos semanales consolidados. No puede esperar 30 días al reporte oficial del IPC para ajustar sus listas de compra o distribución."
                    : "Senses the basic basket is getting more expensive but has no consolidated weekly data. Can't wait 30 days for the official CPI report to adjust purchase or distribution price lists."}
              </p>
            </div>
          </div>

          <div className="mt-8 bg-[var(--cm-ink)] text-[var(--cm-surface)] p-4 rounded-xl relative">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono uppercase text-[var(--cm-mint-dim)]">
                {isES ? "Micro-guion de pitch (3 pasos)" : "Pitch micro-script (3 steps)"}
              </span>
              <button
                onClick={() => handleCopyScript(script)}
                className="text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-surface)] transition-colors"
                title={isES ? "Copiar micro-guion" : "Copy micro-script"}
              >
                {copiedScript ? (
                  <Check className="w-3.5 h-3.5 text-[var(--cm-mint-dim)]" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
            <pre className="text-xs font-sans whitespace-pre-wrap leading-relaxed text-[var(--cm-on-surface-variant)]">
              {script}
            </pre>
          </div>
        </div>

        <div className="lg:col-span-7 p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-mono uppercase tracking-wider text-[var(--cm-text-secondary)] mb-6">
              {isES ? "Cómo CLI Market ayuda al asesor a resolver el caso" : "How CLI Market helps the advisor solve the case"}
            </h4>

            <div className="space-y-6 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-[var(--cm-hairline-soft)]">
              {activeExample === "A" ? (
                <>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/40 flex items-center justify-center text-xs font-bold text-[var(--cm-action-deep)] z-10 shrink-0">
                      1
                    </div>
                    <div>
                      <h5 className="font-semibold text-[var(--cm-on-surface)] text-sm">
                        {isES ? "Comparar “champú” + marcas ancla" : "Compare “shampoo” + anchor brands"}
                      </h5>
                      <p className="text-xs text-[var(--cm-text-secondary)] font-mono mt-0.5">market compare &quot;champú&quot; --country pe</p>
                      <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1 leading-relaxed">
                        {isES
                          ? "Extrae precios de marcas ancla (naturales vs. mass market) en retailers peruanos en tiempo real."
                          : "Pulls anchor-brand prices (natural vs. mass market) from Peruvian retailers in real time."}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/40 flex items-center justify-center text-xs font-bold text-[var(--cm-action-deep)] z-10 shrink-0">
                      2
                    </div>
                    <div>
                      <h5 className="font-semibold text-[var(--cm-on-surface)] text-sm">
                        {isES ? "Optimizar canasta o SKUs de referencia" : "Optimize the basket or reference SKUs"}
                      </h5>
                      <p className="text-xs text-[var(--cm-text-secondary)] font-mono mt-0.5">market optimize champú:2 acondicionador:1 --country pe</p>
                      <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1 leading-relaxed">
                        {isES
                          ? "Ubica en qué retailers específicos la canasta del cliente tiene el mejor TCO para el consumidor final."
                          : "Maps which specific retailers give the client's basket the best TCO for the end consumer."}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/40 flex items-center justify-center text-xs font-bold text-[var(--cm-action-deep)] z-10 shrink-0">
                      3
                    </div>
                    <div>
                      <h5 className="font-semibold text-[var(--cm-on-surface)] text-sm">
                        {isES ? "Leer señales de categoría (Intel Brief)" : "Read category signals (Intel Brief)"}
                      </h5>
                      <p className="text-xs text-[var(--cm-text-secondary)] font-mono mt-0.5">market intel brief --country pe</p>
                      <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1 leading-relaxed">
                        {isES
                          ? "Determina la presión promocional actual y la variabilidad de precios en la categoría."
                          : "Reads current promo intensity and price variability in the category."}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/20 flex items-center justify-center text-xs font-bold text-[var(--cm-mint)] z-10 shrink-0">
                      4
                    </div>
                    <div>
                      <h5 className="font-semibold text-[var(--cm-on-surface)] text-sm">
                        {isES ? "El asesor estructura las 4P de marketing" : "The advisor structures the marketing 4Ps"}
                      </h5>
                      <p className="text-xs text-[var(--cm-text-secondary)] font-mono mt-0.5">
                        {isES ? "Resultado: posicionamiento respaldado por datos" : "Result: data-backed positioning"}
                      </p>
                      <p className="text-xs text-[var(--cm-on-surface-variant)] font-medium mt-1 leading-relaxed">
                        {isES
                          ? "Fija precio y plaza sobre evidencia sólida de góndola; enfoca su criterio en producto y promoción."
                          : "Sets price and place on solid shelf evidence; focuses human judgment on product and promotion."}
                      </p>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/20 flex items-center justify-center text-xs font-bold text-[var(--cm-mint)] z-10 shrink-0">
                      1
                    </div>
                    <div>
                      <h5 className="font-semibold text-[var(--cm-on-surface)] text-sm">
                        {isES ? "Analizar inflación de estantería" : "Analyze shelf inflation"}
                      </h5>
                      <p className="text-xs text-[var(--cm-text-secondary)] font-mono mt-0.5">market intel inflation --country pe</p>
                      <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1 leading-relaxed">
                        {isES
                          ? "Calcula la variación de precios promedio ponderados en estantería digital en los últimos 7 días, por línea."
                          : "Computes the weighted average shelf-price change over the last 7 days, broken down by line."}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/20 flex items-center justify-center text-xs font-bold text-[var(--cm-mint)] z-10 shrink-0">
                      2
                    </div>
                    <div>
                      <h5 className="font-semibold text-[var(--cm-on-surface)] text-sm">
                        {isES ? "Revisar riesgo e Intel Brief" : "Review risk and Intel Brief"}
                      </h5>
                      <p className="text-xs text-[var(--cm-text-secondary)] font-mono mt-0.5">market intel brief --country pe --days 14</p>
                      <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1 leading-relaxed">
                        {isES
                          ? "Ubica qué productos de la canasta del cliente tuvieron mayor dispersión o quiebres de stock temporales."
                          : "Flags which items in the client's basket saw the most dispersion or temporary stockouts."}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-[var(--cm-action-soft)] border border-[var(--cm-mint)]/20 flex items-center justify-center text-xs font-bold text-[var(--cm-mint)] z-10 shrink-0">
                      3
                    </div>
                    <div>
                      <h5 className="font-semibold text-[var(--cm-on-surface)] text-sm">
                        {isES ? "Monitorear stats y cobertura de la góndola" : "Monitor stats and shelf coverage"}
                      </h5>
                      <p className="text-xs text-[var(--cm-text-secondary)] font-mono mt-0.5">market stats</p>
                      <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1 leading-relaxed">
                        {isES
                          ? "Valida la frescura del dato recolectado antes de citarlo en el reporte."
                          : "Validates data freshness before citing it in the report."}
                      </p>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="mt-8 bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-xl p-5">
            <span className="text-[10px] font-mono tracking-wider uppercase text-[var(--cm-text-secondary)] block mb-1">
              {isES ? "Entregable final del asesor para su cliente" : "Advisor's final deliverable to the client"}
            </span>
            <div className="space-y-2">
              <h5 className="text-sm font-bold text-[var(--cm-on-surface)]">
                {activeExample === "A"
                  ? isES ? "Dossier de posicionamiento de precio y canal" : "Price and channel positioning dossier"
                  : isES ? "Reporte ejecutivo de alerta inflacionaria de góndola" : "Executive shelf-inflation alert report"}
              </h5>
              <ul className="text-xs text-[var(--cm-on-surface-variant)] space-y-1">
                {activeExample === "A" ? (
                  <>
                    <li className="flex items-center gap-1.5">
                      • <strong>{isES ? "Rango objetivo de precio:" : "Target price range:"}</strong>{" "}
                      {isES ? "evidencia de góndola para fijar el punto óptimo." : "shelf evidence to set the optimal point."}
                    </li>
                    <li className="flex items-center gap-1.5">
                      • <strong>{isES ? "Mapeo de plaza:" : "Channel mapping:"}</strong>{" "}
                      {isES ? "canales recomendados por menor presión competitiva." : "recommended channels by lowest competitive pressure."}
                    </li>
                    <li className="flex items-center gap-1.5">
                      • <strong>{isES ? "Riesgos detectados:" : "Detected risks:"}</strong>{" "}
                      {isES ? "mismatch de SKU y alertas promocionales activas." : "SKU mismatches and active promo alerts."}
                    </li>
                  </>
                ) : (
                  <>
                    <li className="flex items-center gap-1.5">
                      • <strong>{isES ? "Diagnóstico de presión:" : "Pressure diagnosis:"}</strong>{" "}
                      {isES ? "si la inflación de estantería está acelerando o estable." : "whether shelf inflation is accelerating or stable."}
                    </li>
                    <li className="flex items-center gap-1.5">
                      • <strong>{isES ? "Caveat fundamental:" : "Key caveat:"}</strong>{" "}
                      {isES ? "la inflación online es directional, no reemplaza al IPC oficial." : "online inflation is directional, it doesn't replace the official CPI."}
                    </li>
                    <li className="flex items-center gap-1.5">
                      • <strong>{isES ? "Sugerencia comercial:" : "Commercial suggestion:"}</strong>{" "}
                      {isES ? "cuándo re-negociar con distribuidores antes de perder margen." : "when to renegotiate with distributors before losing margin."}
                    </li>
                  </>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
      </div>
    </section>
  );
}
