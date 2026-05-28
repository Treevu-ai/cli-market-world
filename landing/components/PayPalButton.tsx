"use client"
import { useState } from "react"
import { useLang } from "@/lib/LanguageContext"

export default function PayPalButton() {
  const { lang } = useLang()
  const isES = lang === "es"
  const [loading, setLoading] = useState(false)

  const subscribe = async () => {
    setLoading(true)
    try {
      const r1 = await fetch("https://cli-market-production.up.railway.app/auth/register", { method: "POST" })
      const { api_key } = await r1.json()
      const r2 = await fetch("https://cli-market-production.up.railway.app/billing/paypal", {
        method: "POST", headers: { "Authorization": `Bearer ${api_key}` },
      })
      const data = await r2.json()
      if (data.approve_url) window.location.href = data.approve_url
      else { alert(data.error || "PayPal error"); setLoading(false) }
    } catch { setLoading(false) }
  }

  return (
    <button onClick={subscribe} disabled={loading}
      className="inline-flex items-center justify-center rounded-3xl text-sm font-semibold px-6 py-3 transition-colors w-full bg-[var(--wise-green)] text-[var(--wise-ink)] hover:bg-[var(--wise-green-hover)] disabled:opacity-50">
      {loading ? (isES ? "Conectando..." : "Connecting...") : (isES ? "Suscribirse con PayPal" : "Subscribe with PayPal")}
    </button>
  )
}
