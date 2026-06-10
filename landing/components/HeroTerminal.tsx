"use client";

import { useEffect, useRef } from "react";

const CMD1 = '$ market compare "arroz" --country PE';
const CMD2 = '$ market basket "arroz:1 leche:1 aceite:1" --country PE';
const OUT2 = "✓ CANASTA ÓPTIMA: metro_pe · S/ 24.10 · ahorro −S/ 3.45 (12.5%)";

const ROWS = [
  { lb: "Metro", pr: "S/ 2.90 /kg", w: 100, best: true },
  { lb: "Wong", pr: "S/ 3.10 /kg", w: 96, best: false },
  { lb: "Plaza Vea", pr: "S/ 3.25 /kg", w: 88, best: false },
] as const;

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

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

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
      for (const r of ROWS) {
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
        if (fill) fill.style.width = `${ROWS[i].w}%`;
      }
      await sleep(1050, reduced);
      if (cancelled || runId !== runIdRef.current) return;
      rowEls[0]?.classList.add("hero-term-row-tagged");

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
  }, [loop]);

  return (
    <div
      ref={rootRef}
      className={`hero-term-shell ${className}`.trim()}
      aria-label="CLI Market demo: price compare across retailers"
    />
  );
}
