#!/usr/bin/env node
/**
 * Phase E — capture hub + spoke screenshots (desktop + mobile).
 * Usage: node scripts/spoke-screenshots.mjs http://127.0.0.1:3000
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const baseUrl = process.argv[2] || "http://127.0.0.1:3000";
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const outDir = path.join(root, "qa-screenshots");

const routes = [
  { name: "hub", path: "/" },
  { name: "build", path: "/build" },
  { name: "intelligence", path: "/intelligence" },
  { name: "retailers", path: "/retailers" },
];

const viewports = [
  { tag: "desktop", width: 1280, height: 900 },
  { tag: "mobile", width: 390, height: 844 },
];

fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const results = [];

for (const vp of viewports) {
  const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
  const page = await context.newPage();

  for (const route of routes) {
    const url = `${baseUrl.replace(/\/$/, "")}${route.path}`;
    await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
    await page.waitForTimeout(500);

    const h1Count = await page.locator("h1").count();
    const hubLink = await page.getByRole("link", {
      name: /CLI Market — (elegir otro perfil|choose another profile)/,
    }).count();

    const file = `${route.name}-${vp.tag}.png`;
    await page.screenshot({ path: path.join(outDir, file), fullPage: true });

    results.push({
      route: route.path,
      viewport: vp.tag,
      file,
      h1Count,
      hubLinkVisible: route.path === "/" ? "n/a" : hubLink > 0,
      url,
    });
  }

  await context.close();
}

await browser.close();

const reportPath = path.join(outDir, "report.json");
fs.writeFileSync(reportPath, JSON.stringify({ capturedAt: new Date().toISOString(), baseUrl, results }, null, 2));

console.log(`Screenshots saved to ${outDir}`);
console.log(`Report: ${reportPath}`);
for (const r of results) {
  console.log(`  ${r.file} — H1=${r.h1Count} hubLink=${r.hubLinkVisible}`);
}

const badH1 = results.filter((r) => r.h1Count !== 1);
if (badH1.length) {
  console.error("\nH1 audit failed:", badH1);
  process.exit(1);
}
