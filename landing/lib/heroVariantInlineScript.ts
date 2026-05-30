import { MARKET_STATS } from "@/lib/marketStats";
import { HERO_H1_COPY, HERO_VARIANT_COOKIE, HERO_VARIANT_COOKIE_MAX_AGE, HERO_VARIANT_IDS } from "@/lib/heroVariants";

function defaultPriceChip(): string {
  const n = parseInt(MARKET_STATS.pricesVerifiedLabel.replace(/\D/g, ""), 10) || 43000;
  return `${Math.round(n / 1000)}K+`;
}

/** Blocking inline script — runs before paint to avoid H1 flash when AB is on. */
export function buildHeroVariantInlineScript(): string {
  const copyJson = JSON.stringify(HERO_H1_COPY);
  const priceChip = defaultPriceChip();

  return `(function(){
var V=${JSON.stringify([...HERO_VARIANT_IDS])};
var C=${JSON.stringify(HERO_VARIANT_COOKIE)};
var MAX=${HERO_VARIANT_COOKIE_MAX_AGE};
var H=${copyJson};
var PF=${JSON.stringify(priceChip)};
function gc(n){var m=document.cookie.match(new RegExp("(?:^|; )"+n+"=([^;]*)"));return m?decodeURIComponent(m[1]):"";}
function sc(n,v){document.cookie=n+"="+encodeURIComponent(v)+";path=/;max-age="+MAX+";SameSite=Lax";}
var p=new URLSearchParams(location.search);
var v=(p.get("hero")||"").toLowerCase();
if(V.indexOf(v)<0)v=gc(C);
if(V.indexOf(v)<0)v=V[Math.floor(Math.random()*V.length)];
sc(C,v);
document.documentElement.dataset.heroVariant=v;
var lang=(document.documentElement.lang||"es")==="en"?"en":"es";
var el=document.getElementById("hero-h1");
if(el&&H[v]){
  var t=H[v][lang]||H[v].es;
  el.textContent=t.replace("{priceChip}",PF);
}
})();`;
}
