"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { animate, useInView } from "framer-motion";

type Parsed =
  | { kind: "text"; display: string }
  | { kind: "numeric"; end: number; format: (n: number) => string };

function parseMetricValue(raw: string): Parsed {
  const t = raw.trim();
  const pct = /^(\d+(?:\.\d+)?)%$/.exec(t);
  if (pct) {
    const end = parseFloat(pct[1]);
    return { kind: "numeric", end, format: (n) => `${Math.round(n)}%` };
  }
  const kplus = /^(\d+(?:\.\d+)?)K\+$/i.exec(t);
  if (kplus) {
    const end = parseFloat(kplus[1]) * 1000;
    return {
      kind: "numeric",
      end,
      format: (n) => {
        const k = n / 1000;
        if (k >= 100) return `${Math.round(k)}K+`;
        if (k >= 10) return `${Math.round(k)}K+`;
        return `${k.toFixed(1).replace(/\.0$/, "")}K+`;
      },
    };
  }
  const kh = /^(\d+(?:\.\d+)?)K$/i.exec(t);
  if (kh) {
    const end = parseFloat(kh[1]) * 1000;
    return {
      kind: "numeric",
      end,
      format: (n) => `${Math.round(n / 1000)}K`,
    };
  }
  const num = /^(\d+)$/.exec(t);
  if (num) {
    const end = parseInt(num[1], 10);
    return { kind: "numeric", end, format: (n) => String(Math.round(n)) };
  }
  return { kind: "text", display: t };
}

type Props = {
  value: string;
  className?: string;
  pulseSignal?: boolean;
};

export default function AnimatedMetricValue({ value, className = "", pulseSignal = false }: Props) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-24px" });
  const parsed = useMemo(() => parseMetricValue(value), [value]);
  const finalDisplay = useMemo(
    () => (parsed.kind === "text" ? parsed.display : parsed.format(parsed.end)),
    [parsed],
  );
  const [display, setDisplay] = useState(finalDisplay);
  const runId = useRef(0);

  useEffect(() => {
    if (parsed.kind === "text") {
      setDisplay(parsed.display);
      return;
    }
    if (!inView) {
      setDisplay(finalDisplay);
      return;
    }

    const id = ++runId.current;
    setDisplay(parsed.format(0));

    const controls = animate(0, parsed.end, {
      duration: 1.35,
      ease: [0.22, 1, 0.36, 1],
      onUpdate: (v) => {
        if (runId.current === id) setDisplay(parsed.format(v));
      },
      onComplete: () => {
        if (runId.current === id) setDisplay(finalDisplay);
      },
    });

    return () => {
      controls.stop();
      if (runId.current === id) setDisplay(finalDisplay);
    };
  }, [inView, value, parsed, finalDisplay]);

  return (
    <span
      ref={ref}
      className={`${className}${pulseSignal ? " hero-metric-value-signal" : ""}`}
      aria-live="polite"
    >
      {display}
    </span>
  );
}
