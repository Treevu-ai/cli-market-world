"use client";

import { useEffect, useRef, useState } from "react";
import { API_URL } from "@/lib/api";
import { storeLabel } from "@/lib/storeLabels";

const CMD1 = '$ market compare "arroz" --country PE';
const CMD2 = '$ market basket "arroz:1 leche:1 aceite:1" --country PE';
const OUT2 = "✓ CANASTA ÓPTIMA: metro_pe · S/ 24.10 · ahorro −S/ 3.45 (12.5%)";

type TermRow = { lb: string; pr: string; w: number; best: boolean };

const FALLBACK_ROWS: TermRow[] = [
  { lb: "Metro", pr: "S/ 2.90", w: 100, best: true },
  { lb: "Wong", pr: "S/ 3.10", w: 96, best: false },
  { lb: "Plaza Vea", pr: "S/ 3.25", w: 88, best: false },
];

function rowsFromCompare(prices: Record<string, number>): TermRow[] {
  const entries = Object.entries(prices)
    .filter(([, p]) => p > 0)
    .sort((a, b) => a[1] - b[1]);
  if (entries.length < 2) return FALLBACK_ROWS;
  const max = entries[entries.length - 1][1];
  const bestStore = entries[0][0];
  return entries.slice(0, 3).map(([store, price]) => ({
    lb: storeLabel(store),
    pr: `S/ ${price.toFixed(2)}`,
    w: max > 0 ? Math.round((price / max) * 100) : 100,
    best: store === bestStore,
  }));
}

function sleep(ms: number, reduced: boolean) {
  return new Promise<void>((resolve) => {
    window.setTimeout(resolve, reduced ? 0 : ms);
  });
}

type HeroTerminalProps = {
  className?: string;
  /** When false, animation does not restart (e.g. live playground mode). */
  loop?: boolean;
};

export default function HeroTerminal({ className = "", loop = true }: HeroTerminalProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const runIdRef = useRef(0);
  const [rows, setRows] = useState<TermRow[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      let next = FALLBACK_ROWS;
      try {
        const res = await fetch(`${API_URL}/public/demo/compare?q=arroz`);
        const data = await res.json();
        if (!cancelled && res.ok) {
          const prices = data?.comparison?.[0]?.prices as Record<string, number> | undefined;
          if (prices && Object.keys(prices).length >= 2) {
            next = rowsFromCompare(prices);
          }
        }
      } catch {
        /* fallback */
      }
      if (!cancelled) setRows(next);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const root = rootRef.current;
    if (!root || !rows) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const runId = ++runIdRef.current;
    let cancelled = false;

    const line = (cls?: string) => {
      const d = document.createElement("div");
      d.className = `hero-term-line${cls ? ` ${cls}` : ""}`;
      root.appendChild(d);
      return d;
    };

    const cursorEl = () => {
      const c = document.createElement("span");
      c.className = "hero-term-cursor";
      c.setAttribute("aria-hidden", "true");
      return c;
    };

    const type = async (target: HTMLElement, text: string, totalMs: number) => {
      const per = text.length ? totalMs / text.length : 0;
      const cur = cursorEl();
      target.appendChild(cur);
      for (const ch of text) {
        if (cancelled || runId !== runIdRef.current) return;
        cur.insertAdjacentText("beforebegin", ch);
        await sleep(per, reduced);
      }
      cur.remove();
    };

    const run = async () => {
      root.innerHTML = "";

      const l0 = line();
      l0.appendChild(cursorEl());
      await sleep(1500, reduced);
      if (cancelled || runId !== runIdRef.current) return;
      l0.remove();

      const l1 = line("hero-term-cmd");
      await type(l1, CMD1, 1500);
      if (cancelled || runId !== runIdRef.current) return;

      const rowEls: HTMLDivElement[] = [];
      for (const r of rows) {
        const row = document.createElement("div");
        row.className = `hero-term-row${r.best ? " hero-term-row-best" : ""}`;
        row.innerHTML =
          `<span class="hero-term-lb">${r.lb}</span>` +
          `<div class="hero-term-track"><div class="hero-term-fill"></div></div>` +
          `<span class="hero-term-price">${r.pr}${r.best ? '<span class="hero-term-tag">✓ MEJOR</span>' : ""}</span>`;
        root.appendChild(row);
        rowEls.push(row);
      }
      for (let i = 0; i < rowEls.length; i++) {
        await sleep(i ? 140 : 60, reduced);
        if (cancelled || runId !== runIdRef.current) return;
        rowEls[i].classList.add("hero-term-row-on");
        const fill = rowEls[i].querySelector<HTMLElement>(".hero-term-fill");
        if (fill) fill.style.width = `${rows[i].w}%`;
      }
      await sleep(1050, reduced);
      if (cancelled || runId !== runIdRef.current) return;
      const bestIdx = rows.findIndex((r) => r.best);
      if (bestIdx >= 0) rowEls[bestIdx]?.classList.add("hero-term-row-tagged");

      await sleep(450, reduced);
      if (cancelled || runId !== runIdRef.current) return;

      const l2 = line("hero-term-cmd");
      await type(l2, CMD2, 1500);
      if (cancelled || runId !== runIdRef.current) return;

      await sleep(120, reduced);
      const l3 = line("hero-term-out");
      l3.textContent = OUT2;
      const l4 = line("hero-term-cmd");
      l4.textContent = "$ ";
      l4.appendChild(cursorEl());
      await sleep(1380, reduced);
      if (cancelled || runId !== runIdRef.current) return;

      if (loop) run();
    };

    void run();

    return () => {
      cancelled = true;
      runIdRef.current += 1;
    };
  }, [loop, rows]);

  return (
    <div
      ref={rootRef}
      className={`hero-term-shell ${className}`.trim()}
      aria-label="CLI Market demo: price compare across retailers"
    />
  );
}
