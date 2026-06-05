# CLI Market — Terminal Demo

> **What happens in 60 seconds.** Copy-paste-able. Every command works with the free tier.

---

## 0. Install (once)

```bash
pip install cli-market
```

---

## 1. First contact

```bash
$ market hello

  CLI Market v1.8.0
  ---------------
  45,000+ verified shelf prices  66 retailers (36 active)  8 countries

  Your API key is ready.
  Plan: Free — 1,000 requests/day

  Try:
    market search "leche" --country PE
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
  prod_primor_aceites_0.9l · 4 retailers
```

---

## 4. Build a basket

```bash
$ market basket "arroz:1 aceite:1 leche:2" --country AR

  Your basket × Argentina
  ┌──────────┬─────────┬──────────┬──────────┬──────────┬──────────┐
  │ Item     │ Qty     │ Vea      │ Carrefour│ Jumbo    │ Dia      │
  ├──────────┼─────────┼──────────┼──────────┼──────────┼──────────┤
  │ Arroz    │ 1       │ 890      │ 920      │ 950      │ 880      │
  │ Aceite   │ 1       │ 1,180    │ 1,200    │ 1,350    │ 1,220    │
  │ Leche    │ 2       │ 1,560    │ 1,580    │ 1,640    │ 1,600    │
  ├──────────┼─────────┼──────────┼──────────┼──────────┼──────────┤
  │ TOTAL    │         │ 3,630    │ 3,700    │ 3,940    │ 3,700    │
  └──────────┴─────────┴──────────┴──────────┴──────────┴──────────┘

  Best: Vea at ARS 3,630 · Save 8% vs Jumbo
```

---

## 5. Checkout

```bash
$ market checkout --payment yape

  Order #ORD-2026-0605-001
  Total: ARS 3,630 (~USD 3.85)
  Store: Vea

  [QR code generated]

  Scan with Yape to pay.
  You'll receive confirmation at hello@cli-market.dev
```

---

## 6. Ask in natural language

```bash
$ market ask "what's the cheapest rice in Peru under 5 soles per kilo"

  Arroz Extra Costeño 1kg — PEN 4.20/kg at Plaza Vea
  Arroz Superior Paisana 1kg — PEN 4.50/kg at Metro
  Arroz Extra Molinera 1kg — PEN 4.80/kg at Tottus

  Cheapest: Costeño at PEN 4.20/kg (Plaza Vea)
  5 more results above PEN 5.00/kg available on Pro plan.
```

---

## 7. Set a price alert

```bash
$ market alerts create \
  --product "aceite de girasol 900ml" \
  --country AR \
  --below 1100

  Alert created.
  We'll email you when any retailer drops below ARS 1,100.

$ market alerts list

  Alerts (1)
  ┌──────────────────────────────┬────────┬──────────┬─────────┐
  │ Product                      │ Country│ Threshold│ Channel │
  ├──────────────────────────────┼────────┼──────────┼─────────┤
  │ Aceite de Girasol 900ml      │ AR     │ < 1,100  │ email   │
  └──────────────────────────────┴────────┴──────────┴─────────┘
```

---

## 8. Get platform stats

```bash
$ market stats

  CLI Market Stats
  ────────────────
  Prices tracked:    45,387
  Retailers active:  36 of 66
  Countries:         8
  MCP tools:         43
  Last refresh:      June 5, 2026 14:00 UTC
  Your API key:      Free tier · 1,000 req/day · 892 remaining today
```

---

**Try it.** `pip install cli-market` · `market hello` · No credit card.

[cli-market.dev](https://cli-market.dev)
