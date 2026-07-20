import { useState } from "react";
import { ShieldCheck, Loader2 } from "lucide-react";

/**
 * Manual Pro/Procure activation — for the Yape/Plin bank-transfer path,
 * which has no automated webhook confirmation (PayPal/Mercado Pago
 * activate on their own). Gated by a local passphrase; the real admin
 * token never reaches the browser (see server.ts's /api/activate).
 *
 * Only meaningful for PRO-/PCS-/PCP-/PCB- request ids — Starter (STR-) has
 * no manual override by design (PayPal webhook only).
 */

type ActivateResult = {
  ok?: boolean;
  request_id?: string;
  username?: string;
  actions?: string[];
  detail?: string | { msg?: string }[];
};

function parseApiError(data: ActivateResult, fallback: string): string {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  return fallback;
}

export default function ActivateProPanel() {
  const [open, setOpen] = useState(false);
  const [requestId, setRequestId] = useState("");
  const [passphrase, setPassphrase] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ActivateResult | null>(null);

  const submit = async () => {
    setError("");
    setResult(null);
    if (!requestId.trim()) {
      setError("Ingresa el request_id (PRO-XXXXXXXX)");
      return;
    }
    if (!passphrase.trim()) {
      setError("Ingresa la passphrase");
      return;
    }
    setLoading(true);
    try {
      const r = await fetch(`${import.meta.env.BASE_URL}api/activate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: requestId.trim(), passphrase: passphrase.trim() }),
      });
      const data = (await r.json()) as ActivateResult;
      if (r.ok && data.ok) {
        setResult(data);
      } else {
        setError(parseApiError(data, `Error ${r.status} al activar`));
      }
    } catch {
      setError("Error de red al conectar con la activación");
    }
    setLoading(false);
  };

  return (
    <details
      className="mt-10 text-left text-[11px] text-white/40 font-mono"
      open={open}
      onToggle={(e) => setOpen((e.target as HTMLDetailsElement).open)}
    >
      <summary className="cursor-pointer uppercase tracking-widest hover:text-white/70 select-none">
        Ops · Activar Pro manual
      </summary>
      <div className="mt-3 max-w-sm space-y-2 rounded-sm border border-white/10 bg-white/5 p-4">
        <input
          type="text"
          value={requestId}
          onChange={(e) => setRequestId(e.target.value)}
          placeholder="PRO-XXXXXXXX"
          className="w-full bg-black/40 border border-white/10 rounded-sm py-2 px-3 text-xs font-mono text-white placeholder-white/30 focus:outline-none focus:border-[#bef264]"
        />
        <input
          type="password"
          value={passphrase}
          onChange={(e) => setPassphrase(e.target.value)}
          placeholder="passphrase"
          className="w-full bg-black/40 border border-white/10 rounded-sm py-2 px-3 text-xs font-mono text-white placeholder-white/30 focus:outline-none focus:border-[#bef264]"
        />
        {error && <p className="text-[10px] text-red-400 normal-case">{error}</p>}
        <button
          type="button"
          onClick={() => void submit()}
          disabled={loading}
          className="w-full inline-flex items-center justify-center gap-2 rounded-sm bg-white/10 text-white py-2 px-3 text-[10px] font-mono font-bold uppercase tracking-widest hover:bg-white/20 transition-all disabled:opacity-40"
        >
          {loading && <Loader2 className="h-3 w-3 animate-spin" />}
          {loading ? "Activando…" : "Activar"}
        </button>
        {result && (
          <div className="mt-2 space-y-1 rounded-sm border border-[#bef264]/20 bg-[#bef264]/5 p-3 text-[10px] normal-case">
            <p className="flex items-center gap-1.5 text-[#bef264] font-bold">
              <ShieldCheck className="h-3 w-3" /> Activado — evidencia registrada (record_audit)
            </p>
            <p className="text-white/70">
              request_id: <span className="text-white">{result.request_id}</span> · usuario:{" "}
              <span className="text-white">{result.username}</span>
            </p>
            <ul className="list-disc list-inside text-white/50">
              {result.actions?.map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </details>
  );
}
