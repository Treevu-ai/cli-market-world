"use client";

import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";
import { storeLabel } from "@/lib/storeLabels";

export type CompareRow = { store: string; price: number; best: boolean };

const FALLBACK: CompareRow[] = [
  { store: "Metro", price: 2.9, best: false },
  { store: "Wong", price: 3.1, best: false },
  { store: "Plaza Vea", price: 2.85, best: true },
];

export function useDemoCompareRows(query = "arroz") {
  const [rows, setRows] = useState<CompareRow[]>(FALLBACK);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`${API_URL}/public/demo/compare?q=${encodeURIComponent(query)}`);
        const data = await res.json();
        const prices = data?.comparison?.[0]?.prices as Record<string, number> | undefined;
        const bestStore = data?.comparison?.[0]?.best_store as string | undefined;
        if (!cancelled && res.ok && prices && Object.keys(prices).length >= 2) {
          const next = Object.entries(prices)
            .map(([store, price]) => ({
              store: storeLabel(store),
              price,
              best: store === bestStore,
            }))
            .sort((a, b) => a.price - b.price)
            .slice(0, 4);
          setRows(next);
        }
      } catch {
        /* fallback */
      } finally {
        if (!cancelled) setLoaded(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [query]);

  return { rows, loaded };
}
