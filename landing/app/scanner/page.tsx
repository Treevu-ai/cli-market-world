"use client";

import { useState, useCallback, useRef } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";

type MatchedItem = {
  ticket_text: string;
  best_match: string;
  store: string;
  price: number;
  currency: string;
};

type ScanResult = {
  ocr_text: string;
  items_detected: number;
  items_matched: number;
  potential_savings: number;
  items: MatchedItem[];
  message: string;
};

type Status = "idle" | "uploading" | "done" | "error";

export default function ScannerPage() {
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const scan = useCallback(async (file: File) => {
    setStatus("uploading");
    setResult(null);
    setError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API_URL}/v1/ticket/scan`, {
        method: "POST",
        body: fd,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: ScanResult = await res.json();
      setResult(data);
      setStatus("done");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Error inesperado");
      setStatus("error");
    }
  }, []);

  const onFile = useCallback(
    (file: File | null | undefined) => {
      if (!file) return;
      if (!file.type.startsWith("image/")) {
        setError("Solo se aceptan imágenes (JPG, PNG, WEBP).");
        return;
      }
      scan(file);
    },
    [scan]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      onFile(e.dataTransfer.files?.[0]);
    },
    [onFile]
  );

  return (
    <main className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />

      <div className="relative z-10 max-w-2xl mx-auto px-4 pt-28 pb-20">

        {/* Header */}
        <div className="text-center mb-10">
          <p className="text-xs font-mono uppercase tracking-widest text-[var(--cm-mint)] mb-3">
            Data Moat · Demo pública
          </p>
          <h1 className="text-3xl font-black text-white mb-3">
            Escaneá tu boleta
          </h1>
          <p className="text-sm text-[var(--cm-on-surface-variant)] max-w-md mx-auto">
            Sube una foto de tu ticket de compra. Buscamos cada ítem en{" "}
            <span className="text-white font-semibold">{MARKET_STATS.pricesVerifiedLabel} precios verificados</span> de{" "}
            {MARKET_STATS.retailersVerified} retailers y le mostramos dónde podría pagar menos.
          </p>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/50 mt-2 font-mono">
            Sin registro · Sin cookies · Solo datos de góndola real
          </p>
        </div>

        {/* Upload zone */}
        {status === "idle" || status === "error" ? (
          <div
            className={`rounded-2xl border-2 border-dashed transition-all cursor-pointer p-10 text-center
              ${dragging
                ? "border-[var(--cm-mint)] bg-[var(--cm-mint)]/5"
                : "border-[var(--cm-outline-variant)]/40 hover:border-[var(--cm-mint)]/50"
              }`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => onFile(e.target.files?.[0])}
            />
            <div className="text-4xl mb-3">🧾</div>
            <p className="text-white font-semibold mb-1">
              Arrastrá tu boleta aquí
            </p>
            <p className="text-sm text-[var(--cm-on-surface-variant)]">
              o hacé clic para seleccionar una imagen
            </p>
            <p className="text-xs text-[var(--cm-on-surface-variant)]/50 mt-3 font-mono">
              JPG · PNG · WEBP
            </p>
            {error && (
              <p className="text-red-400 text-sm mt-4 font-mono">{error}</p>
            )}
          </div>
        ) : null}

        {/* Loading */}
        {status === "uploading" && (
          <div className="rounded-2xl border border-[var(--cm-outline-variant)]/30 card-cyber p-10 text-center">
            <div className="inline-flex items-center gap-3 text-[var(--cm-mint)]">
              <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              <span className="font-mono text-sm">Procesando boleta…</span>
            </div>
            <p className="text-xs text-[var(--cm-on-surface-variant)]/50 mt-3">
              OCR → comparación contra el data moat
            </p>
          </div>
        )}

        {/* Results */}
        {status === "done" && result && (
          <div className="space-y-5">

            {/* Summary */}
            <div className="rounded-2xl border border-[var(--cm-outline-variant)]/30 card-cyber p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-1">
                    {result.items_detected} líneas detectadas · {result.items_matched} productos encontrados
                  </p>
                  <p className="text-2xl font-black text-[var(--cm-mint)]">
                    {result.items_matched > 0
                      ? `Ahorro potencial: ${result.potential_savings.toFixed(2)}`
                      : "Sin coincidencias"}
                  </p>
                  <p className="text-xs text-[var(--cm-on-surface-variant)] mt-1">
                    {result.message}
                  </p>
                </div>
                <button
                  onClick={() => { setStatus("idle"); setResult(null); }}
                  className="shrink-0 text-xs font-mono text-[var(--cm-on-surface-variant)] hover:text-white border border-[var(--cm-outline-variant)]/40 rounded-lg px-3 py-1.5 transition-colors"
                >
                  Nueva boleta
                </button>
              </div>
            </div>

            {/* Items table */}
            {result.items.length > 0 && (
              <div className="rounded-2xl border border-[var(--cm-outline-variant)]/30 card-cyber overflow-hidden">
                <div className="px-5 py-3 border-b border-[var(--cm-outline-variant)]/20">
                  <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]">
                    Precios más bajos encontrados en el moat
                  </p>
                </div>
                <div className="divide-y divide-[var(--cm-outline-variant)]/10">
                  {result.items.map((item, i) => (
                    <div key={i} className="px-5 py-3.5 flex items-center justify-between gap-4">
                      <div className="min-w-0">
                        <p className="text-xs text-[var(--cm-on-surface-variant)] font-mono truncate">
                          {item.ticket_text}
                        </p>
                        <p className="text-sm text-white font-semibold truncate">
                          {item.best_match}
                        </p>
                        <p className="text-xs text-[var(--cm-mint)]">{item.store}</p>
                      </div>
                      <div className="shrink-0 text-right">
                        <p className="text-sm font-black text-white tabular-nums">
                          {item.currency} {item.price.toFixed(2)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* CTA */}
            <div className="rounded-2xl border border-[var(--cm-mint)]/20 bg-[var(--cm-mint)]/5 p-5 text-center">
              <p className="text-sm text-white font-semibold mb-1">
                ¿Querés comparar precios programáticamente?
              </p>
              <p className="text-xs text-[var(--cm-on-surface-variant)] mb-4">
                Accedé a {MARKET_STATS.mcpTools} herramientas MCP y {MARKET_STATS.pricesVerifiedLabel} precios verificados vía API.
              </p>
              <a
                href={MARKET_STATS.pypiUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-mint inline-block px-6 py-2 text-sm"
              >
                {MARKET_STATS.pipInstallCmd}
              </a>
            </div>

          </div>
        )}

        {/* OCR raw text (collapsed) */}
        {status === "done" && result?.ocr_text && (
          <details className="mt-4">
            <summary className="text-xs font-mono text-[var(--cm-on-surface-variant)]/50 cursor-pointer hover:text-[var(--cm-on-surface-variant)] transition-colors">
              Ver texto OCR crudo
            </summary>
            <pre className="mt-2 text-xs font-mono text-[var(--cm-on-surface-variant)]/60 bg-[var(--cm-surface-high)]/30 rounded-xl p-4 overflow-x-auto whitespace-pre-wrap">
              {result.ocr_text}
            </pre>
          </details>
        )}

      </div>

      <Footer />
    </main>
  );
}
