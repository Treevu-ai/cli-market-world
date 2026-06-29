"use client";

import { useState, useEffect } from "react";
import { API_URL } from "@/lib/api";

type Restrictions = {
  celiac?: boolean;
  lactose_free?: boolean;
  vegetarian?: boolean;
  vegan?: boolean;
};

type HouseholdProfile = {
  size: number;
  country: string;
  currency: string;
  budget_monthly: number;
  budget_period_start_day: number;
  restrictions: Restrictions;
  default_stores: string[];
  staple_list: string[];
  goals: string[];
};

const DEFAULT: HouseholdProfile = {
  size: 2,
  country: "PE",
  currency: "PEN",
  budget_monthly: 800,
  budget_period_start_day: 1,
  restrictions: {},
  default_stores: [],
  staple_list: [],
  goals: [],
};

const COUNTRIES = ["PE", "MX", "CO", "AR", "CL", "BO", "EC", "UY"];
const CURRENCIES: Record<string, string> = {
  PE: "PEN", MX: "MXN", CO: "COP", AR: "ARS",
  CL: "CLP", BO: "BOB", EC: "USD", UY: "UYU",
};
const GOALS_OPTIONS = ["ahorrar", "comer_sano", "reducir_desperdicio", "comprar_local"];
const GOALS_LABELS: Record<string, string> = {
  ahorrar: "Ahorrar",
  comer_sano: "Comer más sano",
  reducir_desperdicio: "Reducir desperdicio",
  comprar_local: "Comprar local",
};

type Props = { apiKey: string; onSaved?: (country: string) => void };

