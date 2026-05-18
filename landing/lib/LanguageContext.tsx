"use client";
import { createContext, useContext, useState, type ReactNode } from "react";
import { getDict, t, type Lang } from "@/lib/translations";

const LangCtx = createContext<{ lang: Lang; setLang: (l: Lang) => void; t: (k: string) => string } | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("es");
  return <LangCtx.Provider value={{ lang, setLang, t: (k: string) => t(lang, k) }}>{children}</LangCtx.Provider>;
}

export function useLang() {
  const ctx = useContext(LangCtx);
  if (!ctx) throw new Error("useLang must be inside LanguageProvider");
  return ctx;
}
