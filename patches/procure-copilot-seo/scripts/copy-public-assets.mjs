#!/usr/bin/env node
/** Copy public/ root files into .open-next/assets (OpenNext Workers). */
import { copyFileSync, existsSync, mkdirSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const publicDir = "public";
const assetsDir = ".open-next/assets";

if (!existsSync(assetsDir)) {
  console.error("missing .open-next/assets — run opennext build first");
  process.exit(1);
}

const rootFiles = readdirSync(publicDir).filter((name) => {
  const p = join(publicDir, name);
  return statSync(p).isFile();
});

for (const name of rootFiles) {
  copyFileSync(join(publicDir, name), join(assetsDir, name));
  console.log(`copied public/${name} → .open-next/assets/${name}`);
}
