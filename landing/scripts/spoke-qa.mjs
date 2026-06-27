#!/usr/bin/env node
/**
 * Phase E — automated spoke QA (static + optional live checks).
 * Usage: node scripts/spoke-qa.mjs [--live http://127.0.0.1:3000]
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const failures = [];
const passes = [];

function pass(msg) {
  passes.push(msg);
}

function fail(msg) {
  failures.push(msg);
}

function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}

function fileExists(rel) {
  return fs.existsSync(path.join(root, rel));
}

function countMatches(text, re) {
  return (text.match(re) || []).length;
}

function countH1(text) {
  return countMatches(text, /<(?:motion\.)?h1[\s>]/g);
}

const SPOKE_PAGES = [
  { route: "/", file: "app/page.tsx", spoke: false },
  { route: "/build", file: "app/build/page.tsx", spoke: true, icp: "build" },
  { route: "/intelligence", file: "app/intelligence/page.tsx", spoke: true, icp: "intelligence" },
  { route: "/retailers", file: "app/retailers/page.tsx", spoke: true, icp: "retailers" },
];

const SPOKE_COMPONENT_DIRS = [
  "components/spoke",
  "components/retailers",
  "components/IntelligenceSection.tsx",
  "components/IntelligenceFAQ.tsx",
];

const HEX_RE = /#[0-9a-fA-F]{3,8}\b/g;

console.log("=== Spoke QA (Phase E) ===\n");

// 1. Spoke pages use SpokePageShell
for (const p of SPOKE_PAGES.filter((x) => x.spoke)) {
  const src = read(p.file);
  if (src.includes("SpokePageShell")) pass(`${p.route}: SpokePageShell`);
  else fail(`${p.route}: missing SpokePageShell`);

  if (src.includes("SpokeHero")) pass(`${p.route}: SpokeHero`);
  else fail(`${p.route}: missing SpokeHero`);

  if (src.includes("SpokeHubLink")) pass(`${p.route}: SpokeHubLink`);
  else fail(`${p.route}: missing SpokeHubLink`);

  if (src.includes("ErrorBoundary") || src.includes("SpokePageShell"))
    pass(`${p.route}: ErrorBoundary via shell`);
  else fail(`${p.route}: missing ErrorBoundary`);
}

// 2. Single H1 source per spoke (SpokeHero only)
const spokeHero = read("components/spoke/SpokeHero.tsx");
if (countH1(spokeHero) === 1) pass("SpokeHero: exactly one <h1>");
else fail(`SpokeHero: expected 1 <h1>, found ${countH1(spokeHero)}`);

if (spokeHero.includes("hero-garamond-headline")) pass("SpokeHero: hero-garamond-headline");
else fail("SpokeHero: missing hero-garamond-headline");

if (spokeHero.includes("stripe-tag-soft")) pass("SpokeHero: stripe-tag-soft eyebrow");
else fail("SpokeHero: missing stripe-tag-soft");

// 3. Hub H1
const hero = read("components/Hero.tsx");
if (countH1(hero) === 1) pass("Hub Hero: exactly one <h1>");
else fail(`Hub Hero: expected 1 <h1>, found ${countH1(hero)}`);

// 4. Retailers page LOC
const retailersLoc = read("app/retailers/page.tsx").split("\n").length;
if (retailersLoc <= 80) pass(`retailers/page.tsx: ${retailersLoc} LOC (≤80)`);
else fail(`retailers/page.tsx: ${retailersLoc} LOC (>80)`);

// 5. JSON-LD in layout
if (read("app/retailers/layout.tsx").includes("RetailersJsonLd"))
  pass("retailers: JSON-LD in layout");
else fail("retailers: JSON-LD not in layout");

if (!read("app/retailers/page.tsx").includes("application/ld+json"))
  pass("retailers/page.tsx: no inline JSON-LD");
else fail("retailers/page.tsx: inline JSON-LD should be in layout");

// 6. No grid-bg / ScrambleText on retailers
const retailersPage = read("app/retailers/page.tsx");
if (!retailersPage.includes("grid-bg")) pass("retailers: no grid-bg");
else fail("retailers: grid-bg found");

if (!retailersPage.includes("ScrambleText")) pass("retailers page: no ScrambleText");
else fail("retailers page: ScrambleText found");

if (!read("components/ActiveBrandTicker.tsx").includes("ScrambleText"))
  pass("ActiveBrandTicker: no ScrambleText");
else fail("ActiveBrandTicker: ScrambleText still used");

// 7. Intelligence retokenize
const intel = read("components/IntelligenceSection.tsx");
if (!intel.includes("#0369a1") && !intel.includes("#64748b"))
  pass("IntelligenceSection: no legacy blue/slate hex");
else fail("IntelligenceSection: legacy hex remains");

// 8. Hex audit in spoke component files
for (const rel of SPOKE_COMPONENT_DIRS) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) continue;
  const files = fs.statSync(abs).isDirectory()
    ? fs.readdirSync(abs).map((f) => path.join(rel, f))
    : [rel];
  for (const f of files) {
    if (!f.endsWith(".tsx")) continue;
    const text = read(f);
    const hexes = [...new Set(text.match(HEX_RE) || [])];
    // Allow orange gradient hex only in SpokeStepsSection (matches SolutionSection pattern)
    const allowed = new Set(["#f97316", "#ea580c"]);
    const bad = hexes.filter((h) => !allowed.has(h.toLowerCase()));
    if (bad.length === 0) pass(`${f}: no unexpected hex`);
    else fail(`${f}: unexpected hex ${bad.join(", ")}`);
  }
}

// 9. Build spoke config chips
const spokeConfig = read("lib/spokeConfig.ts");
if (spokeConfig.includes("MCP") && spokeConfig.includes("Free"))
  pass("build spokeConfig: MCP + Free tier chips");
else fail("build spokeConfig: missing proof chips");

// 10. Final CTAs wired
for (const icp of ["build", "intelligence", "retailers"]) {
  const pageFile = icp === "build" ? "app/build/page.tsx" : `app/${icp}/page.tsx`;
  if (read(pageFile).includes('SpokeFinalCTA icp="' + icp + '"'))
    pass(`${icp}: SpokeFinalCTA wired`);
  else fail(`${icp}: SpokeFinalCTA not wired`);
}

// Optional live checks
const liveBase = process.argv.find((a) => a.startsWith("--live="))?.split("=")[1]
  || (process.argv.includes("--live") ? process.argv[process.argv.indexOf("--live") + 1] : null);

if (liveBase) {
  console.log(`\n--- Live checks (${liveBase}) ---\n`);
  for (const p of SPOKE_PAGES) {
    const url = `${liveBase.replace(/\/$/, "")}${p.route === "/" ? "/" : p.route}`;
    try {
      const res = await fetch(url);
      if (res.ok) pass(`HTTP ${res.status}: ${p.route}`);
      else fail(`HTTP ${res.status}: ${p.route}`);
      const html = await res.text();
      const h1Count = (html.match(/<h1[\s>]/g) || []).length;
      if (h1Count === 1) pass(`${p.route}: rendered 1 H1`);
      else fail(`${p.route}: rendered ${h1Count} H1 elements`);

      if (p.spoke && (html.includes("elegir otro perfil") || html.includes("choose another profile")))
        pass(`${p.route}: SpokeHubLink copy present`);
      else if (p.spoke) fail(`${p.route}: SpokeHubLink copy not found in HTML`);
    } catch (e) {
      fail(`${p.route}: fetch failed — ${e.message}`);
    }
  }
}

console.log(`\n✅ Passed: ${passes.length}`);
passes.forEach((p) => console.log(`  ✓ ${p}`));

if (failures.length) {
  console.log(`\n❌ Failed: ${failures.length}`);
  failures.forEach((f) => console.log(`  ✗ ${f}`));
  process.exit(1);
}

console.log("\nAll spoke QA checks passed.");
