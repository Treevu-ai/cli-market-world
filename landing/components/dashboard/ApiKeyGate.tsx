"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import { useApiKey } from "@/lib/useApiKey";

/** Shared paste-key entry point — used by the /dashboard shell gate and by
 *  AccountDashboard. Persists via useApiKey() (localStorage), replacing the
 *  old "paste on every reload, never stored" behavior. */
export default function ApiKeyGate({ title }: { title?: string }) {
  const { lang } = useLang();
  const isES = lang === "es";
  const { setApiKey } = useApiKey();
  const [value, setValue] = useState("");
  const [error, setError] = useState("");

  const submit = () => {
    setError("");
    const ok = setApiKey(value);
    if (!ok) {
      setError(isES ? "Ingrese su API key (sk-...)" : "Enter your API key (sk-...)");
    }
  };

  return (
    <div className="card-cyber p-6 space-y-4 max-w-xl mx-auto">
      {title && (
        <h2 className="text-sm font-bold text-[var(--cm-mint)] uppercase tracking-wider">
          {title}
        </h2>
      )}
      <label className="block text-sm font-medium text-[var(--cm-on-surface)]">API key</label>
      <input
        type="password"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && submit()}
        placeholder="sk-..."
        className="input-cyber font-mono text-sm"
        autoComplete="off"
      />
      <p className="text-xs text-[var(--cm-on-surface-variant)]">
        {isES
          ? "Obténgala con market register · También: market account en terminal"
          : "Get one with market register · Or run market account in the terminal"}
      </p>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button type="button" onClick={submit} className="btn-mint w-full">
        {isES ? "Entrar a la consola →" : "Enter console →"}
      </button>
    </div>
  );
}
