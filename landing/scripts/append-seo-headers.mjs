#!/usr/bin/env node
/** Append Cloudflare Pages _headers for generated sitemap XML files. */
import { appendFileSync, existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

const outDir = "out";
const headersPath = join(outDir, "_headers");

if (!existsSync(headersPath)) {
  console.error("missing out/_headers — run next build first");
  process.exit(1);
}

const sitemapFiles = readdirSync(outDir).filter(
  (name) => name === "sitemap.xml" || /^sitemap-\d+\.xml$/.test(name),
);

if (sitemapFiles.length === 0) {
  console.warn("no sitemap*.xml in out/ — skipping header append");
  process.exit(0);
}

const block = sitemapFiles
  .map(
    (name) => `/${name}
  Content-Type: application/xml; charset=utf-8
  Access-Control-Allow-Origin: *
  Cache-Control: public, max-age=3600, must-revalidate
`,
  )
  .join("\n");

appendFileSync(headersPath, `\n${block}`);
for (const name of sitemapFiles) {
  console.log(`appended _headers for /${name}`);
}
