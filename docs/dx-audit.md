---
title: DX Audit — CLI Market
tags:
  - gtm
  - dx
  - mcp
hub: "[[GTM-Hub]]"
author: Developer Advocate + MCP Builder (Agency Agents)
date: 2026-05-28
status: shipped
---

# DX Audit — Time to First Success

**Goal:** A new Cursor user goes from `pip install cli-market-world` → first successful MCP search in **<10 minutes**.

## Journey map

| Step | Command / action | Friction (1–5) | Notes |
|------|------------------|----------------|-------|
| 1. Install | `pip install cli-market-world` | 1 | PyPI OK; post-install `market hello` guides next steps ✅ |
| 2. Discover MCP | Read README or `/tools` | 2 | `/tools` has copy-paste configs ✅ |
| 3. Configure Cursor | Add `mcp.json` server entry | 3 | Needs `python -m market_mcp` path; `/tools` reduces this |
| 4. Auth | `market login` or `market_login` MCP | 2 | Demo creds in README; token persisted locally |
| 5. First search | `market search "leche" --country PE` | 1 | Works offline against API |
| 6. First MCP search | `market_search` in agent chat | 3 | Model must pick tool; improved descriptions below |

**Estimated happy path:** 6–8 min (experienced dev), 12–15 min (first MCP user).

## Findings

### ✅ Strengths

- `market hello` post-install onboarding with CTA to MCP + GitHub
- 22 MCP tools cover full commerce loop (search → cart → checkout)
- `/tools` page with Cursor/Claude/Windsurf configs
- `llms.txt` + `server.json` for agent discovery
- JSON output flags on CLI for agent consumption

### ⚠️ Gaps (prioritized)

| # | Issue | Impact | Fix |
|---|-------|--------|-----|
| 1 | MCP tool names not prefixed consistently in model prompts | Model picks wrong tool | Descriptions now say "Call FIRST: market_login" |
| 2 | `market_add` requires 4 fields from search result | Agent drops fields | Description lists exact field mapping |
| 3 | No GitHub issue template for agent integration | Feedback lost | Add `.github/ISSUE_TEMPLATE/agent-integration.md` |
| 4 | Error messages from API not surfaced in MCP | Dead ends | MCP returns JSON error with `hint` field |
| 5 | Quickstart assumes Fly.io API URL | Local dev confusion | `market hello` prints active API base |

## MCP tool description improvements (shipped 2026-05-28)

Updated in `market_mcp.py`:

- **market_login** — explicit "required before cart/checkout"
- **market_search** — returns `store_key` for `market_add`; suggest `market_lines` first
- **market_compare** — when to use vs `market_search`
- **market_add** — field copy-paste mapping from search JSON
- **market_checkout** — payment methods list + sandbox note

## Recommended quickstart (copy-paste)

```bash
pip install cli-market-world
market hello
market login --username demo --password demo
market search "leche" --country PE --json
```

**Cursor MCP config** (see full configs at https://cli-market.dev/tools):

```json
{
  "mcpServers": {
    "cli-market": {
      "command": "python",
      "args": ["-m", "market_mcp"],
      "env": {}
    }
  }
}
```

## Metrics to track

| Metric | Baseline | Target (30d) |
|--------|----------|--------------|
| Time to first MCP search | ~15 min (estimate) | <10 min |
| GitHub issues tagged `agent-integration` | 0 | 5+ |
| PyPI installs → `market hello` run rate | unknown | 30% |

## Next sprint

1. Add `.github/ISSUE_TEMPLATE/agent-integration.md`
2. Record 60s terminal GIF for README + LinkedIn Day 1
3. Add `market doctor` command (env check + API ping + auth status)

[[GTM-Hub]] · [[growth-channels]]
