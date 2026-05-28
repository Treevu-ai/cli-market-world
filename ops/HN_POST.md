# Show HN: CLI Market — Commerce infrastructure for AI agents (30 retailers, 7 countries)

**Title:** Show HN: CLI Market — My agent shops at 30 stores across 7 countries. One API.

**URL:** https://cli-market.dev

**Text:**

AI agents can't comparison-shop in physical retail. Every store has its own auth, search logic, and checkout flow. Agents fail before the first query.

CLI Market fixes this: one `pip install`, one API across 30 verified retailers in 7 countries. 36 MCP tools. 13,000+ real prices refreshed every 8 hours. Checkout via Yape, Plin, Wise, PayPal, or Lemon.

---

How it works:

- **Search:** `market search "leche" --country PE` → prices from Metro, Wong, Plaza Vea in <2s
- **Compare:** `market basket leche:2 arroz:1` → compares full cart across 9 supermarkets
- **Checkout:** `market checkout --payment yape` → generates QR, confirms via webhook

---

Built in Python. MIT licensed. Open source.

The hard part isn't the code — it's maintaining connectors for 30 retailers whose APIs change without notice. We have VTEX, Shopify, and Magento connectors running a collector daemon every 8 hours. ~13K prices indexed so far, growing to 200K+ as we roll out full catalog downloads.

Would love feedback from anyone building AI agents or working on retail infrastructure.

Repo: https://github.com/Treevu-ai/cli-market-world
Demo: https://cli-market.dev (the landing has a 60s terminal GIF showing a full agent checkout)

---

**First comment (post immediately after submission):**

I built this because I realized the bottleneck for AI shopping agents isn't the LLM — it's the commerce data layer. Every agent I built needed to scrape 30 websites just to answer "what's the cheapest milk near me?"

The project started as a single VTEX connector and grew to 30 retailers across Peru, Argentina, Brazil, Mexico, Colombia, Chile, and the US. We're now working on full catalog downloads (200K+ prices) and a 90-day historical price archive for inflation tracking.

Retailers can list for free — if you run a Shopify or Magento store, we just need a read-only API token. MIT license, no lock-in.
