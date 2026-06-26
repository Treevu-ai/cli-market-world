#!/usr/bin/env node
/** Rasterize OG SVG → PNG. Run: node scripts/rasterize_og.mjs public/og.svg public/og.png */
import { readFileSync, writeFileSync } from "node:fs";
import { Resvg } from "@resvg/resvg-js";

const [svgPath, pngPath] = process.argv.slice(2);
if (!svgPath || !pngPath) {
  console.error("Usage: node scripts/rasterize_og.mjs <in.svg> <out.png>");
  process.exit(1);
}

const svg = readFileSync(svgPath);
const resvg = new Resvg(svg, { fitTo: { mode: "width", value: 1200 } });
writeFileSync(pngPath, resvg.render().asPng());
console.log(`Wrote ${pngPath}`);
