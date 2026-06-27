# Phase E — Spoke visual QA report

**Date:** 2026-06-27  
**Branch:** `cursor/landing-icp-hub-prd-4376`  
**PRD:** `docs/prd-landing-spoke-design-system.md` § Fase E

## Automated checks

| Check | Result |
|-------|--------|
| `npm run build` | ✅ Pass |
| `node scripts/spoke-qa.mjs` | ✅ 36 static checks |
| `node scripts/spoke-qa.mjs --live http://127.0.0.1:3456` | ✅ 47 checks (incl. HTTP 200 + 1× H1 per route) |
| `node scripts/spoke-screenshots.mjs` | ✅ 8 screenshots (4 routes × desktop/mobile) |

Run locally:

```bash
cd landing
npm run build
npx serve out -l 3456
npm run qa:spoke
npm run qa:spoke -- --live http://127.0.0.1:3456
node scripts/spoke-screenshots.mjs http://127.0.0.1:3456
```

## Screenshot matrix

Artifacts: `landing/qa-screenshots/`

| Route | Desktop | Mobile | H1 | Hub link |
|-------|---------|--------|----|----------|
| `/` (hub) | `hub-desktop.png` | `hub-mobile.png` | 1 | n/a |
| `/build` | `build-desktop.png` | `build-mobile.png` | 1 | ✅ |
| `/intelligence` | `intelligence-desktop.png` | `intelligence-mobile.png` | 1 | ✅ |
| `/retailers` | `retailers-desktop.png` | `retailers-mobile.png` | 1 | ✅ |

## Lighthouse accessibility (static export, local serve)

| Route | Score |
|-------|-------|
| `/` | 94 |
| `/build` | 96 |
| `/intelligence` | 95 |
| `/retailers` | 96 |

> Full Lighthouse JSON omitted from repo (regenerate with `npx lighthouse` against served `out/`).

## Cross-spoke acceptance

- [x] 3 spokes use `SpokePageShell` (glow + `brand-mode-operations` on retailers)
- [x] Exactly one `<h1>` per route (verified live)
- [x] Hero eyebrow `stripe-tag-soft` on all spokes
- [x] Hero CTAs `btn-mint` / `btn-outline` only
- [x] Body sections use `landing-section` + `landing-container-wide`
- [x] No legacy hex in spoke components (Pricing enterprise link retokenized in Phase E)
- [x] `← CLI Market` hub link present on all 3 spokes (live DOM)
- [x] `ErrorBoundary` via `SpokePageShell`

## Per-spoke

**Build** — MCP + verified prices + Free chips; Pricing + FAQ + checkout panel present.

**Intelligence** — No `#0369a1`; Commerce Pulse embed section; `IntelligenceFAQ`; `SpokeFinalCTA`.

**Retailers** — No `grid-bg` / `ScrambleText`; apply modal via hero + final CTA; orange step circles.

## Manual follow-ups (non-blocking)

- [ ] Visual diff review of screenshots in PR (founder design sign-off)
- [ ] Checkout E2E on `/build#pricing` against prod billing (requires secrets)

## Fixes applied in Phase E

- `Pricing.tsx`: enterprise contact link → design tokens
- `SpokeStepsSection.tsx`: step circle gradient → `--cm-mint-dim` / `--cm-mint`
- New QA scripts: `scripts/spoke-qa.mjs`, `scripts/spoke-screenshots.mjs`
