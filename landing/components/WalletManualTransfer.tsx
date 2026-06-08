"use client";

import { useState } from "react";

type Props = {
  method: "yape" | "plin";
  amountPen?: number;
  reference?: string;
  phone?: string | null;
  steps?: string[];
  isES: boolean;
};

function CopyButton({ value, label, isES }: { value: string; label: string; isES: boolean }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  };
  return (
    <div className="flex items-center justify-between gap-2 rounded border border-[var(--cm-outline-variant)]/35 bg-[var(--cm-surface-low)]/50 px-3 py-2">
      <div className="min-w-0 text-left">
        <p className="text-[10px] uppercase tracking-wide text-[var(--cm-on-surface-variant)]/60">{label}</p>
        <p className="font-mono text-sm text-white truncate">{value}</p>
      </div>
      <button
        type="button"
        onClick={copy}
        className="shrink-0 text-xs px-2.5 py-1 rounded border border-[var(--cm-outline-variant)]/50 text-[var(--cm-on-surface-variant)] hover:text-white"
      >
        {copied ? (isES ? "Copiado" : "Copied") : isES ? "Copiar" : "Copy"}
      </button>
    </div>
  );
}

export default function WalletManualTransfer({
  method,
  amountPen,
  reference,
  phone,
  steps,
  isES,
}: Props) {
  const app = method === "plin" ? "Plin" : "Yape";

  return (
    <div className="space-y-3 rounded border border-[var(--cm-mint)]/25 bg-[var(--cm-mint)]/5 p-4">
      <p className="text-sm font-semibold text-white">
        {isES ? `Pago manual con ${app}` : `Manual ${app} transfer`}
      </p>
      <p className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">
        {isES
          ? "Abre la app en tu celular y transfiere con estos datos (el QR web no funciona en Yape/Plin)."
          : "Open the app on your phone and transfer using these details (web QR does not work with Yape/Plin)."}
      </p>
      <div className="space-y-2">
        {phone && <CopyButton value={phone} label={isES ? "Número" : "Phone"} isES={isES} />}
        {amountPen != null && (
          <CopyButton
            value={`S/ ${amountPen.toFixed(2)}`}
            label={isES ? "Monto exacto" : "Exact amount"}
            isES={isES}
          />
        )}
        {reference && (
          <CopyButton value={reference} label={isES ? "Referencia (mensaje)" : "Reference (note)"} isES={isES} />
        )}
      </div>
      {steps && steps.length > 0 && (
        <ol className="list-decimal list-inside space-y-1 text-xs text-[var(--cm-on-surface-variant)]">
          {steps.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ol>
      )}
      {!phone && (
        <p className="text-[10px] text-[var(--cm-on-surface-variant)]/70">
          {isES
            ? "Si no ves el número aquí, revisa el email de confirmación."
            : "If the phone number is missing, check your confirmation email."}
        </p>
      )}
    </div>
  );
}