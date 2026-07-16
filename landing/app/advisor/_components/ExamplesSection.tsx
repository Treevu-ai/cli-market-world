"use client";

import { useState } from "react";
import { Megaphone, TrendingUp, Copy, Check } from "lucide-react";

export default function ExamplesSection() {
  const [activeExample, setActiveExample] = useState<"A" | "B">("A");
  const [copiedScript, setCopiedScript] = useState(false);

  const handleCopyScript = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedScript(true);
    setTimeout(() => setCopiedScript(false), 2000);
  };

  const scriptA = `1. Elegí país + categoría (ej. PE · higiene/supermercados).  
2. Corré comparativa de 3–5 referencias (natural, mass, premium).  
3. Salí con rango de precio + 1 recomendación de canal + 1 caveat de frescura.`;

  const scriptB = `1. Fijá país + línea (ej. PE · supermercados) y ventana (7 o 30 días).  
2. Corré brief + inflación (+ risk si el cliente es procurement).  
3. Entregá 5 bullets + 1 acción recomendada + frescura del dato.`;

  return (
    <section id="ejemplos-casos" className="mb-16 scroll-mt-24">
      <div className="text-center mb-10">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-50 border border-emerald-100 text-emerald-800 uppercase tracking-widest mb-3">
          CASOS DE APLICACIÓN PRÁCTICA
        </span>
        <h2 className="text-3xl font-display font-bold text-slate-900 tracking-tight mb-2">
          Ejemplos de Aplicación en Negocios Reales
        </h2>
        <p className="text-slate-600 max-w-2xl mx-auto">
          Mirá cómo asesores reales combinan su expertise estratégico con la evidencia empírica de CLI Market para entregar valor masivo.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 max-w-2xl mx-auto mb-8 bg-slate-100 p-1.5 rounded-2xl border border-slate-200">
        <button
          onClick={() => { setActiveExample("A"); setCopiedScript(false); }}
          className={`py-3 px-4 rounded-xl font-medium text-sm sm:text-base transition-all flex items-center justify-center gap-2 ${
            activeExample === "A"
              ? "bg-white text-slate-900 shadow-sm border border-slate-200/80"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <Megaphone className="w-4 h-4 text-emerald-500" />
          <span>Ejemplo A: Lanzamiento</span>
        </button>
        <button
          onClick={() => { setActiveExample("B"); setCopiedScript(false); }}
          className={`py-3 px-4 rounded-xl font-medium text-sm sm:text-base transition-all flex items-center justify-center gap-2 ${
            activeExample === "B"
              ? "bg-white text-slate-900 shadow-sm border border-slate-200/80"
              : "text-slate-600 hover:text-slate-900"
          }`}
        >
          <TrendingUp className="w-4 h-4 text-emerald-500" />
          <span>Ejemplo B: Inteligencia</span>
        </button>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden grid lg:grid-cols-12">
        <div className="lg:col-span-5 bg-slate-50 p-6 sm:p-8 border-b lg:border-b-0 lg:border-r border-slate-200 flex flex-col justify-between">
          <div>
            <span className="text-[10px] font-mono font-bold tracking-widest text-slate-400 uppercase block mb-1">
              {activeExample === "A" ? "Marketing / Posicionamiento" : "Macro-Análisis / CPG Intelligence"}
            </span>
            <h3 className="text-2xl font-display font-bold text-slate-900 mb-2">
              {activeExample === "A" ? "Caso: Champú Natural / Orgánico (PE)" : "Caso: Inflación de Estantería (PE)"}
            </h3>

            <div className="space-y-4 mt-6">
              <div className="bg-white p-4 rounded-xl border border-slate-200/60">
                <span className="text-xs font-semibold text-slate-500 block mb-0.5">Perfil de Asesor:</span>
                <span className="text-sm font-medium text-slate-800">
                  {activeExample === "A" ? "Consultor de Marketing o Empresarial" : "Analista de Inteligencia de Mercados o Consultor Financiero"}
                </span>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200/60">
                <span className="text-xs font-semibold text-slate-500 block mb-0.5">Cliente del Asesor:</span>
                <span className="text-sm font-medium text-slate-800">
                  {activeExample === "A" ? "Emprendedor o marca mediana lanzando línea higiene" : "Director Comercial, Retailer, Consumo Masivo (CPG) o Fintech"}
                </span>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200/60">
                <span className="text-xs font-semibold text-slate-500 block mb-0.5">Pack Recomendado:</span>
                <span className="text-xs font-mono font-bold uppercase text-emerald-800 bg-emerald-50 border border-emerald-100 px-2 py-0.5 rounded inline-block mt-1">
                  {activeExample === "A" ? "Pack A (Brief) o Pack B (Sesión)" : "Pack C (Retainer Mensual) o Pack A (Brief)"}
                </span>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-slate-200">
              <h4 className="text-sm font-bold text-slate-950 mb-2">Problema del Cliente Final:</h4>
              <p className="text-sm text-slate-600 leading-relaxed">
                {activeExample === "A"
                  ? "No tiene certeza de a qué precio salir al mercado peruano, si le conviene competir en supermercados masivos o cadenas de especialidad, ni si su competencia directa está quemando margen con promociones agresivas."
                  : "Siente que la canasta básica está experimentando incrementos de precio, pero carece de datos semanales consolidados. No puede esperar 30 días al reporte oficial del IPC estatal para ajustar sus listas de precios de compra o de distribución."
                }
              </p>
            </div>
          </div>

          <div className="mt-8 bg-slate-900 text-slate-100 p-4 rounded-xl relative">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono uppercase text-emerald-400">Micro-script de Pitch (3 pasos)</span>
              <button
                onClick={() => handleCopyScript(activeExample === "A" ? scriptA : scriptB)}
                className="text-slate-400 hover:text-white transition-colors"
                title="Copiar Micro-script"
              >
                {copiedScript ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
            <pre className="text-xs font-sans whitespace-pre-wrap leading-relaxed text-slate-300">
              {activeExample === "A" ? scriptA : scriptB}
            </pre>
          </div>
        </div>

        <div className="lg:col-span-7 p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-mono uppercase tracking-wider text-slate-400 mb-6">
              Cómo CLI Market ayuda al asesor a resolver el caso
            </h4>

            <div className="space-y-6 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-100">
              {activeExample === "A" ? (
                <>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-emerald-50 border border-emerald-300 flex items-center justify-center text-xs font-bold text-emerald-700 z-10 shrink-0">
                      1
                    </div>
                    <div>
                      <h5 className="font-semibold text-slate-900 text-sm">Comparar &ldquo;champú&rdquo; + marcas ancla</h5>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">Acción: market compare &ldquo;champú&rdquo; --country pe</p>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                        Se extraen precios de marcas ancla (naturales vs mass market) en retailers peruanos en tiempo real.
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-emerald-50 border border-emerald-300 flex items-center justify-center text-xs font-bold text-emerald-700 z-10 shrink-0">
                      2
                    </div>
                    <div>
                      <h5 className="font-semibold text-slate-900 text-sm">Optimizar canasta o SKUs de referencia</h5>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">Acción: market optimize champú:2 acondicionador:1 --country pe</p>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                        Se mapea en qué retailers específicos la canasta del cliente tiene el mejor TCO para el consumidor final.
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-emerald-50 border border-emerald-300 flex items-center justify-center text-xs font-bold text-emerald-700 z-10 shrink-0">
                      3
                    </div>
                    <div>
                      <h5 className="font-semibold text-slate-900 text-sm">Leer señales de categoría (Intel Brief)</h5>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">Acción: market intel brief --country pe</p>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                        Determina la presión promocional actual y la variabilidad de precios en la categoría.
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-xs font-bold text-emerald-600 z-10 shrink-0">
                      4
                    </div>
                    <div>
                      <h5 className="font-semibold text-slate-900 text-sm">El asesor estructura las 4P de marketing</h5>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">Resultado: Posicionamiento Blindado</p>
                      <p className="text-xs text-slate-700 font-medium mt-1 leading-relaxed">
                        Fija el Precio y la Plaza basándose en evidencia sólida de góndola; se enfoca creativamente en el Producto y Promoción con criterio humano.
                      </p>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-xs font-bold text-emerald-600 z-10 shrink-0">
                      1
                    </div>
                    <div>
                      <h5 className="font-semibold text-slate-900 text-sm">Analizar Inflación de Estantería</h5>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">Acción: market intel inflation --country pe</p>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                        Calcula la fluctuación exacta de precios promedio ponderados en estantería digital en los últimos 7 días, desglosado por línea.
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-xs font-bold text-emerald-600 z-10 shrink-0">
                      2
                    </div>
                    <div>
                      <h5 className="font-semibold text-slate-900 text-sm">Analizar Índice de Riesgo e Intel Brief</h5>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">Acción: market intel brief --country pe --days 14</p>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                        Mapea qué productos específicos de la canasta del cliente sufrieron mayor dispersión o quiebres de stock temporales online.
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4 relative">
                    <div className="w-7 h-7 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-xs font-bold text-emerald-600 z-10 shrink-0">
                      3
                    </div>
                    <div>
                      <h5 className="font-semibold text-slate-900 text-sm">Monitorear stats y cobertura de la góndola</h5>
                      <p className="text-xs text-slate-500 font-mono mt-0.5">Acción: market stats</p>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                        Valida la frescura de los datos recolectados para garantizar un margen metodológico estricto.
                      </p>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>

          <div className="mt-8 bg-slate-50 border border-slate-200 rounded-xl p-5">
            <span className="text-[10px] font-mono tracking-wider uppercase text-slate-400 block mb-1">
              Entregable Final del Asesor para su Cliente
            </span>
            <div className="space-y-2">
              <h5 className="text-sm font-bold text-slate-900">
                {activeExample === "A"
                  ? "✓ Dossier de Posicionamiento de Precio & Canal"
                  : "✓ Reporte Ejecutivo de Alerta Inflacionaria de Góndola"
                }
              </h5>
              <ul className="text-xs text-slate-600 space-y-1">
                {activeExample === "A" ? (
                  <>
                    <li className="flex items-center gap-1.5">• <strong>Rango objetivo de precio:</strong> Evidencia de góndola para fijar el punto óptimo.</li>
                    <li className="flex items-center gap-1.5">• <strong>Mapeo de plaza:</strong> Canales recomendados por menor presión competitiva.</li>
                    <li className="flex items-center gap-1.5">• <strong>Riesgos detectados:</strong> Mismatch de SKU y alertas promocionales activas.</li>
                  </>
                ) : (
                  <>
                    <li className="flex items-center gap-1.5">• <strong>Diagnóstico de presión:</strong> Saber si la inflación de estantería está acelerando o estable.</li>
                    <li className="flex items-center gap-1.5">• <strong>Caveat fundamental:</strong> Claridad de que la inflación online es predictiva, no el IPC estatal.</li>
                    <li className="flex items-center gap-1.5">• <strong>Sugerencia comercial:</strong> Cuándo re-negociar con distribuidores antes de perder margen.</li>
                  </>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
