"use client";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

const STORAGE_KEY = "cm-api-key";

export type AuthStatus = "unknown" | "anonymous" | "authenticated";

function isValidKey(key: string): boolean {
  return key.trim().startsWith("sk-");
}

function readStoredKey(): string | null {
  if (typeof window === "undefined") return null;
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return stored && isValidKey(stored) ? stored : null;
}

type AuthCtxValue = {
  apiKey: string | null;
  status: AuthStatus;
  setApiKey: (key: string) => boolean;
  clearApiKey: () => void;
};

const AuthCtx = createContext<AuthCtxValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [apiKey, setApiKeyState] = useState<string | null>(null);
  const [status, setStatus] = useState<AuthStatus>("unknown");

  useEffect(() => {
    const stored = readStoredKey();
    setApiKeyState(stored);
    setStatus(stored ? "authenticated" : "anonymous");
  }, []);

  const setApiKey = (key: string): boolean => {
    const trimmed = key.trim();
    if (!isValidKey(trimmed)) return false;
    setApiKeyState(trimmed);
    setStatus("authenticated");
    try {
      window.localStorage.setItem(STORAGE_KEY, trimmed);
    } catch {
      // ignore quota / private mode
    }
    return true;
  };

  const clearApiKey = () => {
    setApiKeyState(null);
    setStatus("anonymous");
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore quota / private mode
    }
  };

  return (
    <AuthCtx.Provider value={{ apiKey, status, setApiKey, clearApiKey }}>
      {children}
    </AuthCtx.Provider>
  );
}

export function useApiKey() {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error("useApiKey must be inside AuthProvider");
  return ctx;
}
