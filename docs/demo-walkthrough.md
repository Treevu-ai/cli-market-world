# CLI Market — Terminal Demo

> **What happens in 60 seconds.** Copy-paste-able. Free tier commands marked clearly.

---

## 0. Install (once)

```bash
pip install cli-market-world
```

---

## 1. First contact

```bash
$ market hello
# or: market init   (guided onboarding — API + account + MCP)
```

```bash
$ market init

  Onboarding completo
  OK API → cuenta gratuita → doctor 95% readiness → snippet MCP
```

```bash
$ market register

  Cuenta creada
  Usuario: user-abc123...
  API key: sk-...   ← save it now (shown once)
```

```bash
$ market doctor

  95% readiness — Listo para search e integracion MCP
```

Or, if you already have credentials: `market login`

```bash
$ market whoami

  ✓ user-abc123...  tier: free
  limits: 1,000/day · 60/min · alerts: 0 · checkout: no
```

---

## 2. Search a product

```bash
$ market search "leche" --country PE

  Leche Entera Gloria 1L
  ┌──────────────┬────────┬──────────────┐
  │ Store        │ Price  │ Price per L  │
  ├──────────────┼────────┼──────────────┤
  │ Plaza Vea    │ 4.50   │ 4.50/L       │
  │ Tottus       │ 4.45   │ 4.45/L       │
  │ Metro        │ 4.60   │ 4.60/L       │
  │ Wong         │ 4.80   │ 4.80/L       │
  └──────────────┴────────┴──────────────┘

  4 results · prod_gloria_lacteos_1l · confidence 98%
```

---

## 3. Compare across retailers

```bash
$ market compare "aceite de girasol 900ml" --country AR

  Aceite de Girasol 900ml — Argentina
  ┌──────────────┬────────────┬──────────────┐
  │ Store        │ Price (ARS)│ Price per L  │
  ├──────────────┼────────────┼──────────────┤
  │ Vea          │ 1,180      │ 1,311/L      │
  │ Carrefour    │ 1,200      │ 1,333/L      │
  │ Jumbo        │ 1,350      │ 1,500/L      │
  │ Dia          │ 1,220      │ 1,355/L      │
  └──────────────┴────────────┴──────────────┘

  Best: Vea at ARS 1,180 (saves 14% vs Jumbo)
```

---

## 4. Build a basket

```bash
$ market basket "arroz:1 aceite:1 leche:2" --country AR

  Best: Vea at ARS 3,630 · Save 8% vs Jumbo
```

---

## 5. Checkout (Pro plan)

```bash
$ market checkout --payment yape
```

Requires **Pro** tier (`market upgrade --email you@example.com`). Free tier returns 403 with upgrade hint.

---

## 6. Ask in natural language

```bash
$ market ask "what's the cheapest rice in Peru under 5 soles per kilo"

  Cheapest: Costeño at PEN 4.20/kg (Plaza Vea)
```

---

## 7. Platform stats

```bash
$ market stats

  CLI Market Stats
  ────────────────
  Prices tracked:    45,387
  Retailers active:  38 of 68
  Countries:         8
  MCP tools:         43
  Last refresh:      every 4h
```

---

## Appendix — Starter+ only

**Price alerts** (Starter plan and above):

```bash
$ market alerts create --product "aceite" --country AR --threshold 1100
$ market alerts list
```

---

**Try it.** `pip install cli-market-world` · `market register` · No credit card.

[cli-market.dev](https://cli-market.dev)