"use client";
import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { AnimatedSphere } from "./AnimatedSphere";
import { useLang } from "@/lib/LanguageContext";

const words_es = ["comprar", "comparar", "buscar", "analizar"];
const words_en = ["purchase", "compare", "search", "analyze"];

function BlurWord({ word, trigger }: { word: string; trigger: number }) {
  const ref = useRef<HTMLSpanElement>(null);
  const letters = word.split("");
  const gc = ["#3cffd0", "#FFD600", "#FF6B35", "#60A5FA", "#3cffd0"];

  useEffect(() => {
    if (!ref.current) return;
    const ctx = gsap.context(() => {
      const spans = ref.current!.querySelectorAll("span");
      gsap.fromTo(spans,
        { opacity: 0, filter: "blur(20px)" },
        {
          opacity: 1, filter: "blur(0px)",
          duration: 0.5, stagger: 0.06, delay: 0.15,
          ease: "power3.out",
        }
      );
      // Apply gradient colors after animation starts
      spans.forEach((el, i) => {
        const ci = (i / Math.max(letters.length - 1, 1)) * (gc.length - 1);
        const lo = Math.floor(ci), up = Math.min(lo + 1, gc.length - 1), t2 = ci - lo;
        const hx = (h: string) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
        const [r1, g1, b1] = hx(gc[lo]), [r2, g2, b2] = hx(gc[up]);
        const r = Math.round(r1 + (r2 - r1) * t2), g = Math.round(g1 + (g2 - g1) * t2), b = Math.round(b1 + (b2 - b1) * t2);
        gsap.set(el, { color: `rgb(${r},${g},${b})` });
      });
    }, ref);
    return () => ctx.revert();
  }, [trigger]);

  return (
    <span ref={ref} className="relative inline-block">
      {letters.map((c, i) => (
        <span key={i} className="inline-block align-baseline">{c}</span>
      ))}
    </span>
  );
}

export default function Hero() {
  const { lang, t: _t } = useLang();
  const words = lang === "es" ? words_es : words_en;
  const [wordIdx, setWordIdx] = useState(0);
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const i = setInterval(() => setWordIdx(p => (p + 1) % words.length), 2500);
    return () => clearInterval(i);
  }, []);

  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
      tl.fromTo(".hero-eyebrow", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7 })
        .fromTo(".hero-h1", { opacity: 0, y: 32 }, { opacity: 1, y: 0, duration: 1 }, "-=0.4")
        .fromTo(".hero-sub", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.7 }, "-=0.5")
        .fromTo(".hero-ph", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.6 }, "-=0.4")
        .fromTo(".hero-cta", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.6 }, "-=0.3");
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  return (
    <section ref={sectionRef} className="relative min-h-screen flex flex-col justify-center items-start overflow-hidden bg-[#131313]">
      <div className="absolute inset-0 z-0 parallax-bg">
        <div className="absolute inset-0 bg-gradient-to-br from-[#131313] via-black to-[#131313]" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)", backgroundSize: "64px 64px" }} />
      </div>
      <div className="absolute inset-0 z-[2] overflow-hidden pointer-events-none opacity-[0.08]">
        {[...Array(6)].map((_, i) => <div key={`h${i}`} className="absolute h-px bg-white/10" style={{ top: `${14.28 * (i + 1)}%`, left: 0, right: 0 }} />)}
        {[...Array(10)].map((_, i) => <div key={`v${i}`} className="absolute w-px bg-white/10" style={{ left: `${9.09 * (i + 1)}%`, top: 0, bottom: 0 }} />)}
      </div>
      <div className="hidden xl:block absolute right-0 top-1/2 -translate-y-1/2 w-[600px] h-[600px] xl:w-[800px] xl:h-[800px] opacity-20 pointer-events-none parallax-sphere">
        <AnimatedSphere />
      </div>
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-[#3cffd0]/[0.02] blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 w-full max-w-[1200px] mx-auto px-6 lg:px-12 py-32 lg:py-40">
        <div className="lg:max-w-[65%]">
          <div className="hero-eyebrow mb-8">
            <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40">
              <span className="w-8 h-px bg-[#3cffd0]/40" />
              {_t("hero_eye")}
            </span>
          </div>
          <div className="mb-12">
            <h1 className="hero-h1 text-left text-[clamp(2rem,5.5vw,6rem)] font-grotesk leading-[0.92] tracking-tight text-white">
              <span className="block"><span className="text-[clamp(3rem,8vw,10rem)] leading-[0.85] block">60</span> {_t("hero_h1a").replace("27 ", "").replace("27+ ", "").replace("30 ", "").replace("38 ", "")}</span>
              <span className="block">{_t("hero_h1b")}</span>
              <span className="block">{_t("hero_h1c_p")}{" "}
                <BlurWord word={words[wordIdx]} trigger={wordIdx} />
                {" "}{_t("hero_h1c_s")}
              </span>
            </h1>
          </div>
          <div className="hero-sub mb-12">
            <p className="text-lg lg:text-xl text-white/50 leading-relaxed max-w-xl font-mono">{_t("hero_sub")}</p>
          </div>
          <div className="hero-ph mb-6">
            <a href="https://www.producthunt.com/products/cli-market?embed=true&utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-cli-market" target="_blank" rel="noopener">
              <img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1150344&theme=neutral&t=1779222495059" alt="CLI Market on Product Hunt" className="h-[54px] w-auto" />
            </a>
          </div>
          <div className="hero-cta flex flex-col sm:flex-row gap-4">
            <a href="https://github.com/Treevu-ai/cli-market-world" className="inline-flex items-center gap-2 px-8 py-4 bg-[#3cffd0] text-black font-medium hover:bg-[#309875] transition-colors text-sm font-mono uppercase tracking-widest">{_t("hero_install")}<span className="text-xs opacity-60">→</span></a>
            <a href="#coverage" className="inline-flex items-center gap-2 px-8 py-4 border border-white/10 text-white font-medium hover:bg-white/5 transition-colors text-sm font-mono uppercase tracking-widest">{_t("hero_cov")}</a>
            <a href="mailto:hello@cli-market.dev?subject=CLI%20Market&body=Hola%2C%20me%20interesa%20saber%20mas." className="inline-flex items-center gap-2 px-8 py-4 border border-white/10 text-white/60 hover:text-white hover:border-white/30 transition-colors text-sm font-mono uppercase tracking-widest">{_t("hero_contact")}</a>
          </div>
        </div>
      </div>
    </section>
  );
}
