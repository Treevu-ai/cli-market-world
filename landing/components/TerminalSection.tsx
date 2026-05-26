"use client";
import { useLang } from "@/lib/LanguageContext";

export default function TerminalSection() {
  const { t: _t, lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="terminal" className="relative bg-[var(--wise-ink)] py-24">
      <div className="max-w-[720px] mx-auto px-6 text-center">
        <p className="text-xs text-[var(--wise-mute)] font-medium uppercase tracking-[0.15em] mb-8">
          {isES ? "Terminal" : "Terminal"}
        </p>
        <h2 className="text-[24px] font-medium text-white mb-3 tracking-tight">
          {isES ? "Pruébalo ahora mismo. En tu terminal." : "Try it now. In your terminal."}
        </h2>
        <p className="text-sm text-[var(--wise-body)] max-w-md mx-auto mb-12">
          {isES ? "Search, Compare, Cart y Checkout. Todo desde la línea de comandos." : "Search, Compare, Cart, and Checkout. All from the command line."}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
          {[
            { title: "Search", cmd: "market search \"leche\" --country PE", out: "Wong S/4.20 · Metro S/3.90 · Plaza Vea S/4.50" },
            { title: "Compare", cmd: "market compare \"arroz\"", out: isES ? "Mejor: Metro S/2.80 · Ahorro: S/0.70/unidad" : "Best: Metro S/2.80 · Savings: S/0.70/unit" },
            { title: "Cart", cmd: "market basket leche:2 arroz:1", out: isES ? "Canasta comparada en 3 tiendas · Metro S/11.70" : "Basket compared in 3 stores · Metro S/11.70" },
            { title: "Checkout", cmd: "market checkout --payment yape", out: isES ? "✓ Orden ORD-A7F3B91C · QR Yape generado" : "✓ Order ORD-A7F3B91C · Yape QR generated" },
          ].map((cell) => (
            <div key={cell.title} className="bg-[#1a1d19] rounded-3xl p-4 border border-[#2a2d25] text-left">
              <div className="flex items-center gap-1.5 mb-3">
                <span className="w-2 h-2 rounded-full bg-[#d03238]" />
                <span className="w-2 h-2 rounded-full bg-[#ffd11a]" />
                <span className="w-2 h-2 rounded-full bg-[#2ead4b]" />
                <span className="text-[10px] text-[var(--wise-mute)] font-mono ml-2">{cell.title}</span>
              </div>
              <p className="text-xs text-[var(--wise-green)] font-mono mb-2">$ {cell.cmd}</p>
              <p className="text-[11px] text-[var(--wise-body)] font-mono">{cell.out}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
