"use client";
import { useState, useEffect, useRef } from "react";
import { useLang } from "@/lib/LanguageContext";

const osData = [
  { label: "Linux / macOS", prompt: "$", install: "pip install git+https://github.com/Treevu-ai/cli-market-world.git", server: "market-server &" },
  { label: "PowerShell", prompt: ">", install: "pip install git+https://github.com/Treevu-ai/cli-market-world.git", server: 'Start-Process -NoNewWindow python -ArgumentList "-m", "market_server"' },
  { label: "CMD", prompt: ">", install: "pip install git+https://github.com/Treevu-ai/cli-market-world.git", server: "start python -m market_server" },
];

const stepDefs = [
  { cmd: "market login", color: "#00FF88", outKey: "terminal_step_login" },
  { cmd: 'market search "leche" --country PE', color: "#FF6B35", isMulti: true, results: [{text:"1. Leche Gloria 400ml  Wong  S/3.50",color:"#CCC"}]},
  { cmd: 'market compare "aceite"', color: "#4ADE80", isMulti: true, results: [{text:"Aceite Primor 1L → S/8.90 Wong 🇵🇪",color:"#888"},{text:"Aceite Natura 900ml → ARS 1,250 Carrefour 🇦🇷",color:"#888"},{text:"Aceite Liza 900ml → R$6.50 Carrefour BR 🇧🇷",color:"#888"}]},
  { cmd: "market add 1 --qty 2", color: "#F5F5F0", outKey: "terminal_step_add" },
  { cmd: "market checkout --payment yape", color: "#F5F5F0", outKey: "terminal_step_checkout" },
];

export default function TerminalSection() {
  const { t } = useLang();
  const [osIdx, setOsIdx] = useState(0);
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

  useEffect(() => { setStepIdx(0); setTyped(""); setShowOut(false); setDone(false); }, [osIdx]);

  useEffect(() => {
    if (!visible || done) return;
    const s = stepDefs[stepIdx];
    if (!s) { setDone(true); return; }
    setTyped(""); setShowOut(false);
    let i = 0; const sp = 15 + Math.random() * 20;
    const iv = setInterval(() => {
      i++; setTyped(s.cmd.slice(0, i));
      if (i >= s.cmd.length) { clearInterval(iv); setTimeout(() => setShowOut(true), 300); setTimeout(() => setStepIdx(p => p + 1), s.isMulti ? 1800 : 1200); }
    }, sp);
    return () => clearInterval(iv);
  }, [visible, stepIdx, done, osIdx]);

  const s = stepDefs[stepIdx];
  const os = osData[osIdx];

  return (
    <section ref={ref} id="terminal" className="relative flex flex-col w-full bg-[#060606] py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#00FF88]/40"/>{t("terminal_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">{t("terminal_subtitle")}</h2>
        <p className="text-white/50 font-mono text-sm leading-relaxed">{t("terminal_desc")}</p>
        <div className="flex gap-1 mt-1">
          {osData.map((o, i) => (
            <button key={i} onClick={() => setOsIdx(i)} className="px-3 py-1.5 text-[10px] font-mono border transition-colors cursor-pointer" style={{color: i===osIdx ? "#00FF88" : "#555", borderColor: i===osIdx ? "#00FF88" : "#1A1A1A", background: i===osIdx ? "rgba(0,255,136,0.05)" : "transparent" }}>{o.label}</button>
          ))}
        </div>
      </div>
      <div className="w-full max-w-[800px] bg-[#0A0A0A] border border-[#1A1A1A] overflow-x-auto font-mono text-[10px] sm:text-[11px] md:text-[12px] leading-[1.7]">
        <div className="flex items-center gap-2 px-4 py-2 bg-[#0F0F0F] border-b border-[#1A1A1A]">
          <div className="w-[10px] h-[10px] rounded-full bg-[#FF5F57]"/><div className="w-[10px] h-[10px] rounded-full bg-[#FEBC2E]"/><div className="w-[10px] h-[10px] rounded-full bg-[#28C840]"/>
          <span className="ml-3 text-[10px] text-[#555]">{t("terminal_cli_label")}</span>
        </div>
        <div className="p-4 sm:p-6 min-h-[380px] text-[#888]">
          <div className="mb-3">
            <span style={{color:os.prompt === "$" ? "#00FF88" : "#FF6B35"}}>{os.prompt} </span>
            {stepDefs.map((sd, i) => (
              <span key={i}>
                {stepIdx > i && <span className="text-[#666]">{sd.cmd}<br/>{os.prompt} </span>}
              </span>
            ))}
            {!done && <span style={{color: s?.color}}>{typed}{!showOut && <span className="inline-block w-[7px] h-[13px] bg-[#CCC] animate-pulse align-middle"/>}</span>}
            {done && <span className="text-[#555]">█</span>}
          </div>
          {stepDefs.slice(0, stepIdx).map((sd, i) => (
            <div key={i} className="mb-3">
              {sd.results && sd.results.map((r, j) => <div key={j} className="text-[#888]">{r.text}</div>)}
              {sd.outKey && <div className="text-[#444]">{t(sd.outKey)}</div>}
            </div>
          ))}
          {showOut && s?.results && s.results.map((r, j) => <div key={j} className="text-[#888]">{r.text}</div>)}
          {showOut && s?.outKey && <div className="text-[#444]">{t(s.outKey)}</div>}
          {done && <div><span className="text-[#555]">{os.prompt}</span> <span className="inline-block w-[7px] h-[13px] bg-[#00FF88] animate-pulse align-middle"/></div>}
        </div>
      </div>
      <p className="text-white/30 font-mono text-[10px] uppercase tracking-widest max-w-[800px]">{t("terminal_footer")}</p>
    </section>
  );
}
