"use client";

import { useState, useRef } from "react";
import { API_URL } from "@/lib/api";

type MatchedItem = {
  ticket_text: string;
  best_match: string | null;
  store: string;
  price: number;
  currency: string;
};

type ScanResult = {
  ocr_text?: string;
  items_detected?: number;
  items_matched?: number;
  potential_savings?: number;
  items?: MatchedItem[];
  message?: string;
};

type Status = "idle" | "scanning" | "submitting" | "done" | "error";

type Props = { apiKey: string };

export default function ReceiptScanner({ apiKey }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [submitToCrowd, setSubmitToCrowd] = useState(true);
  const [status, setStatus] = useState<Status>("idle");
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [receiptId, setReceiptId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setScan(null);
    setReceiptId(null);
    setError("");
    setStatus("idle");
  };

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f && f.type.startsWith("image/")) handleFile(f);
  };

  const reset = () => {
    setFile(null);
    setPreview(null);
    setScan(null);
    setReceiptId(null);
    setError("");
    setStatus("idle");
    if (inputRef.current) inputRef.current.value = "";
  };

  const scan_ = async () => {
    if (!file) return;
    setError("");
    setStatus("scanning");
    setScan(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const r = await fetch(`${API_URL}/v1/ticket/scan`, {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}` },
        body: form,
      });
      const body = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(body.detail ?? `HTTP ${r.status}`);
      const d = body?.data ?? body;
      setScan(d);

      if (submitToCrowd) {
        setStatus("submitting");
        const r2 = await fetch(`${API_URL}/v1/receipts/submit`, {
          method: "POST",
          headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
          body: JSON.stringify({
            url: "",
            ocr: { text: d.ocr_text },
            line_items: (d.items ?? []).map((it: MatchedItem) => ({
              name: it.ticket_text,
              price: it.price,
              currency: it.currency,
              store: it.store,
            })),
          }),
        });
        const b2 = await r2.json().catch(() => ({}));
        if (r2.ok) setReceiptId((b2?.data ?? b2)?.id ?? null);
      }

      setStatus("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al escanear");
      setStatus("error");
    }
  };

  const busy = status === "scanning" || status === "submitting";

  return (
    <div className="space-y-5">
      {/* Drop zone / file picker */}
      {!file ? (
        <div
          onDrop={onDrop}
          onDragOver={(e) => e.preventDefault()}
          onClick={() => inputRef.current?.click()}
          className="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-[var(--cm-outline-variant)] hover:border-[var(--cm-mint)] transition-colors cursor-pointer p-10 text-center"
        >
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-[var(--cm-on-surface-variant)]/40">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <div>
            <p className="text-sm font-mono text-[var(--cm-on-surface-variant)]">
              Arrastrá tu foto o tocá para elegir
            </p>
            <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]/50 mt-1">
              JPG, PNG, WEBP — máx. 10 MB
            </p>
          </div>
          <input
            ref={inputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={onInputChange}
            className="hidden"
          />
        </div>
      ) : (
        <div className="space-y-3">
          {/* Preview */}
          <div className="relative rounded-xl overflow-hidden border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-low)]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={preview!} alt="ticket" className="w-full max-h-56 object-contain" />
            <button
              type="button"
              onClick={reset}
              className="absolute top-2 right-2 w-6 h-6 rounded-full bg-black/60 text-white text-xs flex items-center justify-center hover:bg-black/80 transition-colors"
            >
              ×
            </button>
          </div>
          <p className="text-xs font-mono text-[var(--cm-on-surface-variant)]/60 truncate">{file.name}</p>
        </div>
      )}

      {/* Crowd opt-in */}
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={submitToCrowd}
          onChange={(e) => setSubmitToCrowd(e.target.checked)}
          className="accent-[var(--cm-mint)] w-3.5 h-3.5"
        />
        <span className="text-xs font-mono text-[var(--cm-on-surface-variant)]">
          Contribuir precios al moat crowd-truth
        </span>
      </label>

      {/* Action button */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={status === "done" || status === "error" ? reset : scan_}
          disabled={!file || busy}
          className="px-5 py-2.5 rounded-lg bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold font-mono hover:opacity-90 disabled:opacity-40 transition-opacity"
        >
          {status === "scanning" ? "Escaneando..." :
           status === "submitting" ? "Enviando..." :
           status === "done" || status === "error" ? "Nuevo ticket" :
           "Escanear ticket"}
        </button>
        {status === "error" && (
          <p className="text-xs font-mono text-red-400">{error}</p>
        )}
      </div>

      {/* Results */}
      {scan && status === "done" && (
        <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] divide-y divide-[var(--cm-outline-variant)]">
          <div className="p-4 flex flex-wrap gap-5">
            <div className="text-center">
              <p className="text-lg font-mono font-bold text-[var(--cm-on-surface)]">{scan.items_detected ?? 0}</p>
              <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]">líneas detectadas</p>
            </div>
            <div className="text-center">
              <p className="text-lg font-mono font-bold text-[var(--cm-mint)]">{scan.items_matched ?? 0}</p>
              <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]">en moat</p>
            </div>
            {(scan.potential_savings ?? 0) > 0 && (
              <div className="text-center">
                <p className="text-lg font-mono font-bold text-[#FFD700]">{scan.potential_savings?.toFixed(2)}</p>
                <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]">ahorro potencial</p>
              </div>
            )}
            {receiptId && (
              <div className="ml-auto flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--cm-mint)]" />
                <p className="text-[10px] font-mono text-[var(--cm-mint)]">Contribuido · {receiptId}</p>
              </div>
            )}
          </div>

          {(scan.items ?? []).length > 0 && (
            <div className="divide-y divide-[var(--cm-outline-variant)]">
              {scan.items!.map((it, i) => (
                <div key={i} className="px-4 py-2.5 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-mono text-[var(--cm-on-surface)] truncate">{it.ticket_text}</p>
                    {it.best_match && it.best_match !== it.ticket_text && (
                      <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60 truncate">→ {it.best_match}</p>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-xs font-mono tabular-nums text-[var(--cm-on-surface)]">
                      {it.currency} {it.price?.toFixed(2)}
                    </p>
                    {it.store && (
                      <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60">{it.store}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {scan.message && (scan.items ?? []).length === 0 && (
            <p className="px-4 py-3 text-xs font-mono text-[var(--cm-on-surface-variant)]/60">{scan.message}</p>
          )}
        </div>
      )}
    </div>
  );
}
