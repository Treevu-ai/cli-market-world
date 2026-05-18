"use client";
import { useEffect, useState } from "react";
import { AnimatedSphere } from "./AnimatedSphere";

const words = ["comprar", "comparar", "buscar", "analizar"];

function BlurWord({ word, trigger }: { word: string; trigger: number }) {
  const letters = word.split("");
  const [states, setStates] = useState<{o:number;b:number}[]>(letters.map(()=>({o:0,b:20})));
  const [gradient, setGradient] = useState(true);
  useEffect(() => {
    setStates(letters.map(()=>({o:0,b:20}))); setGradient(true);
    const timers: ReturnType<typeof setTimeout>[] = [];
    letters.forEach((_,i)=>{timers.push(setTimeout(()=>{const start=performance.now();const tick=(n:number)=>{const p=Math.min((n-start)/500,1);const e=1-Math.pow(1-p,3);setStates(s=>{const ns=[...s];ns[i]={o:e,b:20*(1-e)};return ns});if(p<1)requestAnimationFrame(tick)};requestAnimationFrame(tick)},i*45))});
    timers.push(setTimeout(()=>setGradient(false),45*letters.length+500+200));
    return ()=>timers.forEach(clearTimeout);
  },[trigger]);
  const gc=["#00FF88","#FFD600","#FF6B35","#60A5FA","#00FF88"];
  return <>{letters.map((c,i)=>{const ci=(i/Math.max(letters.length-1,1))*(gc.length-1);const lo=Math.floor(ci),up=Math.min(lo+1,gc.length-1),t=ci-lo;const hx=(h:string)=>[parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)];const[r1,g1,b1]=hx(gc[lo]),[r2,g2,b2]=hx(gc[up]);const r=Math.round(r1+(r2-r1)*t),g=Math.round(g1+(g2-g1)*t),b=Math.round(b1+(b2-b1)*t);return <span key={i} style={{display:"inline-block",opacity:states[i]?.o??0,filter:`blur(${states[i]?.b??20}px)`,color:gradient?`rgb(${r},${g},${b})`:"white",transition:"color 0.4s ease"}}>{c}</span>})}</>;
}

export default function Hero() {
  const [visible, setVisible] = useState(false);
  const [wordIdx, setWordIdx] = useState(0);
  useEffect(()=>{setVisible(true)},[]);
  useEffect(()=>{const i=setInterval(()=>setWordIdx(p=>(p+1)%words.length),2500);return ()=>clearInterval(i)},[]);

  return (
    <section className="relative min-h-screen flex flex-col justify-center items-start overflow-hidden bg-black">
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-[#0A0A0A] via-black to-[#0A0A0A]" />
        <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage:"linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",backgroundSize:"64px 64px"}} />
      </div>
      <div className="absolute inset-0 z-[2] overflow-hidden pointer-events-none opacity-[0.08]">
        {[...Array(6)].map((_,i)=><div key={`h${i}`} className="absolute h-px bg-white/10" style={{top:`${14.28*(i+1)}%`,left:0,right:0}}/>)}
        {[...Array(10)].map((_,i)=><div key={`v${i}`} className="absolute w-px bg-white/10" style={{left:`${9.09*(i+1)}%`,top:0,bottom:0}}/>)}
      </div>
      <div className="absolute right-0 top-1/2 -translate-y-1/2 w-[600px] h-[600px] lg:w-[800px] lg:h-[800px] opacity-30 pointer-events-none">
        <AnimatedSphere />
      </div>
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-[#00FF88]/[0.02] blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 w-full max-w-[1200px] mx-auto px-6 lg:px-12 py-32 lg:py-40">
        <div className="lg:max-w-[65%]">
          <div className={`mb-8 transition-all duration-700 ${visible?"opacity-100 translate-y-0":"opacity-0 translate-y-4"}`}>
            <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40">
              <span className="w-8 h-px bg-[#00FF88]/40" />
              Infraestructura de comercio para agentes de IA · LATAM y global
            </span>
          </div>
          <div className="mb-12">
            <h1 className={`text-left text-[clamp(2rem,5.5vw,6rem)] font-grotesk leading-[0.92] tracking-tight text-white transition-all duration-1000 ${visible?"opacity-100 translate-y-0":"opacity-0 translate-y-8"}`}>
              <span className="block">1000+ retailers.</span>
              <span className="block">Una sola API.</span>
              <span className="block">Tus agentes pueden{" "}
                <span className="relative inline-block"><BlurWord word={words[wordIdx]} trigger={wordIdx} /></span>
                {" "}solos.
              </span>
            </h1>
          </div>
          <div className={`mb-12 transition-all duration-700 delay-300 ${visible?"opacity-100 translate-y-0":"opacity-0 translate-y-4"}`}>
            <p className="text-lg lg:text-xl text-white/50 leading-relaxed max-w-xl font-mono">
              Conectamos agentes de inteligencia artificial con 1000+ comercios VTEX en 44 países. Buscar, comparar y comprar — todo desde la terminal o vía API.
            </p>
          </div>
          <div className={`flex flex-col sm:flex-row gap-4 transition-all duration-700 delay-500 ${visible?"opacity-100 translate-y-0":"opacity-0 translate-y-4"}`}>
            <a href="https://github.com/Treevu-ai/cli-market-latam" className="inline-flex items-center gap-2 px-8 py-4 bg-[#00FF88] text-black font-medium hover:bg-[#00cc6a] transition-colors text-sm font-mono uppercase tracking-widest">Instalar CLI<span className="text-xs opacity-60">→</span></a>
            <a href="#coverage" className="inline-flex items-center gap-2 px-8 py-4 border border-white/10 text-white font-medium hover:bg-white/5 transition-colors text-sm font-mono uppercase tracking-widest">Ver cobertura</a>
            <a href="https://t.me/climarketbot" className="inline-flex items-center gap-2 px-8 py-4 border border-white/10 text-white/60 hover:text-white hover:border-white/30 transition-colors text-sm font-mono uppercase tracking-widest">Contactar</a>
          </div>
        </div>
      </div>

      <div className={`absolute bottom-12 left-0 right-0 px-6 lg:px-12 transition-all duration-700 delay-500 ${visible?"opacity-100":"opacity-0"}`}>
        <div className="max-w-[1200px] mx-auto flex flex-wrap items-start gap-6 sm:gap-10 lg:gap-20">
          {[{value:"3200+",label:"retailers VTEX activos"},{value:"67",label:"países en LATAM, Europa y global"},{value:"12",label:"líneas de negocio"},{value:"12",label:"herramientas MCP"}].map(s=>(
            <div key={s.label} className="flex flex-col gap-2"><span className="text-3xl lg:text-4xl font-grotesk font-bold text-white">{s.value}</span><span className="text-xs text-white/30 leading-tight font-mono uppercase tracking-wider">{s.label}</span></div>
          ))}</div>
      </div>
    </section>
  );
}
