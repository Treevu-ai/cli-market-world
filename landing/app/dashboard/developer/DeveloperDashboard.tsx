"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useApiKey } from "@/lib/useApiKey";
import { apiFetch, ApiError } from "@/lib/apiClient";

type ApiKeyRow = {
  id: number;
  key_prefix: string;
  scopes: string;
  label: string;
  created_at: string;
  last_used_at: string | null;
};

type KeysResponse = { keys: ApiKeyRow[]; total: number };
type CreateKeyResponse = { key: string; prefix: string; scopes: string; label: string };

const MCP_TARGETS = [
  { id: "claude-desktop", label: "Claude Desktop / Claude Code" },
  { id: "cursor", label: "Cursor" },
  { id: "generic", label: "Genérico (mcp.json)" },
] as const;

function mcpSnippet(target: string, key: string): string {
  const body = {
    mcpServers: {
      "cli-market": {
        command: "market-mcp",
        args: [],
        env: {
          MARKET_API_URL: "https://cli-market-api.fly.dev",
          MCP_TOOL_PROFILE: "default",
          MARKET_API_TOKEN: key,
        },
      },
    },
  };
  return JSON.stringify(body, null, 2);
}

export default function DeveloperDashboard() {
  const { apiKey } = useApiKey();
  const [keys, setKeys] = useState<ApiKeyRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [newLabel, setNewLabel] = useState("");
  const [justCreated, setJustCreated] = useState<CreateKeyResponse | null>(null);
  const [target, setTarget] = useState<(typeof MCP_TARGETS)[number]["id"]>("claude-desktop");
  const [copied, setCopied] = useState(false);

  const loadKeys = async () => {
    if (!apiKey) return;
    setError("");
    setLoading(true);
    try {
      const data = await apiFetch<KeysResponse>("/auth/keys", { apiKey });
      setKeys(data.keys ?? []);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al cargar las keys");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKeys();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiKey]);

  const createKey = async () => {
    if (!apiKey) return;
    setError("");
    try {
      const data = await apiFetch<CreateKeyResponse>("/auth/keys", {
        apiKey,
        method: "POST",
        body: { scopes: "read_write", label: newLabel.trim() || "console" },
      });
      setJustCreated(data);
      setNewLabel("");
      await loadKeys();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al crear la key");
    }
  };

  const revokeKey = async (id: number) => {
    if (!apiKey) return;
    setKeys((prev) => prev.filter((k) => k.id !== id)); // optimistic
    try {
      await apiFetch(`/auth/keys/${id}`, { apiKey, method: "DELETE" });
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Error al revocar la key");
      loadKeys(); // revert on failure
    }
  };

  const snippetKey = justCreated?.key ?? apiKey ?? "sk-...";
  const snippet = mcpSnippet(target, snippetKey);

  const copySnippet = async () => {
    try {
      await navigator.clipboard.writeText(snippet);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard API unavailable — ignore
    }
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--cm-surface)] pt-20 pb-24">
        <div className="max-w-2xl mx-auto px-4 sm:px-6">
          <div className="py-10">
            <p className="section-eyebrow mb-2 text-[var(--cm-mint)]">Developer</p>
            <h1 className="section-title mb-2">API keys y configuración MCP</h1>
            <p className="text-sm text-[var(--cm-on-surface-variant)]">
              Gestioná tus API keys y generá la config para tu cliente MCP favorito.
            </p>
          </div>

          {error && <p className="text-xs font-mono text-red-400 mb-4">{error}</p>}

          {/* Keys table */}
          <section className="mb-10">
            <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider mb-4">
              API Keys
            </h2>

            <div className="flex gap-2 mb-4">
              <input
                value={newLabel}
                onChange={(e) => setNewLabel(e.target.value)}
                placeholder="Etiqueta (ej. mi-laptop)"
                className="input-cyber font-mono text-sm flex-1"
              />
              <button type="button" onClick={createKey} className="btn-mint shrink-0">
                + Crear key
              </button>
            </div>

            {justCreated && (
              <div className="rounded-xl border border-[var(--cm-mint)]/40 bg-[var(--cm-mint)]/5 p-4 mb-4 space-y-2">
                <p className="text-xs font-mono text-[var(--cm-mint)]">
                  Guardala ahora — no se vuelve a mostrar completa.
                </p>
                <pre className="text-xs font-mono text-[var(--cm-on-surface)] bg-[var(--cm-surface-high)] p-2 rounded-lg overflow-x-auto">
                  {justCreated.key}
                </pre>
              </div>
            )}

            <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] divide-y divide-[var(--cm-outline-variant)]">
              {loading && keys.length === 0 && (
                <p className="p-4 text-xs font-mono text-[var(--cm-on-surface-variant)]">Cargando...</p>
              )}
              {!loading && keys.length === 0 && (
                <p className="p-4 text-xs font-mono text-[var(--cm-on-surface-variant)]">
                  No tenés keys todavía.
                </p>
              )}
              {keys.map((k) => (
                <div key={k.id} className="px-4 py-2.5 flex items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-mono text-[var(--cm-on-surface)] truncate">{k.label}</p>
                    <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60">
                      {k.key_prefix} · {k.scopes} · {k.last_used_at ? `usada ${k.last_used_at.slice(0, 10)}` : "nunca usada"}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => revokeKey(k.id)}
                    className="shrink-0 px-2.5 py-1 rounded-lg border border-[var(--cm-outline-variant)] text-[10px] font-mono text-[var(--cm-on-surface-variant)] hover:border-red-400 hover:text-red-400 transition-colors"
                  >
                    Revocar
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* MCP config generator */}
          <section>
            <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider mb-4">
              Config MCP
            </h2>
            <div className="flex items-center gap-2 mb-3 flex-wrap">
              {MCP_TARGETS.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setTarget(t.id)}
                  className={`text-xs font-mono px-2.5 py-1 rounded-full border transition-colors ${
                    target === t.id
                      ? "bg-[var(--cm-mint)] border-[var(--cm-mint)] text-[var(--cm-on-mint)] font-semibold"
                      : "border-[var(--cm-outline-variant)] text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)] hover:border-[var(--cm-mint)]"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
            <div className="relative">
              <pre className="text-xs font-mono text-[var(--cm-on-surface)] bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] p-4 rounded-xl overflow-x-auto">
                {snippet}
              </pre>
              <button
                type="button"
                onClick={copySnippet}
                className="absolute top-3 right-3 px-2.5 py-1 rounded-lg border border-[var(--cm-outline-variant)] text-[10px] font-mono text-[var(--cm-on-surface-variant)] hover:border-[var(--cm-mint)] hover:text-[var(--cm-on-surface)] transition-colors bg-[var(--cm-surface-high)]"
              >
                {copied ? "Copiado ✓" : "Copiar"}
              </button>
            </div>
            <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/60 mt-2">
              Incluye tu key real — es para tu config local, no para commitear a un repo compartido.
            </p>
          </section>
        </div>
      </main>
      <Footer />
    </>
  );
}
