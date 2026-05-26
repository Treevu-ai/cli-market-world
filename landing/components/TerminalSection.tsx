"use client";
import { useState, useEffect, useRef } from "react";
import { motion, useInView } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";

type CmdLine = { text: string; color?: string; delay: number };

const cells_es = [
  { title: "Search", lines: [
    { text: "$ market search \"leche\" --country PE", delay: 300 },
    { text: "Wong ......... S/ 4.20", color: "text-[#27c93f]", delay: 800 },
    { text: "Metro ........ S/ 3.90", color: "text-[#27c93f]", delay: 1000 },
    { text: "Plaza Vea ..... S/ 4.50", color: "text-[#27c93f]", delay: 1200 },
    { text: "▸ 3 resultados en 1.2s", color: "text-[#868685]", delay: 1500 },
  ]},
  { title: "Compare", lines: [
    { text: "$ market compare \"arroz\"", delay: 300 },
    { text: "Mejor precio: Metro (S/ 2.80)", color: "text-[#27c93f]", delay: 800 },
    { text: "Precio máx: Wong (S/ 3.50)", color: "text-[#ff5f56]", delay: 1000 },
    { text: "▸ Ahorro: S/ 0.70 por unidad", color: "text-[#868685]", delay: 1300 },
  ]},
  { title: "Cart", lines: [
    { text: "$ market basket leche:2 arroz:1", delay: 300 },
    { text: "▸ Canasta comparada en 3 tiendas", color: "text-[#868685]", delay: 600 },
    { text: "Metro ....... S/ 11.70 total", color: "text-[#27c93f]", delay: 900 },
    { text: "Wong ........ S/ 12.30 total", color: "text-[#ffbd2e]", delay: 1100 },
    { text: "Plaza Vea ... S/ 13.20 total", color: "text-[#ffbd2e]", delay: 1300 },
  ]},
  { title: "Checkout", lines: [
    { text: "$ market checkout --payment yape", delay: 300 },
    { text: "▸ Orden ORD-A7F3B91C creada", color: "text-[#27c93f]", delay: 700 },
    { text: "▸ QR Yape generado", color: "text-[#868685]", delay: 900 },
    { text: "▸ Escanea para completar el pago", color: "text-[#868685]", delay: 1100 },
  ]},
];

const cells_en = [
  { title: "Search", lines: [
    { text: "$ market search \"milk\" --country PE", delay: 300 },
    { text: "Wong ......... S/ 4.20", color: "text-[#27c93f]", delay: 800 },
    { text: "Metro ........ S/ 3.90", color: "text-[#27c93f]", delay: 1000 },
    { text: "Plaza Vea ..... S/ 4.50", color: "text-[#27c93f]", delay: 1200 },
    { text: "▸ 3 results in 1.2s", color: "text-[#868685]", delay: 1500 },
  ]},
  { title: "Compare", lines: [
    { text: "$ market compare \"rice\"", delay: 300 },
    { text: "Best price: Metro (S/ 2.80)", color: "text-[#27c93f]", delay: 800 },
    { text: "Max price: Wong (S/ 3.50)", color: "text-[#ff5f56]", delay: 1000 },
    { text: "▸ Savings: S/ 0.70 per unit", color: "text-[#868685]", delay: 1300 },
  ]},
  { title: "Cart", lines: [
    { text: "$ market basket milk:2 rice:1", delay: 300 },
    { text: "▸ Basket compared in 3 stores", color: "text-[#868685]", delay: 600 },
    { text: "Metro ....... S/ 11.70 total", color: "text-[#27c93f]", delay: 900 },
    { text: "Wong ........ S/ 12.30 total", color: "text-[#ffbd2e]", delay: 1100 },
    { text: "Plaza Vea ... S/ 13.20 total", color: "text-[#ffbd2e]", delay: 1300 },
  ]},
  { title: "Checkout", lines: [
    { text: "$ market checkout --payment yape", delay: 300 },
    { text: "▸ Order ORD-A7F3B91C created", color: "text-[#27c93f]", delay: 700 },
    { text: "▸ Yape QR generated", color: "text-[#868685]", delay: 900 },
    { text: "▸ Scan to complete payment", color: "text-[#868685]", delay: 1100 },
  ]},
];

function MiniTerminal({ title, lines }: { title: string; lines: CmdLine[] }) {
  const [visibleLines, setVisibleLines] = useState<number[]>([]);
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });

  useEffect(() => {
    if (!inView) return;
    lines.forEach((line, i) => {
      const t = setTimeout(() => setVisibleLines(prev => [...prev, i]), line.delay);
      return () => clearTimeout(t);
    });
  }, [inView, lines]);

  return (
    <div ref={ref} className="bg-[#e8ebe6] border border-[#c5edab] rounded-lg p-4 min-h-[140px]">
      <div className="flex items-center gap-1.5 mb-3 pb-2 border-b border-[#fafafa]">
        <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56]" />
        <span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e]" />
        <span className="w-2.5 h-2.5 rounded-full bg-[#27c93f]" />
        <span className="text-[10px] text-[#868685] font-mono ml-2 uppercase tracking-wider">{title}</span>
      </div>
      <div className="font-mono text-[11px] leading-relaxed space-y-0.5">
        {lines.map((line, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0 }}
            animate={visibleLines.includes(i) ? { opacity: 1 } : {}}
            transition={{ duration: 0.3 }}
            className={line.color || "text-[#454745]"}
          >
            {line.text}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default function TerminalSection() {
  const { t: _t, lang } = useLang();
  const isES = lang === "es";
  const cells = isES ? cells_es : cells_en;

  return (
    <section id="terminal" className="relative bg-[#e8ebe6] py-20 border-t border-[#c5edab]">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[#868685] font-mono uppercase tracking-[0.15em] mb-8">{_t("terminal_label")}</p>
        <h2 className="text-[24px] font-medium text-[#0e0f0c] mb-3 tracking-tight">{_t("terminal_title")}</h2>
        <p className="text-sm text-[#454745] max-w-md mx-auto mb-12">{_t("terminal_desc")}</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
          {cells.map((cell) => (
            <MiniTerminal key={cell.title} title={cell.title} lines={cell.lines} />
          ))}
        </div>
        <p className="mt-8 text-[10px] text-[#868685] font-mono uppercase tracking-[0.15em]">{_t("terminal_footer")}</p>
      </div>
    </section>
  );
}
