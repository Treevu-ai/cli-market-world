"use client";

import { useState } from "react";
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

type ReceiptStatus = "idle" | "scanning" | "submitting" | "done" | "error";

type Props = { apiKey: string };

export default function ReceiptScanner({ apiKey }: Props) {
  const [url, setUrl] = useState("");
  const [submitToCrowd, setSubmitToCrowd] = useState(true);
  const [status, setStatus] = useState<ReceiptStatus>("idle");
  const [scan, setScan] = useState<ScanResult | null>(null);
  const [receiptId, setReceiptId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const reset = () => {
    setScan(null);
    setReceiptId(null);
    setError("");
    setStatus("idle");
  };

  const handleScan = async () => {
    if (!url.trim()) return;
    setError("");
    setStatus("scanning");
    setScan(null);

    try {
      const r = await fetch(`${API_URL}/v1/ticket/scan-url`, {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
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
            url: url.trim(),
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

  return (
    <div className="space-y-5">
      {/* URL input */}
      <div className="space-y-2">
        <label className="block text-xs font-mono text-[var(--cm-on-surface-variant)]">
          URL pública de la foto del ticket
        </label>
        <div className="flex gap-2">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && status === "idle" && handleScan()}
            placeholder="https://..."
            disabled={status === "scanning" || status === "submitting"}
            className="flex-1 bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] placeholder:text-[var(--cm-on-surface-variant)]/40 focus:outline-none focus:border-[var(--cm-mint)] disabled:opacity-50"
          />
          <button
            type="button"
            onClick={status === "done" || status === "error" ? reset : handleScan}
            disabled={(!url.trim() && status === "idle") || status === "scanning" || status === "submitting"}
            className="px-4 py-2 rounded-lg bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold font-mono hover:opacity-90 disabled:opacity-40 transition-opacity whitespace-nowrap"
          >
            {status === "scanning" ? "Escaneando..." :
             status === "submitting" ? "Enviando..." :
             status === "done" || status === "error" ? "Nuevo" :
             "Escanear"}
          </button>
        </div>
      </div>

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

      {/* Error */}
      {status === "error" && (
        <p className="text-xs font-mono text-red-400">{error}</p>
      )}

      {/* Results */}
      {scan && status === "done" && (
        <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] divide-y divide-[var(--cm-outline-variant)]">
          {/* Header */}
          <div className="p-4 flex flex-wrap gap-4">
            <div className="text-center">
              <p className="text-lg font-mono font-bold text-[var(--cm-on-surface)]">{scan.items_detected ?? 0}</p>
              <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]">detectados</p>
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
              <div className="ml-auto flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--cm-mint)]" />
                <p className="text-[10px] font-mono text-[var(--cm-mint)]">Contribuido · {receiptId}</p>
              </div>
            )}
          </div>

          {/* Line items */}
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
        </div>
      )}
    </div>
  );
}
