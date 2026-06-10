"use client";

import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { API_URL } from "@/lib/api";
import { recordFunnelEvent } from "@/lib/funnel";
import { MARKET_STATS } from "@/lib/marketStats";
import { storeLabel } from "@/lib/storeLabels";
import HeroTerminal from "@/components/HeroTerminal";
import {
  hasSeenPlaygroundDemo,
  markPlaygroundDemoSeen,
  persistPlaygroundKey,
  readPlaygroundKey,
  type PlaygroundMode,
} from "@/lib/playground";

const DEMO_QUERIES = new Set(["arroz", "leche"]);

type LiveLine = { kind: "cmd" | "out" | "err"; text: string };

type CompareRow = { store: string; price: number; best: boolean };

type ComparePayload = {
  comparison?: Array<{
    name?: string;
    prices?: Record<string, number>;
    best_store?: string;
    best_price?: number;
  }>;
  stale?: boolean;
  seed?: boolean;
  cached_at?: string;
};

function parseCompareQuery(raw: string): string | null {
  const trimmed = raw.trim();
  const m =
    trimmed.match(/compare\s+"([^"]+)"/i) ||
    trimmed.match(/compare\s+(\S+)/i) ||
    trimmed.match(/^market\s+compare\s+"([^"]+)"/i) ||
    trimmed.match(/^market\s+compare\s+(\S+)/i);
  return m?.[1]?.replace(/^["']|["']$/g, "") ?? null;
}

function CompareRows({ rows, isES }: { rows: CompareRow[]; isES: boolean }) {
  const max = Math.max(...rows.map((x) => x.price), 0);
  return (
    <>
      {rows.map((r) => {
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
    </>
  );
}

export default function HeroPlayground() {
  const { lang } = useLang();
  const isES = lang === "es";
  const [mode, setMode] = useState<PlaygroundMode>("demo");
  const [input, setInput] = useState('market compare "arroz" --country PE');
  const [apiKey, setApiKey] = useState("");
  const [lines, setLines] = useState<LiveLine[]>([]);
  const [rows, setRows] = useState<CompareRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [claimingKey, setClaimingKey] = useState(false);
  const outputRef = useRef<HTMLDivElement>(null);
  const cmdInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const saved = readPlaygroundKey();
    if (saved.startsWith("sk-")) setApiKey(saved);
    if (hasSeenPlaygroundDemo()) setMode("live");
  }, []);

  useEffect(() => {
    const onFocus = (e: Event) => {
      const detail = (e as CustomEvent<{ mode?: PlaygroundMode }>).detail;
      if (detail?.mode) setMode(detail.mode);
      window.requestAnimationFrame(() => cmdInputRef.current?.focus());
    };
    window.addEventListener("playground-focus", onFocus);
    return () => window.removeEventListener("playground-focus", onFocus);
  }, []);

  useEffect(() => {
    if (mode === "demo") markPlaygroundDemoSeen();
  }, [mode]);

  useEffect(() => {
    outputRef.current?.scrollTo({ top: outputRef.current.scrollHeight, behavior: "smooth" });
  }, [lines, rows, loading]);

  const persistKey = (key: string) => {
    setApiKey(key);
    persistPlaygroundKey(key);
  };

  const applyCompareData = useCallback(
    (data: ComparePayload, query: string, opts?: { cached?: boolean }) => {
      const comp = data.comparison?.[0];
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

      const prices = comp.prices;
      const bestStore = comp.best_store ?? "";
      const nextRows: CompareRow[] = Object.entries(prices)
        .map(([store, price]) => ({ store, price, best: store === bestStore }))
        .sort((a, b) => a.price - b.price);
      setRows(nextRows);

      const cacheNote = opts?.cached
        ? isES
          ? " · demo cache"
          : " · demo cache"
        : "";
      setLines((prev) => [
        ...prev,
        {
          kind: "out",
          text: `${comp.name ?? query} · ${Object.keys(prices).length} ${isES ? "tiendas" : "stores"} · ${isES ? "mejor" : "best"} ${storeLabel(bestStore)} S/ ${comp.best_price?.toFixed?.(2) ?? comp.best_price}${cacheNote}`,
        },
      ]);
    },
    [isES],
  );

  const claimFreeKey = useCallback(async () => {
    setClaimingKey(true);
    try {
      const res = await fetch(`${API_URL}/auth/register`, { method: "POST" });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || typeof data.api_key !== "string") {
        setLines((prev) => [
          ...prev,
          {
            kind: "err",
            text: isES ? "No se pudo crear la key. Intenta en /account." : "Could not create key. Try /account.",
          },
        ]);
        return;
      }
      persistKey(data.api_key);
      recordFunnelEvent("register", {
        username: typeof data.username === "string" ? data.username : undefined,
        meta: { source: "hero_playground" },
        dedupe: false,
      });
      setLines((prev) => [
        ...prev,
        {
          kind: "out",
          text: isES
            ? "✓ API key Free creada. Ejecuta de nuevo tu compare."
            : "✓ Free API key created. Run your compare again.",
        },
      ]);
    } catch {
      setLines((prev) => [
        ...prev,
        { kind: "err", text: isES ? "Error de red al registrar." : "Network error during register." },
      ]);
    } finally {
      setClaimingKey(false);
    }
  }, [isES]);

  const runCompare = useCallback(
    async (query: string) => {
      const q = query.toLowerCase();
      const useDemo = !apiKey.startsWith("sk-") && DEMO_QUERIES.has(q);

      if (!apiKey.startsWith("sk-") && !useDemo) {
        setLines((prev) => [
          ...prev,
          {
            kind: "err",
            text: isES
              ? `Sin key: prueba "arroz" o "leche" (demo cache) o obtén key gratis abajo.`
              : `No key: try "arroz" or "leche" (demo cache) or get a free key below.`,
          },
        ]);
        return;
      }

      setLoading(true);
      setRows([]);
      try {
        if (useDemo) {
          const res = await fetch(`${API_URL}/public/demo/compare?q=${encodeURIComponent(q)}`);
          const data = (await res.json()) as ComparePayload & { detail?: string };
          if (!res.ok) {
            setLines((prev) => [
              ...prev,
              { kind: "err", text: typeof data.detail === "string" ? data.detail : `Error ${res.status}` },
            ]);
            return;
          }
          applyCompareData(data, query, { cached: true });
          return;
        }

        const res = await fetch(`${API_URL}/products/compare`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify({ query, limit: 5 }),
        });
        const data = (await res.json()) as ComparePayload & { detail?: string };
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
        applyCompareData(data, query);
      } catch {
        setLines((prev) => [
          ...prev,
          { kind: "err", text: isES ? "No se pudo conectar a la API." : "Could not reach the API." },
        ]);
      } finally {
        setLoading(false);
      }
    },
    [apiKey, isES, applyCompareData],
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
    <div className="mt-12 w-full landing-content-rail text-left">
      <div className="flex flex-wrap items-center justify-center gap-2 mb-4 w-full">
        <button
          type="button"
          onClick={() => setMode("demo")}
          className={`hero-playground-tab ${mode === "demo" ? "hero-playground-tab-active" : ""}`}
        >
          {isES ? "Demo en vivo" : "Live demo"}
        </button>
        <button
          type="button"
          onClick={() => {
            setMode("live");
            window.requestAnimationFrame(() => cmdInputRef.current?.focus());
          }}
          className={`hero-playground-tab ${mode === "live" ? "hero-playground-tab-active" : ""}`}
        >
          {isES ? "Probar API" : "Try the API"}
        </button>
      </div>

      <div
        className="hero-playground-terminal"
        aria-label={isES ? "Terminal CLI Market" : "CLI Market terminal"}
      >
        {mode === "demo" ? (
          <div>
            <HeroTerminal />
            <div className="flex justify-center border-t border-[var(--cm-outline-variant)]/25 px-4 py-3">
              <button
                type="button"
                className="hero-playground-try-live text-xs font-mono uppercase tracking-wider text-[var(--cm-data)] hover:brightness-110"
                onClick={() => {
                  setMode("live");
                  window.requestAnimationFrame(() => cmdInputRef.current?.focus());
                }}
              >
                {isES ? "Probar tú mismo →" : "Try it yourself →"}
              </button>
            </div>
          </div>
        ) : (
          <div className="hero-term-live">
            <div ref={outputRef} className="hero-term-live-output">
              {lines.length === 0 ? (
                <p className="hero-term-line hero-term-muted text-sm">
                  {isES
                    ? 'Sin key: compare "arroz" o "leche" (cache). Otras búsquedas → key gratis abajo.'
                    : 'No key: compare "arroz" or "leche" (cache). Other queries → free key below.'}
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
              <CompareRows rows={rows} isES={isES} />
              {loading ? (
                <div className="hero-term-line hero-term-muted">{isES ? "Consultando API…" : "Calling API…"}</div>
              ) : null}
            </div>
            <form onSubmit={onSubmit} className="hero-term-live-form">
              <label className="sr-only" htmlFor="hero-api-key">
                API key
              </label>
              <div className="hero-term-live-key-row">
                <input
                  id="hero-api-key"
                  type="password"
                  value={apiKey}
                  onChange={(e) => persistKey(e.target.value)}
                  placeholder="sk-..."
                  className="hero-term-key-input"
                  autoComplete="off"
                />
                {!apiKey.startsWith("sk-") ? (
                  <button
                    type="button"
                    className="hero-playground-get-key shrink-0"
                    disabled={claimingKey}
                    onClick={() => void claimFreeKey()}
                  >
                    {claimingKey
                      ? isES
                        ? "Creando…"
                        : "Creating…"
                      : isES
                        ? "Key gratis"
                        : "Free key"}
                  </button>
                ) : null}
              </div>
              <div className="hero-term-live-cmd-row">
                <span className="hero-term-cmd shrink-0">$</span>
                <input
                  ref={cmdInputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="hero-term-cmd-input"
                  spellCheck={false}
                  aria-label={isES ? "Comando" : "Command"}
                />
                <button type="submit" className="hero-playground-run" disabled={loading || claimingKey}>
                  {isES ? "Ejecutar" : "Run"}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
      <p className="text-[10px] text-[var(--cm-on-surface-variant)]/60 mt-2 font-mono text-center">
        {isES
          ? `▸ arroz/leche sin key (cache) · compare real con key Free · ${MARKET_STATS.retailersVerified} verificados`
          : `▸ arroz/leche no key (cache) · live compare with free key · ${MARKET_STATS.retailersVerified} verified`}
      </p>
    </div>
  );
}
