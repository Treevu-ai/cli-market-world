"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AnimatedSphere } from "./AnimatedSphere";
import { useLang } from "@/lib/LanguageContext";

const words_es = ["comprar", "comparar", "buscar", "analizar"];
const words_en = ["purchase", "compare", "search", "analyze"];

function BlurWord({ word, trigger }: { word: string; trigger: number }) {
  const letters = word.split("");
  const gc = ["#3cffd0", "#FFD600", "#FF6B35", "#60A5FA", "#3cffd0"];

  return (
    <span className="relative inline-block">
      {letters.map((c, i) => {
        const ci = (i / Math.max(letters.length - 1, 1)) * (gc.length - 1);
        const lo = Math.floor(ci), up = Math.min(lo + 1, gc.length - 1), t = ci - lo;
        const hx = (h: string) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
        const [r1, g1, b1] = hx(gc[lo]), [r2, g2, b2] = hx(gc[up]);
        const r = Math.round(r1 + (r2 - r1) * t), g = Math.round(g1 + (g2 - g1) * t), b = Math.round(b1 + (b2 - b1) * t);
        return (
          <motion.span
            key={trigger + "-" + i}
            className="inline-block align-baseline"
            initial={{ opacity: 0, filter: "blur(20px)" }}
            animate={{ opacity: 1, filter: "blur(0px)", color: `rgb(${r},${g},${b})` }}
            transition={{ duration: 0.5, delay: 0.2 + i * 0.06, ease: [0.22, 1, 0.36, 1] }}
          >
            {c}
          </motion.span>
        );
      })}
    </span>
  );
}

export default function Hero() {
  const { lang, t: _t } = useLang();
  const words = lang === "es" ? words_es : words_en;
  const [visible, setVisible] = useState(false);
  const [wordIdx, setWordIdx] = useState(0);
  useEffect(() => { setVisible(true); }, []);
  useEffect(() => { const i = setInterval(() => setWordIdx(p => (p + 1) % words.length), 2500); return () => clearInterval(i); }, []);

  return (
    <section className="relative min-h-screen flex flex-col justify-center items-start overflow-hidden bg-[#131313]">
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-[#131313] via-black to-[#131313]" />
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)", backgroundSize: "64px 64px" }} />
      </div>
      <div className="absolute inset-0 z-[2] overflow-hidden pointer-events-none opacity-[0.08]">
        {[...Array(6)].map((_, i) => <div key={`h${i}`} className="absolute h-px bg-white/10" style={{ top: `${14.28 * (i + 1)}%`, left: 0, right: 0 }} />)}
        {[...Array(10)].map((_, i) => <div key={`v${i}`} className="absolute w-px bg-white/10" style={{ left: `${9.09 * (i + 1)}%`, top: 0, bottom: 0 }} />)}
      </div>
      <div className="hidden xl:block absolute right-0 top-1/2 -translate-y-1/2 w-[600px] h-[600px] xl:w-[800px] xl:h-[800px] opacity-20 pointer-events-none">
        <AnimatedSphere />
      </div>
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-[#3cffd0]/[0.02] blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 w-full max-w-[1200px] mx-auto px-6 lg:px-12 py-32 lg:py-40">
        <div className="lg:max-w-[65%]">
          <motion.div
            className="mb-8"
            initial={{ opacity: 0, y: 12 }}
            animate={visible ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40">
              <span className="w-8 h-px bg-[#3cffd0]/40" />
              {_t("hero_eye")}
            </span>
          </motion.div>
          <div className="mb-12">
            <motion.h1
              className="text-left text-[clamp(2rem,5.5vw,6rem)] font-grotesk leading-[0.92] tracking-tight text-white"
              initial={{ opacity: 0, y: 24 }}
              animate={visible ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 1, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            >
              <span className="block"><span className="text-[clamp(3rem,8vw,10rem)] leading-[0.85] block">30</span> {_t("hero_h1a").replace("27 ", "").replace("27+ ", "").replace("30 ", "")}</span>
              <span className="block">{_t("hero_h1b")}</span>
              <span className="block">{_t("hero_h1c_p")}{" "}
                <BlurWord word={words[wordIdx]} trigger={wordIdx} />
                {" "}{_t("hero_h1c_s")}
              </span>
            </motion.h1>
          </div>
          <motion.div className="mb-12" initial={{ opacity: 0, y: 12 }} animate={visible ? { opacity: 1, y: 0 } : {}} transition={{ duration: 0.7, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}>
            <p className="text-lg lg:text-xl text-white/50 leading-relaxed max-w-xl font-mono">{_t("hero_sub")}</p>
          </motion.div>
          <motion.div className="mb-6" initial={{ opacity: 0, y: 12 }} animate={visible ? { opacity: 1, y: 0 } : {}} transition={{ duration: 0.7, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}>
            <a href="https://www.producthunt.com/products/cli-market?embed=true&utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-cli-market" target="_blank" rel="noopener">
              <img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1150344&theme=neutral&t=1779222495059" alt="CLI Market on Product Hunt" className="h-[54px] w-auto" />
            </a>
          </motion.div>
          <motion.div className="flex flex-col sm:flex-row gap-4" initial={{ opacity: 0, y: 12 }} animate={visible ? { opacity: 1, y: 0 } : {}} transition={{ duration: 0.7, delay: 0.5, ease: [0.22, 1, 0.36, 1] }}>
            <a href="https://github.com/Treevu-ai/cli-market-world" className="inline-flex items-center gap-2 px-8 py-4 bg-[#3cffd0] text-black font-medium hover:bg-[#309875] transition-colors text-sm font-mono uppercase tracking-widest">{_t("hero_install")}<span className="text-xs opacity-60">→</span></a>
            <a href="#coverage" className="inline-flex items-center gap-2 px-8 py-4 border border-white/10 text-white font-medium hover:bg-white/5 transition-colors text-sm font-mono uppercase tracking-widest">{_t("hero_cov")}</a>
            <a href="mailto:hello@cli-market.dev?subject=CLI%20Market&body=Hola%2C%20me%20interesa%20saber%20mas." className="inline-flex items-center gap-2 px-8 py-4 border border-white/10 text-white/60 hover:text-white hover:border-white/30 transition-colors text-sm font-mono uppercase tracking-widest">{_t("hero_contact")}</a>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
