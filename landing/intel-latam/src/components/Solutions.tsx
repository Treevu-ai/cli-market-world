import React from "react";
import { 
  TrendingUp, ArrowUpRight, Search, Zap, 
  ShoppingCart, ShieldAlert, Coins, HelpCircle, 
  BarChart4, Percent, Layers, CheckSquare 
} from "lucide-react";
import { RoleTabId } from "../types";
import { motion, AnimatePresence } from "motion/react";
import ScrollReveal from "./ScrollReveal";

interface SolutionsProps {
  activeRole: RoleTabId;
  setActiveRole: (role: RoleTabId) => void;
}

export default function Solutions({ activeRole, setActiveRole }: SolutionsProps) {
  
  const handleTabClick = (role: RoleTabId) => {
    setActiveRole(role);
  };

  return (
    <section className="bg-[#0a0a0a] text-[#f5f5f5] py-20 lg:py-28 border-b border-white/10" id="soluciones-section">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        {/* Header Title */}
        <ScrollReveal duration={0.8}>
          <div className="mx-auto max-w-3xl text-center mb-12">
            <span className="font-mono text-[10px] font-bold text-[#bef264] uppercase tracking-widest bg-[#bef264]/5 border border-[#bef264]/20 px-3 py-1.5 rounded-sm">
              Matriz de Valor
            </span>
            <h2 className="mt-6 text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Inteligencia diseñada para cada función del negocio.
            </h2>
            <p className="mt-3 text-white/60 text-xs sm:text-sm max-w-xl mx-auto">
              Segmenta la información según tus objetivos estratégicos. Elige tu rol comercial abajo para ver cómo CLI Market empodera tu día a día.
            </p>
          </div>
        </ScrollReveal>

        {/* Tab Buttons bar */}
        <ScrollReveal delay={0.1} duration={0.8}>
          <div className="flex flex-wrap justify-center gap-2 md:gap-4 mb-12 border-b border-white/10 pb-4 max-w-2xl mx-auto">
            
            <button
              onClick={() => handleTabClick("revenue")}
              className={`flex items-center space-x-2 px-5 py-3 rounded-sm text-xs font-mono font-bold uppercase tracking-widest transition-all duration-200 cursor-pointer ${
                activeRole === "revenue"
                  ? "bg-[#bef264] text-black"
                  : "bg-white/5 text-white/70 hover:bg-white/10 border border-white/10"
              }`}
              id="tab-btn-revenue"
            >
              <span className={`inline-block h-1.5 w-1.5 rounded-full ${activeRole === "revenue" ? "bg-black animate-pulse" : "bg-[#bef264]"}`}></span>
              <span>Revenue & Growth</span>
            </button>

            <button
              onClick={() => handleTabClick("procurement")}
              className={`flex items-center space-x-2 px-5 py-3 rounded-sm text-xs font-mono font-bold uppercase tracking-widest transition-all duration-200 cursor-pointer ${
                activeRole === "procurement"
                  ? "bg-[#bef264] text-black"
                  : "bg-white/5 text-white/70 hover:bg-white/10 border border-white/10"
              }`}
              id="tab-btn-procurement"
            >
              <span className={`inline-block h-1.5 w-1.5 rounded-full ${activeRole === "procurement" ? "bg-black animate-pulse" : "bg-[#bef264]"}`}></span>
              <span>Procurement & Ops</span>
            </button>

            <button
              onClick={() => handleTabClick("innovation")}
              className={`flex items-center space-x-2 px-5 py-3 rounded-sm text-xs font-mono font-bold uppercase tracking-widest transition-all duration-200 cursor-pointer ${
                activeRole === "innovation"
                  ? "bg-[#bef264] text-black"
                  : "bg-white/5 text-white/70 hover:bg-white/10 border border-white/10"
              }`}
              id="tab-btn-innovation"
            >
              <span className={`inline-block h-1.5 w-1.5 rounded-full ${activeRole === "innovation" ? "bg-black animate-pulse" : "bg-[#bef264]"}`}></span>
              <span>Innovación & Producto</span>
            </button>
          </div>
        </ScrollReveal>

        {/* Interactive Tab Content Display */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch mt-8">
          
          {/* Content Column (Left or Right depending on alignment) */}
          <ScrollReveal delay={0.2} duration={0.8} className="lg:col-span-6 flex flex-col justify-center">
            <div className="flex flex-col justify-center bg-white/5 border border-white/10 p-8 sm:p-12 rounded-sm text-left h-full">
              
              <AnimatePresence mode="wait">
                {activeRole === "revenue" && (
                  <motion.div
                    key="revenue-content"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ duration: 0.15 }}
                    className="space-y-6"
                  >
                    <span className="font-mono text-[9px] font-bold text-[#bef264] bg-[#bef264]/10 border border-[#bef264]/20 px-2.5 py-1 rounded-sm uppercase tracking-widest">
                      MODO ATAQUE
                    </span>
                    
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white leading-tight font-sans">
                      Captura Market Share con Precisión Quirúrgica.
                    </h3>

                    <div className="space-y-5 pt-2">
                      
                      {/* Benefit 1 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <TrendingUp className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Dynamic Pricing</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Ajusta tus precios basándote en el movimiento real y actualizado de toda la competencia.</p>
                        </div>
                      </div>

                      {/* Benefit 2 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <Search className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Gap Detection</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Encuentra de inmediato huecos e inconsistencias en la oferta de los retailers y lánzate con el producto correcto.</p>
                        </div>
                      </div>

                      {/* Benefit 3 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <Zap className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Offensive Marketing</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Identifica en qué canales o tiendas tu competencia directa está sobrepreciada y lanza un ataque enfocado de volumen.</p>
                        </div>
                      </div>

                    </div>

                    <div className="pt-6 border-t border-white/10">
                      <p className="text-sm sm:text-base font-bold text-[#bef264] italic font-serif">
                        "Deja de reaccionar al mercado. Empieza a dictarlo."
                      </p>
                    </div>
                  </motion.div>
                )}

                {activeRole === "procurement" && (
                  <motion.div
                    key="procurement-content"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ duration: 0.15 }}
                    className="space-y-6"
                  >
                    <span className="font-mono text-[9px] font-bold text-[#bef264] bg-[#bef264]/10 border border-[#bef264]/20 px-2.5 py-1 rounded-sm uppercase tracking-widest">
                      MODO DEFENSA
                    </span>
                    
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white leading-tight font-sans">
                      Optimiza el Gasto, Elimina la Fuga de Capital.
                    </h3>

                    <div className="space-y-5 pt-2">
                      
                      {/* Benefit 1 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <ShoppingCart className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Procure Copilot</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Optimiza tus canastas de insumos y compras de abastecimiento automáticamente calculando los mejores splits de tiendas.</p>
                        </div>
                      </div>

                      {/* Benefit 2 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <ShieldAlert className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Auditoría de Góndola</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Verifica que el precio real neto cobrado coincida exactamente con las cotizaciones acordadas del mercado actual.</p>
                        </div>
                      </div>

                      {/* Benefit 3 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <Coins className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Arbitraje de Suministros</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Encuentra la fuente regional o el distribuidor local más eficiente de insumos y materias primas en tiempo real.</p>
                        </div>
                      </div>

                    </div>

                    <div className="pt-6 border-t border-white/10">
                      <p className="text-sm sm:text-base font-bold text-[#bef264] italic font-serif">
                        "Convierte tu departamento de compras en un centro de ahorro estratégico."
                      </p>
                    </div>
                  </motion.div>
                )}

                {activeRole === "innovation" && (
                  <motion.div
                    key="innovation-content"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 10 }}
                    transition={{ duration: 0.15 }}
                    className="space-y-6"
                  >
                    <span className="font-mono text-[9px] font-bold text-[#bef264] bg-[#bef264]/10 border border-[#bef264]/20 px-2.5 py-1 rounded-sm uppercase tracking-widest">
                      MODO ESTRATEGIA
                    </span>
                    
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white leading-tight font-sans">
                      Diseña Productos que el Mercado ya está Demandando.
                    </h3>

                    <div className="space-y-5 pt-2">
                      
                      {/* Benefit 1 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <Layers className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Sizing de Oportunidad</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Valida el potencial de rentabilidad de un nuevo SKU basándote en la distribución real y densidad de precios de la categoría.</p>
                        </div>
                      </div>

                      {/* Benefit 2 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <Percent className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Análisis de Elasticidad</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Observa empíricamente cómo reacciona el consumidor y la góndola ante incrementos macro de precios.</p>
                        </div>
                      </div>

                      {/* Benefit 3 */}
                      <div className="flex items-start space-x-3.5">
                        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                          <BarChart4 className="h-4 w-4" />
                        </div>
                        <div>
                          <h4 className="text-sm sm:text-base font-bold text-white uppercase tracking-wider font-mono">Benchmarking Continuo</h4>
                          <p className="text-xs sm:text-sm text-white/60 mt-0.5">Mide la propuesta de valor y los márgenes de tu marca contra el promedio ponderado consolidado de todo el mercado.</p>
                        </div>
                      </div>

                    </div>

                    <div className="pt-6 border-t border-white/10">
                      <p className="text-sm sm:text-base font-bold text-[#bef264] italic font-serif">
                        "Lanza productos con un hit-rate del 100% basándote en datos, no en hipótesis."
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

            </div>
          </ScrollReveal>

          {/* Visual Mockup Dashboard Column (Right) */}
          <ScrollReveal delay={0.3} duration={0.8} className="lg:col-span-6 flex flex-col justify-center">
            <div className="relative w-full rounded-sm border border-white/10 bg-black/45 text-white p-5 sm:p-8 overflow-hidden flex flex-col min-h-[440px] shadow-lg text-left h-full">
              <div className="absolute top-0 left-0 right-0 h-[2px] bg-[#bef264]"></div>
              
              {/* Fake Menu Window controls */}
              <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-5">
                <div className="flex items-center space-x-1.5">
                  <span className="h-2.5 w-2.5 rounded-full bg-zinc-850 border border-white/10"></span>
                  <span className="h-2.5 w-2.5 rounded-full bg-zinc-850 border border-white/10"></span>
                  <span className="h-2.5 w-2.5 rounded-full bg-zinc-850 border border-white/10"></span>
                  <span className="text-white/40 font-mono text-[9px] uppercase tracking-wider ml-2">Console v1.4 // Live Matrix</span>
                </div>
                <div className="bg-white/5 px-2 py-0.5 rounded-sm font-mono text-[8px] text-[#bef264] font-bold border border-[#bef264]/20 tracking-widest uppercase">
                  VISTA PREVIA
                </div>
              </div>

              {/* Dynamic visual dashboard depending on Tab active */}
              <div className="flex-1 flex flex-col justify-center">
                <AnimatePresence mode="wait">
                  
                  {activeRole === "revenue" && (
                    <motion.div
                      key="revenue-viz"
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.98 }}
                      transition={{ duration: 0.12 }}
                      className="space-y-4 text-xs font-mono"
                    >
                      <div className="flex justify-between items-center bg-[#bef264]/5 p-2.5 rounded-sm border border-[#bef264]/20">
                        <span className="text-white/80">💡 Alerta de Gap Activo</span>
                        <span className="text-[#bef264] font-bold">+14.2% Sobreprecio</span>
                      </div>
                      
                      {/* Gap graph comparison */}
                      <div className="space-y-3 bg-white/5 p-4 rounded-sm border border-white/10">
                        <div className="text-[9px] text-white/40 tracking-wider">PRODUCTO: CAFÉ SOLUBLE LIOFILIZADO 100G</div>
                        
                        <div className="space-y-1">
                          <div className="flex justify-between text-[10px]">
                            <span className="text-white/60">Tu Marca (Precio Base)</span>
                            <span className="text-white">S/ 21.00 PEN</span>
                          </div>
                          <div className="h-1.5 w-full bg-white/5 rounded-sm overflow-hidden border border-white/5">
                            <div className="h-full bg-white/30" style={{ width: '60%' }}></div>
                          </div>
                        </div>

                        <div className="space-y-1">
                          <div className="flex justify-between text-[10px]">
                            <span className="text-white/60">Competidor Lider (Walmart)</span>
                            <span className="text-[#bef264] font-bold">S/ 24.90 PEN (+18.5%)</span>
                          </div>
                          <div className="h-1.5 w-full bg-white/5 rounded-sm overflow-hidden border border-white/5">
                            <div className="h-full bg-[#bef264]" style={{ width: '85%' }}></div>
                          </div>
                        </div>

                        <div className="space-y-1">
                          <div className="flex justify-between text-[10px]">
                            <span className="text-white/60">Competidor B (Plaza Vea)</span>
                            <span className="text-white/80">S/ 19.90 PEN (-5.2%)</span>
                          </div>
                          <div className="h-1.5 w-full bg-white/5 rounded-sm overflow-hidden border border-white/5">
                            <div className="h-full bg-white/50" style={{ width: '48%' }}></div>
                          </div>
                        </div>
                      </div>

                      <div className="p-3 bg-white/5 border border-white/10 rounded-sm text-[10px] text-white/60 leading-normal font-sans">
                        <strong className="text-white font-mono text-[9px] uppercase tracking-wider block mb-1">Estrategia de Ataque recomendada:</strong> Competidor Líder tiene quiebre de stock en CDMX. Reducir 2% temporalmente para canalizar demanda cautiva.
                      </div>
                    </motion.div>
                  )}

                  {activeRole === "procurement" && (
                    <motion.div
                      key="procurement-viz"
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.98 }}
                      transition={{ duration: 0.12 }}
                      className="space-y-4 text-xs font-mono"
                    >
                      <div className="bg-[#bef264]/5 p-2.5 rounded-sm border border-[#bef264]/20 flex justify-between items-center">
                        <span className="text-white/80">🛒 Canasta Corporativa Optimizada</span>
                        <span className="text-[#bef264] font-bold">Ahorro Neto: 18.2%</span>
                      </div>

                      {/* Procurement split receipt */}
                      <div className="bg-white/5 p-4 rounded-sm border border-white/10 space-y-3">
                        <div className="flex justify-between border-b border-white/10 pb-2 text-[9px] text-white/40 tracking-wider font-bold">
                          <span>ITEM DE LA CANASTA (Split)</span>
                          <span>COMPRAR EN</span>
                          <span className="text-right">AHORRO</span>
                        </div>
                        
                        <div className="flex justify-between text-[11px] items-center">
                          <span className="text-white/80">Arroz Extra Grano x25kg</span>
                          <span className="text-[#bef264] font-bold bg-[#bef264]/10 px-1.5 py-0.5 rounded-sm border border-[#bef264]/20 text-[10px]">Wong</span>
                          <span className="text-[#bef264] font-bold">-22%</span>
                        </div>

                        <div className="flex justify-between text-[11px] items-center">
                          <span className="text-white/80">Aceite Vegetal x18L</span>
                          <span className="text-[#bef264] font-bold bg-[#bef264]/10 px-1.5 py-0.5 rounded-sm border border-[#bef264]/20 text-[10px]">Plaza Vea</span>
                          <span className="text-[#bef264] font-bold">-14%</span>
                        </div>

                        <div className="flex justify-between text-[11px] items-center">
                          <span className="text-white/80">Harina de Trigo x50kg</span>
                          <span className="text-[#bef264] font-bold bg-[#bef264]/10 px-1.5 py-0.5 rounded-sm border border-[#bef264]/20 text-[10px]">Metro</span>
                          <span className="text-[#bef264] font-bold">-19%</span>
                        </div>
                      </div>

                      <div className="p-3 bg-white/5 border border-white/10 rounded-sm text-[10px] text-white/60 leading-normal font-sans">
                        <strong className="text-white font-mono text-[9px] uppercase tracking-wider block mb-1">Procure Copilot Cop:</strong> Al consolidar el split propuesto, tu costo total desciende de S/ 8,450 a S/ 6,912.
                      </div>
                    </motion.div>
                  )}

                  {activeRole === "innovation" && (
                    <motion.div
                      key="innovation-viz"
                      initial={{ opacity: 0, scale: 0.98 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.98 }}
                      transition={{ duration: 0.12 }}
                      className="space-y-4 text-xs font-mono"
                    >
                      <div className="bg-[#bef264]/5 p-3 rounded-sm border border-[#bef264]/20 flex justify-between items-center">
                        <span className="text-white/80">📊 Oportunidad de SKU Lácteo</span>
                        <span className="text-[#bef264] font-bold">Viabilidad: 92%</span>
                      </div>

                      {/* SKU Sizing map chart visualizer */}
                      <div className="bg-white/5 p-4 rounded-sm border border-white/10 space-y-3.5">
                        <div className="text-[9px] text-white/40 uppercase tracking-widest font-bold">Concentración de SKU por Rango de Precios</div>
                        
                        <div className="space-y-1.5">
                          <div className="flex justify-between text-[10px]">
                            <span className="text-white/60">Rango Low (S/ 2.50 - S/ 3.20)</span>
                            <span className="text-white/40">12 SKUs • Saturado</span>
                          </div>
                          <div className="h-2 w-full bg-zinc-900 rounded-sm overflow-hidden border border-white/5">
                            <div className="h-full bg-white/20" style={{ width: '80%' }}></div>
                          </div>
                        </div>

                        <div className="space-y-1.5">
                          <div className="flex justify-between text-[10px] text-[#bef264] font-bold">
                            <span>Rango Medio (S/ 3.25 - S/ 4.10) ★ OPORTUNIDAD</span>
                            <span>1 SKU</span>
                          </div>
                          <div className="h-2 w-full bg-zinc-900 rounded-sm overflow-hidden border border-[#bef264]/30">
                            <div className="h-full bg-[#bef264]" style={{ width: '12%' }}></div>
                          </div>
                        </div>

                        <div className="space-y-1.5">
                          <div className="flex justify-between text-[10px]">
                            <span className="text-white/60">Rango Premium (S/ 4.15+)</span>
                            <span className="text-white/40">18 SKUs • Saturado</span>
                          </div>
                          <div className="h-2 w-full bg-zinc-900 rounded-sm overflow-hidden border border-white/5">
                            <div className="h-full bg-white/20" style={{ width: '90%' }}></div>
                          </div>
                        </div>
                      </div>

                      <div className="p-3 bg-white/5 border border-white/10 rounded-sm text-[10px] text-white/60 leading-normal font-sans">
                        <strong className="text-white font-mono text-[9px] uppercase tracking-wider block mb-1">Sizing Insight:</strong> El segmento medio-bajo se encuentra desabastecido de marcas locales en formato familiar.
                      </div>
                    </motion.div>
                  )}
                  
                </AnimatePresence>
              </div>

              <p className="mt-4 pt-4 border-t border-white/10 text-[9px] text-white/30 font-mono uppercase tracking-wider">
                Vista previa ilustrativa — capacidad en construcción, cifras de ejemplo.
              </p>

            </div>
          </ScrollReveal>

        </div>

      </div>
    </section>
  );
}