export default function HouseholdSetupForm({ apiKey, onSaved }: Props) {
  const [profile, setProfile] = useState<HouseholdProfile>(DEFAULT);
  const [stapleInput, setStapleInput] = useState("");
  const [storeInput, setStoreInput] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "saving" | "saved" | "error">("idle");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!apiKey) return;
    setStatus("loading");
    fetch(`${API_URL}/v1/household`, {
      headers: { Authorization: `Bearer ${apiKey}` },
    })
      .then((r) => r.json())
      .then((body) => {
        const d = body?.data ?? body;
        if (d && d.size !== undefined) {
          setProfile({ ...DEFAULT, ...d, restrictions: { ...DEFAULT.restrictions, ...(d.restrictions ?? {}) } });
        }
        setStatus("idle");
      })
      .catch(() => setStatus("idle"));
  }, [apiKey]);

  const set = <K extends keyof HouseholdProfile>(k: K, v: HouseholdProfile[K]) =>
    setProfile((p) => ({ ...p, [k]: v }));

  const toggleRestriction = (k: keyof Restrictions) =>
    setProfile((p) => ({
      ...p,
      restrictions: { ...p.restrictions, [k]: !p.restrictions[k] },
    }));

  const addTag = (
    field: "staple_list" | "default_stores",
    input: string,
    clear: () => void
  ) => {
    const val = input.trim().toLowerCase();
    if (!val) return;
    if (!profile[field].includes(val)) set(field, [...profile[field], val]);
    clear();
  };

  const removeTag = (field: "staple_list" | "default_stores", tag: string) =>
    set(field, profile[field].filter((t) => t !== tag));

  const toggleGoal = (g: string) =>
    set(
      "goals",
      profile.goals.includes(g) ? profile.goals.filter((x) => x !== g) : [...profile.goals, g]
    );

  const save = async () => {
    setStatus("saving");
    setError("");
    try {
      const r = await fetch(`${API_URL}/v1/household`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });
      if (!r.ok) {
        const b = await r.json().catch(() => ({}));
        throw new Error(b.detail ?? `HTTP ${r.status}`);
      }
      setStatus("saved");
      onSaved?.(profile.country);
      setTimeout(() => setStatus("idle"), 2500);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error al guardar");
      setStatus("error");
    }
  };

  if (status === "loading") {
    return (
      <div className="flex items-center gap-2 text-xs text-[var(--cm-on-surface-variant)]/60 font-mono py-4">
        <span className="w-2 h-2 rounded-full bg-[var(--cm-mint)] animate-pulse" />
        Cargando perfil...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Básicos */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-mono text-[var(--cm-on-surface-variant)] mb-1">Personas en el hogar</label>
          <input
            type="number" min={1} max={20}
            value={profile.size}
            onChange={(e) => set("size", Number(e.target.value))}
            className="w-full bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] focus:outline-none focus:border-[var(--cm-mint)]"
          />
        </div>
        <div>
          <label className="block text-xs font-mono text-[var(--cm-on-surface-variant)] mb-1">País</label>
          <select
            value={profile.country}
            onChange={(e) => {
              set("country", e.target.value);
              set("currency", CURRENCIES[e.target.value] ?? "USD");
            }}
            className="w-full bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] focus:outline-none focus:border-[var(--cm-mint)]"
          >
            {COUNTRIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-mono text-[var(--cm-on-surface-variant)] mb-1">
            Presupuesto mensual ({profile.currency})
          </label>
          <input
            type="number" min={0}
            value={profile.budget_monthly}
            onChange={(e) => set("budget_monthly", Number(e.target.value))}
            className="w-full bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] focus:outline-none focus:border-[var(--cm-mint)]"
          />
        </div>
        <div>
          <label className="block text-xs font-mono text-[var(--cm-on-surface-variant)] mb-1">Día de inicio del período</label>
          <input
            type="number" min={1} max={28}
            value={profile.budget_period_start_day}
            onChange={(e) => set("budget_period_start_day", Number(e.target.value))}
            className="w-full bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] focus:outline-none focus:border-[var(--cm-mint)]"
          />
        </div>
      </div>

      {/* Restricciones */}
      <div>
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-2">Restricciones alimentarias</p>
        <div className="flex flex-wrap gap-2">
          {(["celiac", "lactose_free", "vegetarian", "vegan"] as (keyof Restrictions)[]).map((k) => {
            const labels: Record<keyof Restrictions, string> = {
              celiac: "Celíaco", lactose_free: "Sin lactosa", vegetarian: "Vegetariano", vegan: "Vegano",
            };
            const active = !!profile.restrictions[k];
            return (
              <button
                key={k}
                type="button"
                onClick={() => toggleRestriction(k)}
                className={`px-3 py-1 rounded-full text-xs font-mono border transition-colors ${
                  active
                    ? "bg-[var(--cm-mint)] text-[var(--cm-on-mint)] border-[var(--cm-mint)]"
                    : "bg-transparent text-[var(--cm-on-surface-variant)] border-[var(--cm-outline-variant)] hover:border-[var(--cm-mint)]"
                }`}
              >
                {labels[k]}
              </button>
            );
          })}
        </div>
      </div>

      {/* Goals */}
      <div>
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-2">Objetivos</p>
        <div className="flex flex-wrap gap-2">
          {GOALS_OPTIONS.map((g) => {
            const active = profile.goals.includes(g);
            return (
              <button
                key={g}
                type="button"
                onClick={() => toggleGoal(g)}
                className={`px-3 py-1 rounded-full text-xs font-mono border transition-colors ${
                  active
                    ? "bg-[var(--cm-mint)]/20 text-[var(--cm-mint)] border-[var(--cm-mint)]"
                    : "bg-transparent text-[var(--cm-on-surface-variant)] border-[var(--cm-outline-variant)] hover:border-[var(--cm-mint)]"
                }`}
              >
                {GOALS_LABELS[g]}
              </button>
            );
          })}
        </div>
      </div>

      {/* Staples */}
      <div>
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-2">Productos básicos recurrentes</p>
        <div className="flex gap-2 mb-2">
          <input
            value={stapleInput}
            onChange={(e) => setStapleInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addTag("staple_list", stapleInput, () => setStapleInput(""))}
            placeholder="leche, arroz, azúcar..."
            className="flex-1 bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] placeholder:text-[var(--cm-on-surface-variant)]/40 focus:outline-none focus:border-[var(--cm-mint)]"
          />
          <button
            type="button"
            onClick={() => addTag("staple_list", stapleInput, () => setStapleInput(""))}
            className="px-3 py-2 rounded-lg bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] text-sm text-[var(--cm-on-surface-variant)] hover:border-[var(--cm-mint)] transition-colors"
          >
            +
          </button>
        </div>
        <div className="flex flex-wrap gap-1">
          {profile.staple_list.map((t) => (
            <span key={t} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] text-xs font-mono text-[var(--cm-on-surface-variant)]">
              {t}
              <button type="button" onClick={() => removeTag("staple_list", t)} className="hover:text-[var(--cm-error)] transition-colors leading-none">×</button>
            </span>
          ))}
        </div>
      </div>

      {/* Default stores */}
      <div>
        <p className="text-xs font-mono text-[var(--cm-on-surface-variant)] mb-2">Retailers preferidos</p>
        <div className="flex gap-2 mb-2">
          <input
            value={storeInput}
            onChange={(e) => setStoreInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addTag("default_stores", storeInput, () => setStoreInput(""))}
            placeholder="wong, metro, plaza vea..."
            className="flex-1 bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] placeholder:text-[var(--cm-on-surface-variant)]/40 focus:outline-none focus:border-[var(--cm-mint)]"
          />
          <button
            type="button"
            onClick={() => addTag("default_stores", storeInput, () => setStoreInput(""))}
            className="px-3 py-2 rounded-lg bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] text-sm text-[var(--cm-on-surface-variant)] hover:border-[var(--cm-mint)] transition-colors"
          >
            +
          </button>
        </div>
        <div className="flex flex-wrap gap-1">
          {profile.default_stores.map((t) => (
            <span key={t} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] text-xs font-mono text-[var(--cm-on-surface-variant)]">
              {t}
              <button type="button" onClick={() => removeTag("default_stores", t)} className="hover:text-[var(--cm-error)] transition-colors leading-none">×</button>
            </span>
          ))}
        </div>
      </div>

      {/* Save */}
      <div className="flex items-center gap-3 pt-2">
        <button
          type="button"
          onClick={save}
          disabled={status === "saving"}
          className="px-5 py-2.5 rounded-lg bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold font-mono hover:opacity-90 disabled:opacity-50 transition-opacity"
        >
          {status === "saving" ? "Guardando..." : "Guardar perfil"}
        </button>
        {status === "saved" && (
          <span className="text-xs font-mono text-[var(--cm-mint)]">✓ Guardado</span>
        )}
        {status === "error" && (
          <span className="text-xs font-mono text-red-400">{error}</span>
        )}
      </div>
    </div>
  );
}
