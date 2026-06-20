"use client";

import { useRef, useEffect, useState } from "react";

interface LiquidGlassButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  href?: string;
  className?: string;
}

export default function LiquidGlassButton({ children, onClick, href, className = "" }: LiquidGlassButtonProps) {
  const btnRef = useRef<HTMLButtonElement | null>(null);
  const [filterId] = useState(() => `lgb-${Math.random().toString(36).slice(2, 8)}`);
  const [mapUrl, setMapUrl] = useState("");
  const [dims, setDims] = useState({ w: 0, h: 0 });

  useEffect(() => {
    const el = btnRef.current;
    if (!el) return;

    const generate = () => {
      const rect = el.getBoundingClientRect();
      const w = Math.round(rect.width);
      const h = Math.round(rect.height);
      if (w === 0 || h === 0) return;
      setDims({ w, h });

      const canvas = document.createElement("canvas");
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext("2d")!;
      const imageData = ctx.createImageData(w, h);
      const data = imageData.data;

      const heightFn = (t: number) => Math.pow(1 - Math.pow(1 - Math.max(0, Math.min(1, t)), 4), 0.25);
      const slopeFn = (t: number) => (heightFn(t + 0.001) - heightFn(t - 0.001)) / 0.002;

      const N = 128;
      const n1 = 1.0, n2 = 1.5;
      const rawDisp: number[] = [];
      let maxD = 0;
      for (let i = 0; i < N; i++) {
        const t = i / (N - 1);
        const slope = slopeFn(t);
        const theta1 = Math.atan(Math.abs(slope));
        const sinT2 = (n1 / n2) * Math.sin(theta1);
        if (Math.abs(sinT2) >= 1) { rawDisp.push(0); continue; }
        const mag = Math.tan(theta1 - Math.asin(sinT2)) * heightFn(t);
        rawDisp.push(slope >= 0 ? mag : -mag);
        maxD = Math.max(maxD, Math.abs(mag));
      }
      if (maxD > 0) for (let i = 0; i < N; i++) rawDisp[i] /= maxD;

      const bezel = h / 2;
      for (let py = 0; py < h; py++) {
        for (let px = 0; px < w; px++) {
          const dL = px, dR = w - 1 - px, dT = py, dB = h - 1 - py;
          const dH = Math.min(dL, dR);
          const dV = Math.min(dT, dB);
          let dx = 0, dy = 0;
          if (dH < bezel) {
            const si = Math.min(N - 1, Math.round((dH / bezel) * (N - 1)));
            dx = rawDisp[si] * (dL < dR ? 1 : -1);
          }
          if (dV < bezel) {
            const si = Math.min(N - 1, Math.round((dV / bezel) * (N - 1)));
            dy = rawDisp[si] * (dT < dB ? 1 : -1);
          }
          const idx = (py * w + px) * 4;
          data[idx] = Math.max(0, Math.min(255, Math.round(128 + dx * 127)));
          data[idx + 1] = Math.max(0, Math.min(255, Math.round(128 + dy * 127)));
          data[idx + 2] = 128;
          data[idx + 3] = 255;
        }
      }
      ctx.putImageData(imageData, 0, 0);
      setMapUrl(canvas.toDataURL("image/png"));
    };

    const raf = requestAnimationFrame(generate);
    const ro = new ResizeObserver(generate);
    ro.observe(el);
    return () => { cancelAnimationFrame(raf); ro.disconnect(); };
  }, []);

  const style: React.CSSProperties = {
    position: "relative",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "16px 40px",
    borderRadius: 999,
    border: "1px solid rgba(255, 255, 255, 0.12)",
    background: "transparent",
    backdropFilter: mapUrl ? `url(#${filterId})` : "none",
    WebkitBackdropFilter: mapUrl ? `url(#${filterId})` : "none",
    color: "#ffffff",
    fontFamily: "var(--font-mono), 'JetBrains Mono', monospace",
    fontSize: 14,
    fontWeight: 300,
    letterSpacing: "0.5px",
    cursor: "pointer",
    overflow: "hidden",
    textDecoration: "none",
    transition: "all 0.4s cubic-bezier(0.16, 1, 0.3, 1)",
  };

  const inner = (
    <>
      {mapUrl && (
        <svg width="0" height="0" style={{ position: "absolute", pointerEvents: "none" }} colorInterpolationFilters="sRGB">
          <defs>
            <filter id={filterId} x="0%" y="0%" width="100%" height="100%" filterUnits="userSpaceOnUse" primitiveUnits="userSpaceOnUse">
              <feImage href={mapUrl} x="0" y="0" width={dims.w} height={dims.h} result="dispMap" />
              <feDisplacementMap in="SourceGraphic" in2="dispMap" scale="50" xChannelSelector="R" yChannelSelector="G" />
            </filter>
          </defs>
        </svg>
      )}
      <span style={{ position: "absolute", inset: 0, borderRadius: 999, background: "radial-gradient(ellipse at 30% 0%, rgba(255,255,255,0.08) 0%, transparent 60%)", pointerEvents: "none" }} />
      <span style={{ position: "relative", zIndex: 1 }}>{children}</span>
    </>
  );

  if (href) {
    return (
      <a
        href={href}
        className={`liquid-glass-btn ${className}`}
        style={style as React.CSSProperties}
        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.25)"; (e.currentTarget as HTMLElement).style.transform = "translateY(-1px)"; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.12)"; (e.currentTarget as HTMLElement).style.transform = "translateY(0)"; }}
      >
        {inner}
      </a>
    );
  }

  return (
    <button
      ref={btnRef}
      type="button"
      onClick={onClick}
      className={`liquid-glass-btn ${className}`}
      style={style}
      onMouseEnter={(e) => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.25)"; e.currentTarget.style.transform = "translateY(-1px)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)"; e.currentTarget.style.transform = "translateY(0)"; }}
    >
      {inner}
    </button>
  );
}
