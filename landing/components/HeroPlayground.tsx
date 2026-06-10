"use client";

import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { MARKET_STATS } from "@/lib/marketStats";
import HeroTerminal from "@/components/HeroTerminal";

const API_KEY_STORAGE = "cli_market_api_key";

type Mode = "demo" | "live";

type LiveLine = { kind: "cmd" | "out" | "err"; text: string };

type CompareRow = { store: string; price: number; best: boolean };

function parseCompareQuery(raw: string): string | null {
  const trimmed = raw.trim();
  const m =
    trimmed.match(/compare\s+"([^"]+)"/i) ||
    trimmed.match(/compare\s+(\S+)/i) ||
    trimmed.match(/^market\s+compare\s+"([^"]+)"/i) ||
    trimmed.match(/^market\s+compare\s+(\S+)/i);
  return m?.[1]?.replace(/^["']|["']$/g, "") ?? null;
}

function storeLabel(store: string): string {
  const map: Record<string, string> = {
    metro_pe: "Metro",
    wong_pe: "Wong",
    plaza_vea_pe: "Plaza Vea",
  };
  return map[store] ?? store.replace(/_/g, " ");
}

export default function HeroPlayground() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [mode, setMode] = useState<Mode>("demo");
  const [input, setInput] = useState('market compare "arroz" --country PE');
  const [apiKey, setApiKey] = useState("");
  const [lines, setLines] = useState<LiveLine[]>([]);
  const [rows, setRows] = useState<CompareRow[]>([]);
  const [loading, setLoading] = useState(false);
  const outputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(API_KEY_STORAGE);
      if (saved?.startsWith("sk-")) setApiKey(saved);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    outputRef.current?.scrollTo({ top: outputRef.current.scrollHeight, behavior: "smooth" });
  }, [lines, rows, loading]);

  const persistKey = (key: string) => {
    setApiKey(key);
    try {
      if (key.startsWith("sk-")) window.localStorage.setItem(API_KEY_STORAGE, key);
      else window.localStorage.removeItem(API_KEY_STORAGE);
    } catch {
      /* ignore */
    }
  };

  const runCompare = useCallback(
    async (query: string) => {
      if (!apiKey.startsWith("sk-")) {
        setLines((prev) => [
          ...prev,
          {
            kind: "err",
            text: isES
              ? "Necesitas API key gratis (tier Free). Regístrate en /account y pégala abajo."
              : "Free-tier API key required. Register at /account and paste it below.",
          },
        ]);
        return;
      }

      setLoading(true);
      setRows([]);
      try {
        const res = await fetch(`${API_URL}/products/compare`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify({ query, limit: 5 }),
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          const detail =
            typeof data.detail === "string"
              ? data.detail
              : isES
                ? `Error ${res.status}`
                : `Error ${res.status}`;
          setLines((prev) => [...prev, { kind: "err", text: detail }]);
          return;
        }

        const comp = (data.comparison ?? [])[0];
        if (!comp?.prices || !Object.keys(comp.prices).length) {
          setLines((prev) => [
            ...prev,
            {
              kind: "out",
              text: isES ? "Sin resultados para esa búsqueda." : "No results for that query.",
            },
          ]);
          return;
        }

        const prices = comp.prices as Record<string, number>;
        const bestStore = comp.best_store as string;
        const max = Math.max(...Object.values(prices));
        const nextRows: CompareRow[] = Object.entries(prices)
          .map(([store, price]) => ({ store, price, best: store === bestStore }))
          .sort((a, b) => a.price - b.price);
        setRows(nextRows);
        setLines((prev) => [
          ...prev,
          {
            kind: "out",
            text: `${comp.name ?? query} · ${Object.keys(prices).length} ${isES ? "tiendas" : "stores"} · ${isES ? "mejor" : "best"} ${storeLabel(bestStore)} S/ ${comp.best_price?.toFixed?.(2) ?? comp.best_price}`,
          },
        ]);
      } catch {
        setLines((prev) => [
          ...prev,
          { kind: "err", text: isES ? "No se pudo conectar a la API." : "Could not reach the API." },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [apiKey, isES],
  );

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    const cmd = input.trim();
    if (!cmd) return;
    setLines((prev) => [...prev, { kind: "cmd", text: cmd.startsWith("$") ? cmd : `$ ${cmd}` }]);
    const query = parseCompareQuery(cmd);
    if (!query) {
      setLines((prev) => [
        ...prev,
        {
          kind: "err",
          text: isES
            ? 'Prueba: market compare "arroz" --country PE'
            : 'Try: market compare "arroz" --country PE',
        },
      ]);
      return;
    }
    void runCompare(query);
  };

  return (
    <div className="mt-12 w-full max-w-[920px]">
      <div className="flex flex-wrap items-center justify-center gap-2 mb-3">
        <button
          type="button"
          onClick={() => setMode("demo")}
          className={`hero-playground-tab ${mode === "demo" ? "hero-playground-tab-active" : ""}`}
        >
          {isES ? "Demo en vivo" : "Live demo"}
        </button>
        <button
          type="button"
          onClick={() => setMode("live")}
          className={`hero-playground-tab ${mode === "live" ? "hero-playground-tab-active" : ""}`}
        >
          {isES ? "Probar API" : "Try the API"}
        </button>
      </div>

      <div
        className="rounded-xl border border-[var(--cm-mint)]/35 bg-[#0a0a0a] shadow-[0_0_40px_rgba(58,254,207,0.12)] overflow-hidden text-left"
        aria-label={isES ? "Terminal CLI Market" : "CLI Market terminal"}
      >
        {mode === "demo" ? (
          <HeroTerminal />
        ) : (
          <div className="hero-term-live">
            <div ref={outputRef} className="hero-term-live-output">
              {lines.length === 0 ? (
                <p className="hero-term-line hero-term-muted text-sm">
                  {isES
                    ? "Escribe un comando compare. Usa tu API key gratis (tier Free)."
                    : "Type a compare command. Uses your free-tier API key."}
                </p>
              ) : null}
              {lines.map((l, i) => (
                <div
                  key={`${l.kind}-${i}`}
                  className={`hero-term-line ${
                    l.kind === "cmd" ? "hero-term-cmd" : l.kind === "out" ? "hero-term-out" : "hero-term-err"
                  }`}
                >
                  {l.text}
                </div>
              ))}
              {rows.map((r) => {
                const max = Math.max(...rows.map((x) => x.price));
                const w = max > 0 ? Math.round((r.price / max) * 100) : 0;
                return (
                  <div
                    key={r.store}
                    className={`hero-term-row hero-term-row-on${r.best ? " hero-term-row-best hero-term-row-tagged" : ""}`}
                  >
                    <span className="hero-term-lb">{storeLabel(r.store)}</span>
                    <div className="hero-term-track">
                      <div className="hero-term-fill" style={{ width: `${w}%` }} />
                    </div>
                    <span className="hero-term-price">
                      S/ {r.price.toFixed(2)}
                      {r.best ? <span className="hero-term-tag">✓ {isES ? "MEJOR" : "BEST"}</span> : null}
                    </span>
                  </div>
                );
              })}
              {loading ? (
                <div className="hero-term-line hero-term-muted">{isES ? "Consultando API…" : "Calling API…"}</div>
              ) : null}
            </div>
            <form onSubmit={onSubmit} className="hero-term-live-form border-t border-[var(--cm-outline-variant)]/30">
              <label className="sr-only" htmlFor="hero-api-key">
                API key
              </label>
              <input
                id="hero-api-key"
                type="password"
                value={apiKey}
                onChange={(e) => persistKey(e.target.value)}
                placeholder="sk-..."
                className="hero-term-key-input"
                autoComplete="off"
              />
              <div className="flex gap-2 w-full">
                <span className="hero-term-cmd py-2 shrink-0">$</span>
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="hero-term-cmd-input flex-1"
                  spellCheck={false}
                  aria-label={isES ? "Comando" : "Command"}
                />
                <button type="submit" className="hero-playground-run" disabled={loading}>
                  {isES ? "Ejecutar" : "Run"}
                </button>
              </div>
              {!apiKey.startsWith("sk-") ? (
                <p className="text-[10px] font-mono text-[var(--cm-on-surface-variant)]/70 mt-2">
                  {isES ? "Sin key → " : "No key → "}
                  <Link href="/account" className="text-[var(--cm-data)] underline underline-offset-2">
                    {isES ? "crear cuenta gratis" : "free account"}
                  </Link>
                </p>
              ) : null}
            </form>
          </div>
        )}
      </div>
      <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono text-center">
        {isES
          ? `▸ compare real · tier Free · ${MARKET_STATS.retailersVerified} verificados · ${MARKET_STATS.mcpTools} MCP`
          : `▸ live compare · free tier · ${MARKET_STATS.retailersVerified} verified · ${MARKET_STATS.mcpTools} MCP`}
      </p>
    </div>
  );
}
