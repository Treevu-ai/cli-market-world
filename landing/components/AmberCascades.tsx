"use client";

import { useEffect, useRef } from "react";

function initAmberCascades(canvas: HTMLCanvasElement) {
  const ctx = canvas.getContext("2d")!;
  let width = 0;
  let height = 0;
  let dpr = 1;
  let animationFrameId = 0;
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const FALL_SPEED = 1.0;
  const COLUMN_DENSITY = 0.7;
  const FONT_SIZE = Math.max(14, Math.round(16));
  const WAVE_RESOLUTION = 4;
  const MAX_RIPPLES = 40;

  const mathSymbols = "×÷∆ΣΠ√∞≈≠≤≥∫∂αβγθφψω";
  const numbers = "0123456789";
  const allChars = numbers + mathSymbols;
  const randomChar = () => allChars[Math.floor(Math.random() * allChars.length)];

  interface CharState { char: string; cycleTimer: number; cycleRate: number; }
  interface Column { x: number; y: number; speed: number; length: number; chars: CharState[]; active: boolean; restartDelay: number; opacity: number; hitWater: boolean; }
  interface Ripple { x: number; y: number; radius: number; maxRadius: number; speed: number; life: number; decay: number; }
  interface WavePoint { y: number; vy: number; }

  let columns: Column[] = [];
  let waterSurface = 0;
  let ripples: Ripple[] = [];
  let wavePoints: WavePoint[] = [];

  function createColumn(index: number, scatter: boolean): Column {
    const length = 12 + Math.floor(Math.random() * 20);
    const chars: CharState[] = Array.from({ length: length + 5 }, () => ({
      char: randomChar(),
      cycleTimer: Math.random() * 3,
      cycleRate: 0.5 + Math.random() * 2,
    }));
    let y: number;
    if (scatter) {
      y = Math.random() < COLUMN_DENSITY
        ? Math.random() * (waterSurface + length * FONT_SIZE) - length * FONT_SIZE * 0.3
        : -length * FONT_SIZE - Math.random() * height * 0.5;
    } else {
      y = -length * FONT_SIZE * Math.random() * 0.3;
    }
    return {
      x: index * FONT_SIZE, y, speed: 1.2 + Math.random() * 2.5, length, chars,
      active: scatter ? Math.random() < (COLUMN_DENSITY + 0.2) : Math.random() < COLUMN_DENSITY,
      restartDelay: 0, opacity: 0.6 + Math.random() * 0.4, hitWater: false,
    };
  }

  function initSystems() {
    waterSurface = height * 0.78;
    const colCount = Math.floor(width / FONT_SIZE);
    columns = Array.from({ length: colCount }, (_, i) => createColumn(i, true));
    const waveCount = Math.ceil(width / WAVE_RESOLUTION) + 1;
    wavePoints = Array.from({ length: waveCount }, () => ({ y: 0, vy: 0 }));
  }

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    initSystems();
  }

  function spawnRipple(x: number, y: number) {
    if (ripples.length >= MAX_RIPPLES) ripples.shift();
    ripples.push({ x, y, radius: 0, maxRadius: 30 + Math.random() * 50, speed: 20 + Math.random() * 30, life: 1.0, decay: 0.3 + Math.random() * 0.2 });
  }

  function disturbWave(x: number, force: number) {
    const idx = Math.floor(x / WAVE_RESOLUTION);
    const spread = 3;
    for (let i = -spread; i <= spread; i++) {
      const wi = idx + i;
      if (wi >= 0 && wi < wavePoints.length) {
        wavePoints[wi].vy += force * (1 - Math.abs(i) / (spread + 1));
      }
    }
  }

  let lastTime = 0;

  function render(timestamp: number) {
    const dt = Math.min((timestamp - (lastTime || timestamp)) / 1000, 0.05);
    lastTime = timestamp;
    const time = timestamp / 1000;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#0a0a0a";
    ctx.fillRect(0, 0, width, height);

    if (!prefersReduced) {
      for (const col of columns) {
        if (!col.active) {
          col.restartDelay -= dt;
          if (col.restartDelay <= 0) {
            if (Math.random() < COLUMN_DENSITY) {
              Object.assign(col, createColumn(Math.floor(col.x / FONT_SIZE), false), { active: true });
            } else {
              col.restartDelay = 0.3 + Math.random() * 1.5;
            }
          }
          continue;
        }
        const prevY = col.y;
        col.y += col.speed * FALL_SPEED * dt * 60;
        for (const c of col.chars) {
          c.cycleTimer -= dt;
          if (c.cycleTimer <= 0) { c.char = randomChar(); c.cycleTimer = c.cycleRate; }
        }
        if (!col.hitWater && col.y >= waterSurface && prevY < waterSurface) {
          col.hitWater = true;
          spawnRipple(col.x + FONT_SIZE * 0.5, waterSurface);
          disturbWave(col.x + FONT_SIZE * 0.5, -2 - Math.random() * 3);
        }
        if (col.y - col.length * FONT_SIZE > waterSurface + 30) {
          col.active = false;
          col.restartDelay = 0.2 + Math.random() * 2;
        }
      }

      for (let i = ripples.length - 1; i >= 0; i--) {
        const r = ripples[i];
        r.radius += r.speed * dt;
        r.life -= r.decay * dt;
        if (r.life <= 0 || r.radius > r.maxRadius) ripples.splice(i, 1);
      }

      for (const p of wavePoints) {
        p.vy += -0.03 * p.y;
        p.vy *= 0.97;
        p.y += p.vy;
      }
      for (let pass = 0; pass < 3; pass++) {
        for (let i = 0; i < wavePoints.length; i++) {
          if (i > 0) wavePoints[i].vy += 0.25 * (wavePoints[i - 1].y - wavePoints[i].y);
          if (i < wavePoints.length - 1) wavePoints[i].vy += 0.25 * (wavePoints[i + 1].y - wavePoints[i].y);
        }
      }
    }

    ctx.font = `${FONT_SIZE}px "JetBrains Mono", "Fira Code", "SF Mono", monospace`;
    ctx.textAlign = "center";
    ctx.textBaseline = "top";

    for (const col of columns) {
      if (!col.active) continue;
      for (let j = 0; j < col.length; j++) {
        const charY = col.y - j * FONT_SIZE;
        if (charY > waterSurface || charY < -FONT_SIZE) continue;
        let brightness: number;
        if (j === 0) brightness = 1.0;
        else if (j === 1) brightness = 0.9;
        else if (j < 4) brightness = 0.75 - (j - 2) * 0.08;
        else brightness = Math.max(0, 0.6 * (1 - j / col.length));
        const distToWater = waterSurface - charY;
        if (distToWater < FONT_SIZE * 3) brightness *= Math.max(0, distToWater / (FONT_SIZE * 3));
        brightness *= col.opacity;
        if (brightness < 0.02) continue;
        let r: number, g: number, b: number;
        if (j === 0) { r = 255; g = 245; b = 220; }
        else if (j < 3) { r = 240; g = 200; b = 140; }
        else { r = 200; g = 149; b = 108; }
        ctx.fillStyle = `rgba(${r},${g},${b},${brightness})`;
        if (j === 0) { ctx.shadowColor = "rgba(255, 220, 160, 0.6)"; ctx.shadowBlur = 8; }
        ctx.fillText(col.chars[j % col.chars.length].char, col.x + FONT_SIZE * 0.5, charY);
        if (j === 0) ctx.shadowBlur = 0;
      }
    }

    const waterGrad = ctx.createLinearGradient(0, waterSurface, 0, height);
    waterGrad.addColorStop(0, "rgba(15, 13, 11, 0.6)");
    waterGrad.addColorStop(1, "rgba(10, 10, 10, 0.95)");
    ctx.fillStyle = waterGrad;
    ctx.fillRect(0, waterSurface - 2, width, height - waterSurface + 2);

    ctx.beginPath();
    for (let x = 0; x <= width; x += WAVE_RESOLUTION) {
      const idx = Math.floor(x / WAVE_RESOLUTION);
      const waveY = idx < wavePoints.length ? wavePoints[idx].y : 0;
      const ambient = Math.sin(x * 0.01 + time * 0.8) * 1.5 + Math.sin(x * 0.023 + time * 0.5);
      const py = waterSurface + waveY + ambient;
      if (x === 0) ctx.moveTo(x, py);
      else ctx.lineTo(x, py);
    }
    ctx.strokeStyle = "rgba(200, 170, 130, 0.25)";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    for (const r of ripples) {
      const alpha = r.life * 0.3;
      for (let ring = 0; ring < 3; ring++) {
        const ringRadius = r.radius - ring * 8;
        if (ringRadius <= 0) continue;
        ctx.beginPath();
        ctx.ellipse(r.x, r.y + ring * 2, ringRadius, ringRadius * 0.3, 0, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(200, 170, 130, ${alpha * (1 - ring * 0.3)})`;
        ctx.lineWidth = 1 - ring * 0.2;
        ctx.stroke();
      }
    }

    animationFrameId = requestAnimationFrame(render);
  }

  function handleInteract(e: MouseEvent | TouchEvent) {
    const touch = "touches" in e ? e.touches[0] : null;
    const x = touch ? touch.clientX : (e as MouseEvent).clientX;
    disturbWave(x, -4 - Math.random() * 3);
    spawnRipple(x, waterSurface);
    const colIdx = Math.floor(x / FONT_SIZE);
    for (let di = -1; di <= 1; di++) {
      if (columns[colIdx + di]) {
        Object.assign(columns[colIdx + di], { active: true, y: (touch ? touch.clientY : (e as MouseEvent).clientY), speed: 2.5 + Math.random() * 2, hitWater: false });
      }
    }
  }

  window.addEventListener("resize", resize);
  canvas.addEventListener("click", handleInteract);
  canvas.addEventListener("touchstart", handleInteract as EventListener, { passive: false });
  resize();
  animationFrameId = requestAnimationFrame(render);

  return () => {
    window.removeEventListener("resize", resize);
    canvas.removeEventListener("click", handleInteract);
    canvas.removeEventListener("touchstart", handleInteract as EventListener);
    cancelAnimationFrame(animationFrameId);
  };
}

export default function AmberCascades({ opacity = 1 }: { opacity?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    return initAmberCascades(canvasRef.current);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", opacity, zIndex: 1 }}
      aria-hidden="true"
    />
  );
}
