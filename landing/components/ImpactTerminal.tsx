"use client";

import { useEffect, useRef } from "react";
import { useLang } from "@/lib/LanguageContext";

type BarRow = { store: string; price: string; width: number; best: boolean };

export default function ImpactTerminal() {
  const { lang } = useLang();
  const isES = lang === "es";
  const bodyRef = useRef<HTMLDivElement>(null);
  const ranRef = useRef(false);

  useEffect(() => {
    const body = bodyRef.current;
    if (!body || ranRef.current) return;
    ranRef.current = true;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const sleep = (ms: number) =>
      new Promise<void>((r) => setTimeout(r, reduced ? 0 : ms));

    const el = (html: string) => {
      const d = document.createElement("div");
      d.className = "impact-term-line";
      d.innerHTML = html;
      body.appendChild(d);
      return d;
    };

    const typeCmd = async (text: string) => {
      const line = el(
        '<span class="impact-term-prompt">agente@latam</span><span class="impact-term-dim"> ~ $ </span><span class="impact-term-cmd"></span><span class="impact-term-cursor"></span>'
      );
      const cmd = line.querySelector(".impact-term-cmd");
      if (!cmd) return;
      for (const ch of text) {
        cmd.textContent = (cmd.textContent ?? "") + ch;
        await sleep(34 + Math.random() * 40);
      }
      line.querySelector(".impact-term-cursor")?.remove();
    };

    const run = async () => {
      body.innerHTML = "";
      await sleep(900);
      await typeCmd('market compare "aceite de girasol 900ml" --country PE');
      await sleep(350);
      el(
        `<span class="impact-term-dim">→ ${isES ? "consultando retailers verificados · normalizando /L …" : "querying verified retailers · normalizing /L …"}</span>`
      );
      await sleep(700);

      const rows: BarRow[] = [
        { store: "plaza_vea", price: "S/ 19.20", width: 100, best: false },
        { store: "wong", price: "S/ 18.90", width: 98, best: false },
        { store: "metro", price: "S/ 17.40", width: 90, best: true },
      ];

      for (const r of rows) {
        const row = document.createElement("div");
        row.className = "impact-term-bar-row impact-term-line";
        row.innerHTML = `<span class="${r.best ? "impact-term-accent" : "impact-term-dim"}">${r.store}</span>
          <div class="impact-term-bar-track"><div class="impact-term-bar-fill ${r.best ? "impact-term-bar-fill-best" : ""}"></div></div>
          <span class="impact-term-bar-price"><b>${r.price}</b> /L</span>`;
        body.appendChild(row);
        await sleep(60);
        const fill = row.querySelector(".impact-term-bar-fill") as HTMLElement | null;
        if (fill) fill.style.width = `${r.width}%`;
        await sleep(280);
      }

      await sleep(400);
      el(
        `<span class="impact-term-best">${isES ? "✓ MEJOR PRECIO: metro · S/ 17.40/L · spread 10.3% · refresh hace 1h 12m" : "✓ BEST PRICE: metro · S/ 17.40/L · spread 10.3% · refresh 1h 12m ago"}</span>`
      );
      await sleep(900);
      await typeCmd('market basket "arroz:1 aceite:1 leche:1" --country PE');
      await sleep(500);
      el(
        `<span class="impact-term-dim">→ ${isES ? "canasta óptima: " : "optimal basket: "}</span><span class="impact-term-accent">metro_pe · S/ 24.10 total</span><span class="impact-term-dim"> · ${isES ? "ahorro vs peor cadena: " : "savings vs worst chain: "}</span><span class="impact-term-best">−S/ 3.45 (12.5%)</span>`
      );
      await sleep(300);
      el(
        '<span class="impact-term-prompt">agente@latam</span><span class="impact-term-dim"> ~ $ </span><span class="impact-term-cursor"></span>'
      );
    };

    run();
  }, [isES]);

  return (
    <div className="impact-term">
      <div className="impact-term-bar-chrome">
        <i aria-hidden="true" />
        <i aria-hidden="true" />
        <i aria-hidden="true" />
        <span>{isES ? "cli-market — agente conectado vía MCP" : "cli-market — agent connected via MCP"}</span>
      </div>
      <div ref={bodyRef} className="impact-term-body" />
    </div>
  );
}
