#!/usr/bin/env node
/** Generate public/favicon.ico from public/favicon.svg (32×32). */
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";
import { Resvg } from "@resvg/resvg-js";
import toIco from "to-ico";

const svgPath = "public/favicon.svg";
const pngPath = "public/favicon-32.png";
const icoPath = "public/favicon.ico";

const svg = readFileSync(svgPath);
const resvg = new Resvg(svg, { fitTo: { mode: "width", value: 32 } });
writeFileSync(pngPath, resvg.render().asPng());

const ico = await toIco([readFileSync(pngPath)]);
writeFileSync(icoPath, ico);
unlinkSync(pngPath);

console.log(`Wrote ${icoPath} (${ico.length} bytes)`);
