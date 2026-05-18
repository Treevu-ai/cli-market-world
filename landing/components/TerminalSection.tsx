"use client";
import { useEffect, useState, useRef } from "react";

const steps = [
  { cmd: "pip install git+https://github.com/Treevu-ai/cli-market-world.git", color: "#00FF88", output: "→ Instala el CLI en tu sistema", outColor: "#444" },
  { cmd: "market-server &", color: "#00FF88", output: "→ Levanta el backend en localhost:8765", outColor: "#444" },
  { cmd: "market login", color: "#00FF88", output: "→ Autentícate para acceder a 3,400+ retailers", outColor: "#444" },
  { cmd: 'market search "leche" --country PE', color: "#FF6B35", isMulti: true, results: [{text:"1. Leche Gloria 400ml  Wong  S/3.50",color:"#CCC"}]},
  { cmd: 'market compare "aceite"', color: "#4ADE80", isMulti: true, results: [{text:"Aceite Primor 1L → S/8.90 Wong 🇵🇪",color:"#888"},{text:"Aceite Natura 900ml → ARS 1,250 Carrefour 🇦🇷",color:"#888"},{text:"Aceite Liza 900ml → R$6.50 Carrefour BR 🇧🇷",color:"#888"}]},
  { cmd: "market add 1 --qty 2", color: "#F5F5F0", output: "→ Agrega al carrito desde el resultado de búsqueda", outColor: "#444" },
  { cmd: "market checkout --payment yape", color: "#F5F5F0", output: "→ Completa la compra con métodos de pago locales", outColor: "#444" },
];

export default function TerminalSection() {
  const [visible, setVisible] = useState(false);
  const [stepIdx, setStepIdx] = useState(0);
  const [typed, setTyped] = useState("");
  const [showOut, setShowOut] = useState(false);
  const [done, setDone] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setVisible(true); }, {threshold:0.3});
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    if (!visible || done) return;
    const s = steps[stepIdx];
    if (!s) { setDone(true); return; }
    setTyped(""); setShowOut(false);
    let i = 0;
    const sp = 20 + Math.random() * 25;
    const iv = setInterval(() => {
      i++; setTyped(s.cmd.slice(0, i));
      if (i >= s.cmd.length) {
        clearInterval(iv);
        setTimeout(() => setShowOut(true), 300);
        setTimeout(() => setStepIdx(p => p + 1), s.isMulti ? 2000 : 1400);
      }
    }, sp);
    return () => clearInterval(iv);
  }, [visible, stepIdx, done]);

  const s = steps[stepIdx];

  return (
    <section ref={ref} id="terminal" className="relative flex flex-col w-full bg-black py-16 px-6 lg:px-12 md:py-[80px] gap-10">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#00FF88]/40"/>Terminal</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">Una CLI. Miles de comercios.</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">Instala, autentícate y empieza a buscar en 3,400+ retailers VTEX desde la terminal.</p>
      </div>
      <div className="w-full max-w-[800px] bg-[#0A0A0A] border border-[#1A1A1A] overflow-x-auto font-mono text-[10px] sm:text-[11px] md:text-[12px] leading-[1.7]">
        <div className="flex items-center gap-2 px-4 py-2 bg-[#0F0F0F] border-b border-[#1A1A1A]">
          <div className="w-[10px] h-[10px] rounded-full bg-[#FF5F57]"/><div className="w-[10px] h-[10px] rounded-full bg-[#FEBC2E]"/><div className="w-[10px] h-[10px] rounded-full bg-[#28C840]"/>
          <span className="ml-3 text-[10px] text-[#555]">cli-market — bash</span>
        </div>
        <div className="p-4 sm:p-6 min-h-[360px] text-[#888]">
          {steps.slice(0, stepIdx).map((st, idx) => (
            <div key={idx} className="mb-3">
              <div className="break-all"><span className="text-[#555]">$</span> <span style={{color:st.color}}>{st.cmd}</span></div>
              {st.output && <div className="text-[10px] pl-4" style={{color:st.outColor}}>{st.output}</div>}
              {st.isMulti && st.results?.map((r,ri)=><div key={ri} className="pl-4 text-[10px]" style={{color:r.color}}>{r.text}</div>)}
            </div>
          ))}
          {!done && s && (
            <div className="mb-3">
              <div className="break-all"><span className="text-[#555]">$</span> <span style={{color:s.color}}>{typed}</span><span className="inline-block w-[7px] h-[13px] bg-[#00FF88] animate-pulse align-middle ml-[1px]"/></div>
              {showOut && s.output && <div className="text-[10px] pl-4" style={{color:s.outColor}}>{s.output}</div>}
              {showOut && s.isMulti && s.results?.map((r,ri)=><div key={ri} className="pl-4 text-[10px]" style={{color:r.color,animation:"fadeIn 0.3s ease-out"}}>{r.text}</div>)}
            </div>
          )}
          {done && <div><span className="text-[#555]">$</span> <span className="inline-block w-[7px] h-[13px] bg-[#00FF88] animate-pulse align-middle"/></div>}
        </div>
      </div>
      <p className="text-white/30 font-mono text-[10px] uppercase tracking-widest max-w-[800px]">OPEN SOURCE · MIT LICENSE · pip install · 3,400+ COMERCIOS · 67 PAÍSES</p>
    </section>
  );
}
