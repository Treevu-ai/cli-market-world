#!/usr/bin/env node
/** Generate public/favicon.ico from public/favicon.svg (32×32 PNG-in-ICO, no extra deps). */
import { readFileSync, writeFileSync, unlinkSync } from "node:fs";
import { Resvg } from "@resvg/resvg-js";

const svgPath = "public/favicon.svg";
const pngPath = "public/favicon-32.png";
const icoPath = "public/favicon.ico";

function pngBufferToIco(png) {
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(1, 4);

  const entry = Buffer.alloc(16);
  entry[0] = 32;
  entry[1] = 32;
  entry.writeUInt16LE(1, 4);
  entry.writeUInt16LE(32, 6);
  entry.writeUInt32LE(png.length, 8);
  entry.writeUInt32LE(6 + 16, 12);

  return Buffer.concat([header, entry, png]);
}

const svg = readFileSync(svgPath);
const resvg = new Resvg(svg, { fitTo: { mode: "width", value: 32 } });
const png = resvg.render().asPng();
writeFileSync(pngPath, png);

const ico = pngBufferToIco(png);
writeFileSync(icoPath, ico);
unlinkSync(pngPath);

console.log(`Wrote ${icoPath} (${ico.length} bytes)`);
