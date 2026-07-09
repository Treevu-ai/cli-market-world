"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import HouseholdSetupForm from "@/components/HouseholdSetupForm";
import BudgetSummaryWidget from "@/components/BudgetSummaryWidget";
import ReceiptScanner from "@/components/ReceiptScanner";
import BasketOptimizer from "@/components/BasketOptimizer";
import EcosystemRadarWidget from "@/components/EcosystemRadarWidget";
import InflationPulseWidget from "@/components/InflationPulseWidget";
import PriceAlertsWidget from "@/components/PriceAlertsWidget";
import { API_URL } from "@/lib/api";

type Tab = "canasta" | "radar" | "perfil" | "tickets";

export default function HouseholdDashboard() {
  const [apiKey, setApiKey] = useState("");
  const [confirmedKey, setConfirmedKey] = useState("");
  const [tab, setTab] = useState<Tab>("canasta");
  const [budgetRefresh, setBudgetRefresh] = useState(0);
  const [profileCountry, setProfileCountry] = useState("PE");

  const isAuth = !!confirmedKey;

  const handleAuth = () => {
    if (apiKey.trim().startsWith("sk-") || apiKey.trim().startsWith("demo-")) {
      setConfirmedKey(apiKey.trim());
    }
  };

  // Load country from household profile on auth
  useEffect(() => {
    if (!confirmedKey) return;
    fetch(`${API_URL}/v1/household`, {
      headers: { Authorization: `Bearer ${confirmedKey}` },
    })
      .then((r) => r.json())
      .then((b) => {
        const country = (b?.data ?? b)?.country;
        if (country) setProfileCountry(country);
      })
      .catch(() => {});
  }, [confirmedKey, budgetRefresh]);

  const TAB_LABELS: Record<Tab, string> = {
    canasta: "Canasta",
    radar: "Radar",
    perfil: "Perfil",
    tickets: "Mis tickets",
  };

  return (
    <>
      <Navbar />
      <main className="min-h-screen bg-[var(--cm-surface)] pt-20 pb-24">
        <div className="max-w-2xl mx-auto px-4 sm:px-6">

          {/* Header */}
          <div className="py-10">
            <p className="text-xs font-mono text-[var(--cm-mint)] uppercase tracking-widest mb-2">Mi hogar</p>
            <h1 className="text-2xl font-bold text-[var(--cm-on-surface)] leading-tight">
              Perfil de hogar y tickets
            </h1>
            <p className="mt-2 text-sm text-[var(--cm-on-surface-variant)]">
              Tu presupuesto, canasta, radar de retailers y tickets — en un solo lugar.
            </p>
          </div>

          {/* API Key gate */}
          {!isAuth ? (
            <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] p-6 space-y-4">
              <p className="text-sm font-mono text-[var(--cm-on-surface-variant)]">
                Ingresa tu API key para continuar
              </p>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleAuth()}
                  placeholder="sk-..."
                  className="flex-1 bg-[var(--cm-surface-low)] border border-[var(--cm-outline-variant)] rounded-lg px-3 py-2 text-sm font-mono text-[var(--cm-on-surface)] placeholder:text-[var(--cm-on-surface-variant)]/40 focus:outline-none focus:border-[var(--cm-mint)]"
                />
                <button
                  type="button"
                  onClick={handleAuth}
                  disabled={!apiKey.trim().startsWith("sk-") && !apiKey.trim().startsWith("demo-")}
                  className="px-4 py-2 rounded-lg bg-[var(--cm-mint)] text-[var(--cm-on-mint)] text-sm font-semibold font-mono hover:opacity-90 disabled:opacity-40 transition-opacity"
                >
                  Entrar
                </button>
              </div>
              <p className="text-[11px] font-mono text-[var(--cm-on-surface-variant)]/50">
                ¿No tienes key?{" "}
                <a href="/docs#api-key" className="text-[var(--cm-mint)] hover:underline">
                  Prueba gratis 7 días →
                </a>
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Budget summary — always visible */}
              <BudgetSummaryWidget apiKey={confirmedKey} refreshKey={budgetRefresh} />

              {/* Tabs */}
              <div className="flex gap-1 p-1 rounded-xl bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)]">
                {(["canasta", "radar", "perfil", "tickets"] as Tab[]).map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setTab(t)}
                    className={`flex-1 py-2 rounded-lg text-xs font-mono font-semibold transition-colors ${
                      tab === t
                        ? "bg-[var(--cm-surface-low)] text-[var(--cm-on-surface)] shadow-sm"
                        : "text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-on-surface)]"
                    }`}
                  >
                    {TAB_LABELS[t]}
                  </button>
                ))}
              </div>

              {/* Tab content */}
              <div className="rounded-xl border border-[var(--cm-outline-variant)] bg-[var(--cm-surface-high)] p-6">
                {tab === "canasta" ? (
                  <BasketOptimizer apiKey={confirmedKey} country={profileCountry} />
                ) : tab === "radar" ? (
                  <div className="space-y-8">
                    <EcosystemRadarWidget country={profileCountry} />
                    <div className="border-t border-[var(--cm-outline-variant)] pt-6">
                      <InflationPulseWidget country={profileCountry} apiKey={confirmedKey} />
                    </div>
                    <div className="border-t border-[var(--cm-outline-variant)] pt-6">
                      <PriceAlertsWidget apiKey={confirmedKey} country={profileCountry} />
                    </div>
                  </div>
                ) : tab === "perfil" ? (
                  <HouseholdSetupForm
                    apiKey={confirmedKey}
                    onSaved={(country) => {
                      setProfileCountry(country);
                      setBudgetRefresh((n) => n + 1);
                    }}
                  />
                ) : (
                  <ReceiptScanner apiKey={confirmedKey} />
                )}
              </div>
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
