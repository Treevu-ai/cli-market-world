"use client";

import { useState, useEffect, useCallback } from "react";
import { API_URL } from "@/lib/api";

interface Alert {
  id: string;
  name: string;
  condition: string;
  product_query: string;
  store: string;
  threshold_pct: number;
  active: boolean;
  created_at: string;
}

interface Props {
  apiKey: string;
  country: string;
}

const CONDITION_LABEL: Record<string, string> = {
  price_drop: "Baja de precio",
  price_jump: "Suba de precio",
  price_min_30d: "Mínimo 30d",
  dispersion_anomaly: "Anomalía dispersión",
};

export default function PriceAlertsWidget({ apiKey, country }: Props) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stapleList, setStapleList] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const headers = { Authorization: `Bearer ${apiKey}` };

  const loadAlerts = useCallback(async () => {
    try {
      const r = await fetch(`${API_URL}/v1/alerts`, { headers });
      const b = await r.json();
      setAlerts(b.alerts ?? []);
    } catch {
      setAlerts([]);
    }
  }, [apiKey]);

  useEffect(() => {
    if (!apiKey) return;
    setLoading(true);
    Promise.all([
      fetch(`${API_URL}/v1/household`, { headers })
        .then((r) => r.json())
        .then((b) => {
          const profile = b?.data ?? b;
          setStapleList(Array.isArray(profile?.staple_list) ? profile.staple_list : []);
        })
        .catch(() => {}),
      loadAlerts(),
    ]).finally(() => setLoading(false));
  }, [apiKey]);

  const alertedProducts = new Set(alerts.map((a) => a.product_query.toLowerCase()));

  async function createAlertsFromStaples() {
    const pending = stapleList.filter((p) => !alertedProducts.has(p.toLowerCase()));
    if (!pending.length) {
      setMessage("Todas tus básicas ya tienen alerta activa.");
      return;
    }
    setCreating(true);
    setMessage(null);
    let created = 0;
    for (const product of pending) {
      try {
        const r = await fetch(`${API_URL}/v1/alerts`, {
          method: "POST",
          headers: { ...headers, "Content-Type": "application/json" },
          body: JSON.stringify({
            condition: "price_drop",
            product_query: product,
            threshold_pct: 5,
            cooldown_hours: 24,
          }),
        });
        if (r.ok) created++;
      } catch {
        // skip silently
      }
    }
    await loadAlerts();
    setCreating(false);
    setMessage(`${created} alerta${created !== 1 ? "s" : ""} creada${created !== 1 ? "s" : ""}.`);
  }

  async function deleteAlert(id: string) {
    await fetch(`${API_URL}/v1/alerts/${id}`, { method: "DELETE", headers });
    setAlerts((prev) => prev.filter((a) => a.id !== id));
  }

  async function toggleAlert(id: string, active: boolean) {
    await fetch(`${API_URL}/v1/alerts/${id}/toggle`, { method: "PUT", headers });
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, active: !active } : a)));
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-3">
        {[1, 2].map((i) => (
          <div key={i} className="h-10 rounded-lg bg-[var(--cm-surface-low)]" />
        ))}
      </div>
    );
  }

  const pendingCount = stapleList.filter((p) => !alertedProducts.has(p.toLowerCase())).length;

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold font-mono text-[var(--cm-on-surface)]">
            Alertas de precio
          </h3>
          <p className="text-xs text-[var(--cm-on-surface-variant)] mt-0.5">
            Recibí aviso cuando bajan tus básicos
          </p>
        </div>
        {stapleList.length > 0 && (
          <button
            type="button"
            onClick={createAlertsFromStaples}
            disabled={creating || pendingCount === 0}
            className="text-xs font-mono font-semibold px-3 py-1.5 rounded-lg bg-[var(--cm-mint)] text-[var(--cm-on-mint)] hover:opacity-90 disabled:opacity-40 transition-opacity"
          >
            {creating
              ? "Creando..."
              : pendingCount > 0
              ? `+ Alertar ${pendingCount} básico${pendingCount !== 1 ? "s" : ""}`
              : "Al día ✓"}
          </button>
        )}
      </div>

      {message && (
        <p className="text-xs font-mono text-[var(--cm-mint)]">{message}</p>
      )}

      {stapleList.length === 0 && alerts.length === 0 && (
        <p className="text-xs text-[var(--cm-on-surface-variant)]">
          Configurá tu lista de básicos en{" "}
          <span className="font-mono text-[var(--cm-mint)]">Perfil → staple_list</span> para
          crear alertas automáticas.
        </p>
      )}

      {alerts.length > 0 && (
        <ul className="space-y-2">
          {alerts.map((alert) => (
            <li
              key={alert.id}
              className="flex items-center gap-3 rounded-lg bg-[var(--cm-surface-low)] px-3 py-2.5"
            >
              <span
                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  alert.active ? "bg-[var(--cm-mint)]" : "bg-[var(--cm-on-surface-variant)]/30"
                }`}
              />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-mono font-semibold text-[var(--cm-on-surface)] truncate">
                  {alert.product_query}
                </p>
                <p className="text-[11px] text-[var(--cm-on-surface-variant)]">
                  {CONDITION_LABEL[alert.condition] ?? alert.condition} · {alert.threshold_pct}%
                </p>
              </div>
              <div className="flex gap-1 flex-shrink-0">
                <button
                  type="button"
                  onClick={() => toggleAlert(alert.id, alert.active)}
                  title={alert.active ? "Pausar" : "Activar"}
                  className="text-[11px] font-mono px-2 py-1 rounded bg-[var(--cm-surface-high)] text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)] transition-colors"
                >
                  {alert.active ? "⏸" : "▶"}
                </button>
                <button
                  type="button"
                  onClick={() => deleteAlert(alert.id)}
                  title="Eliminar"
                  className="text-[11px] font-mono px-2 py-1 rounded bg-[var(--cm-surface-high)] text-[var(--cm-on-surface-variant)] hover:text-red-400 transition-colors"
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
