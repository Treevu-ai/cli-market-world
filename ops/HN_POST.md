# Show HN: CLI Market — Commerce infrastructure for AI agents (38 retailers, 8 countries)

**Title:** Show HN: CLI Market — My agent shops at 38 verified retailers across 8 countries. One API.

**URL:** https://cli-market.dev

**Text:**

AI agents can't comparison-shop in physical retail. Every store has its own auth, search logic, and checkout flow. Agents fail before the first query.

CLI Market fixes this: one `pip install`, one API across 80 retailers (40 verified) in 8 countries. 22 curated MCP tools (46 legacy). ~50,000+ real prices refreshed every 4 hours. Checkout via PayPal (API) or QR (Yape/Plin).

---

How it works:

- **Search:** `market search "leche" --country PE` → prices from Metro, Wong, Plaza Vea in <2s
- **Compare:** `market basket leche:2 arroz:1` → compares full cart across 9 supermarkets
- **Checkout:** `market checkout --payment yape` → generates QR, confirms via webhook

---

Built in Python. MIT licensed. Open source.

The hard part isn't the code — it's maintaining connectors for 80 retailers whose APIs change without notice. We have VTEX, Shopify, and Magento connectors running a collector daemon every 4 hours. ~51,000+ prices indexed so far, growing to 200K+ as we roll out full catalog downloads.

Would love feedback from anyone building AI agents or working on retail infrastructure.

Site: https://cli-market.dev · PyPI: https://pypi.org/project/cli-market-world/
Demo: https://cli-market.dev (the landing has a 60s terminal GIF showing a full agent checkout)

---

**First comment (post immediately after submission):**

I built this because I realized the bottleneck for AI shopping agents isn't the LLM — it's the commerce data layer. Every agent I built needed to scrape 30 websites just to answer "what's the cheapest milk near me?"

The project started as a single VTEX connector and grew to 36 verified retailers across Peru, Argentina, Brazil, Mexico, Colombia, Chile, the US, and more. We're now working on full catalog downloads (200K+ prices) and a 90-day historical price archive for inflation tracking.

Retailers can list for free — if you run a Shopify or Magento store, we just need a read-only API token. MIT license, no lock-in.
