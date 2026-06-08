#!/usr/bin/env node
/** Rasterize OG SVG → PNG. Run from landing/: node scripts/rasterize_og.mjs public/og.svg public/og.png */
import { readFileSync, writeFileSync } from "node:fs";
import { Resvg } from "@resvg/resvg-js";

const [svgPath, pngPath] = process.argv.slice(2);
if (!svgPath || !pngPath) {
  console.error("Usage: node scripts/rasterize_og.mjs <in.svg> <out.png>");
  process.exit(1);
}

const svg = readFileSync(svgPath);
const width = svgPath.includes("preview") ? 800 : 1200;
const resvg = new Resvg(svg, { fitTo: { mode: "width", value: width } });
writeFileSync(pngPath, resvg.render().asPng());
console.log(`Wrote ${pngPath}`);