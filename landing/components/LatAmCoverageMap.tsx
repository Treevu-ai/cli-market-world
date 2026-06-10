"use client";

import { useEffect, useRef } from "react";
import { useLang } from "@/lib/LanguageContext";

const POLYS: number[][][] = [
  [
    [6, 3],
    [20, 2],
    [30, 8],
    [27, 13],
    [19, 11],
    [13, 16],
    [7, 11],
  ],
  [
    [27, 13],
    [35, 21],
    [39, 27],
    [35, 28],
    [28, 19],
    [24, 15],
  ],
  [
    [39, 27],
    [50, 24],
    [60, 29],
    [68, 37],
    [70, 48],
    [64, 61],
    [55, 74],
    [50, 87],
    [46, 97],
    [42, 97],
    [40, 84],
    [35, 68],
    [29, 53],
    [27, 43],
    [32, 33],
  ],
];

const NODES = [
  { x: 15, y: 8, c: "MX" },
  { x: 42, y: 36, c: "CO" },
  { x: 58, y: 50, c: "BR" },
  { x: 38, y: 53, c: "PE" },
  { x: 45, y: 80, c: "CL" },
  { x: 51, y: 71, c: "AR" },
];

function inPoly(px: number, py: number, poly: number[][]) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i];
    const [xj, yj] = poly[j];
    if ((yi > py) !== (yj > py) && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) {
      inside = !inside;
    }
  }
  return inside;
}

function buildDots() {
  const dots: { x: number; y: number; ph: number }[] = [];
  for (let y = 0; y < 100; y += 2.1) {
    for (let x = 0; x < 74; x += 2.1) {
      if (POLYS.some((p) => inPoly(x, y, p))) {
        dots.push({ x, y, ph: Math.random() * Math.PI * 2 });
      }
    }
  }
  return dots;
}

const DOTS = buildDots();

export default function LatAmCoverageMap() {
  const { lang } = useLang();
  const isES = lang === "es";
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const rectRef = useRef<DOMRect | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const sizeCanvas = () => {
      const r = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      canvas.width = r.width * dpr;
      canvas.height = r.height * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      rectRef.current = r;
      return r;
    };

    let rect = sizeCanvas();
    let frame = 0;

    const draw = (t: number) => {
      if (!rectRef.current) rect = sizeCanvas();
      else rect = rectRef.current;

      ctx.clearRect(0, 0, rect.width, rect.height);
      const sx = rect.width / 74;
      const sy = rect.height / 100;

      for (const d of DOTS) {
        const tw = reduced ? 0 : Math.sin(t / 900 + d.ph) * 0.25;
        ctx.fillStyle = `rgba(255, 178, 36, ${0.13 + tw * 0.08})`;
        ctx.beginPath();
        ctx.arc(d.x * sx, d.y * sy, 1.4, 0, Math.PI * 2);
        ctx.fill();
      }

      NODES.forEach((n, i) => {
        const px = n.x * sx;
        const py = n.y * sy;
        const pulse = reduced ? 0 : ((t / 1100 + i * 0.7) % 1);
        ctx.strokeStyle = `rgba(61, 220, 132, ${(1 - pulse) * 0.5})`;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(px, py, 5 + pulse * 20, 0, Math.PI * 2);
        ctx.stroke();
        ctx.fillStyle = "#3DDC84";
        ctx.shadowColor = "#3DDC84";
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(px, py, 3.4, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        ctx.fillStyle = "#F2E9D8";
        ctx.font = '600 11px "IBM Plex Mono", monospace';
        ctx.fillText(n.c, px + 11, py + 4);
      });

      if (!reduced) frame = requestAnimationFrame(draw);
    };

    const onResize = () => {
      rect = sizeCanvas();
      if (reduced) draw(0);
    };

    window.addEventListener("resize", onResize);
    if (reduced) draw(0);
    else frame = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", onResize);
    };
  }, []);

  return (
    <div className="latam-map-wrap" aria-hidden="true">
      <canvas ref={canvasRef} className="latam-map-canvas" />
      <p className="latam-map-legend">
        {isES ? "● NODO ACTIVO — COLLECTOR CADA 4H" : "● ACTIVE NODE — COLLECTOR EVERY 4H"}
      </p>
    </div>
  );
}
