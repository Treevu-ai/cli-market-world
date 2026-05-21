#!/usr/bin/env python3
"""scan_stores.py — VTEX store scanner. Tests all candidate URLs and keeps only working ones."""

import asyncio, json, sys, time
from pathlib import Path
import httpx

OUTPUT = Path(__file__).parent / "market_stores.py"
PARALLEL = 100; TIMEOUT = 5.0

PATTERNS = [
    ("Carrefour","carrefour","supermercados",{"AR":"com.ar","BR":"com.br","ES":"es","FR":"fr","IT":"it","BE":"be","RO":"ro","PL":"pl"}),
    ("Lider","lider","supermercados",{"CL":"cl"}),
    ("Santa Isabel","santaisabel","supermercados",{"CL":"cl","PE":"pe"}),
    ("Dia","dia","supermercados",{"AR":"com.ar","BR":"com.br","ES":"es","PT":"pt"}),
    ("Walmart","walmart","supermercados",{"MX":"com.mx","CL":"cl","AR":"com.ar","US":"com"}),
    ("Exito","exito","supermercados",{"CO":"com","UY":"uy","EC":"ec"}),
    ("Vea","vea","supermercados",{"AR":"com.ar"}),
    ("Jumbo","jumbo","supermercados",{"AR":"com.ar","CL":"cl"}),
    ("Coto","coto","supermercados",{"AR":"com.ar"}),
    ("Carulla","carulla","supermercados",{"CO":"com"}),
    ("Olimpica","olimpica","supermercados",{"CO":"com"}),
    ("Chedraui","chedraui","supermercados",{"MX":"com.mx"}),
    ("HEB","heb","supermercados",{"MX":"com.mx"}),
    ("Soriana","soriana","supermercados",{"MX":"com"}),
    ("La Comer","lacomer","supermercados",{"MX":"com.mx"}),
    ("Wong","wong","supermercados",{"PE":"pe"}),
    ("Metro","metro","supermercados",{"PE":"pe"}),
    ("Plaza Vea","plazavea","supermercados",{"PE":"pe"}),
    ("Tottus","tottus","supermercados",{"PE":"pe","CL":"cl","AR":"com.ar"}),
    ("Makro","makro","supermercados",{"PE":"pe","AR":"com.ar","CO":"com.co","BR":"com.br"}),
    ("Sodimac","sodimac","hogar",{"CO":"com.co","CL":"cl","PE":"pe","AR":"com.ar","BR":"com.br","MX":"com.mx","UY":"com.uy"}),
    ("Easy","easy","hogar",{"AR":"com.ar","CL":"cl","CO":"co","PE":"pe","UY":"com.uy"}),
    ("Homecenter","homecenter","hogar",{"CO":"com.co","CL":"cl","PE":"pe"}),
    ("Promart","promart","hogar",{"PE":"pe"}),
    ("Leroy Merlin","leroymerlin","hogar",{"BR":"com.br","ES":"es","FR":"fr","IT":"it","PT":"pt","PL":"pl","RO":"ro"}),
    ("Ripley","ripley","departamentales",{"CL":"cl","PE":"pe","CO":"co","MX":"com.mx","AR":"com.ar"}),
    ("Falabella","falabella","departamentales",{"CL":"cl","PE":"pe","CO":"co","AR":"com.ar","BR":"com.br","MX":"com.mx","UY":"com.uy"}),
    ("Coppel","coppel","departamentales",{"MX":"com","AR":"com.ar"}),
    ("Liverpool","liverpool","departamentales",{"MX":"com.mx"}),
    ("Sanborns","sanborns","departamentales",{"MX":"com.mx"}),
    ("El Palacio","elpalaciodehierro","departamentales",{"MX":"com"}),
    ("Sears MX","sears","departamentales",{"MX":"com.mx"}),
    ("Motorola","motorola","electro",{"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","ES":"es","IT":"it","DE":"de","US":"com"}),
    ("Electrolux","electrolux","electro",{"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","ES":"es","IT":"it","FR":"fr","DE":"de","SE":"se","PT":"pt","NL":"nl"}),
    ("Whirlpool","whirlpool","electro",{"BR":"com.br","MX":"com.mx","AR":"com.ar","ES":"es","IT":"it","FR":"fr","DE":"de","US":"com","PT":"pt"}),
    ("Samsung","samsung","electro",{"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","ES":"es","FR":"fr","IT":"it","DE":"de","US":"us","PT":"pt"}),
    ("LG","lg","electro",{"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","ES":"es","FR":"fr","IT":"it","DE":"de","US":"us","PT":"pt"}),
    ("Magazine Luiza","magazineluiza","electro",{"BR":"com.br"}),
    ("Casas Bahia","casasbahia","electro",{"BR":"com.br"}),
    ("Ponto Frio","pontofrio","electro",{"BR":"com.br"}),
    ("Alkosto","alkosto","electro",{"CO":"com"}),
    ("C&A","cea","moda",{"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co"}),
    ("Renner","renner","moda",{"BR":"com.br"}),
    ("Riachuelo","riachuelo","moda",{"BR":"com.br"}),
    ("Marisa","marisa","moda",{"BR":"com.br","AR":"com.ar"}),
    ("Hering","hering","moda",{"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co"}),
    ("Leonisa","leonisa","moda",{"CO":"com","PE":"pe","MX":"com.mx","US":"com"}),
    ("Totto","totto","moda",{"CO":"com","PE":"pe","EC":"com","MX":"com.mx"}),
    ("Droga Raia","drogaria","farmacias",{"BR":"com.br"}),
    ("Drogasil","drogasil","farmacias",{"BR":"com.br"}),
    ("Pacheco","drogariaspacheco","farmacias",{"BR":"com.br"}),
    ("Inkafarma","inkafarma","farmacias",{"PE":"pe"}),
    ("Mifarma","mifarma","farmacias",{"PE":"pe"}),
    ("Farmatodo","farmatodo","farmacias",{"CO":"com.co","MX":"com.mx","VE":"com.ve","AR":"com.ar"}),
    ("Cruz Verde","cruzverde","farmacias",{"CO":"com.co","CL":"cl","PE":"pe","MX":"com.mx"}),
    ("Farmacias Guadalajara","farmaciasguadalajara","farmacias",{"MX":"com.mx"}),
    ("Farmacias del Ahorro","farmaciasdelahorro","farmacias",{"MX":"com.mx"}),
    ("Garbarino","garbarino","electro",{"AR":"com.ar"}),
    ("Centauro","centauro","deportes",{"BR":"com.br"}),
    ("Decathlon","decathlon","deportes",{"BR":"com.br","CL":"cl","PE":"pe","CO":"com.co","AR":"com.ar","MX":"com.mx","ES":"es","FR":"fr","IT":"it","PT":"pt","PL":"pl"}),
    ("O Boticario","oboticario","belleza",{"BR":"com.br","PT":"pt","AR":"com.ar","CL":"cl","PE":"pe","CO":"co","MX":"com.mx"}),
    ("Natura","natura","belleza",{"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co","BO":"com.bo","FR":"fr"}),
    ("Office Depot","officedepot","libreria",{"MX":"com.mx","PE":"pe"}),
    ("AutoZone","autozone","autopartes",{"MX":"com.mx","BR":"com.br"}),
    ("Petlove","petlove","mascotas",{"BR":"com.br"}),
    ("Petz","petz","mascotas",{"BR":"com.br"}),
    ("Sam's Club","samsclub","supermercados",{"BR":"com.br","MX":"com.mx","US":"com"}),
    ("Mambo","mambo","supermercados",{"BR":"com.br"}),
]

CURR = {"PE":"PEN","AR":"ARS","BR":"BRL","MX":"MXN","CO":"COP","CL":"CLP","ES":"EUR","FR":"EUR","IT":"EUR","DE":"EUR","PT":"EUR","NL":"EUR","BE":"EUR","PL":"PLN","SE":"SEK","AT":"EUR","RO":"RON","GB":"GBP","US":"USD","UY":"UYU","EC":"USD","BO":"BOB","PY":"PYG","VE":"USD"}

def mk(name,cc):
    n = name.lower().replace(" ","_").replace("-","_").replace("'","").replace("&","and")
    return f"{n}_{cc.lower()}"

candidates = []
for name, domain, line, ccs in PATTERNS:
    for cc, tld in ccs.items():
        candidates.append({"key":mk(name,cc),"name":name,"cc":cc,"url":f"https://www.{domain}.{tld}","line":line,"curr":CURR.get(cc,"USD")})

async def test(client, c):
    url = f"{c['url']}/api/catalog_system/pub/products/search/leche?_from=0&_to=1"
    try:
        r = await client.get(url)
        if r.status_code in (200,206):
            d = r.json(); n = len(d) if isinstance(d,list) else 0
            return {"ok":True,"n":n,"c":c}
        return {"ok":False,"c":c}
    except: return {"ok":False,"c":c}

async def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample",type=int,default=0)
    ap.add_argument("--parallel",type=int,default=PARALLEL)
    args = ap.parse_args()
    
    cands = candidates
    if args.sample: 
        import random; cands = random.sample(cands, min(args.sample,len(cands)))
    
    print(f"Testing {len(cands)} candidates...")
    t0 = time.monotonic()
    sem = asyncio.Semaphore(args.parallel)
    async def bd(c):
        async with sem: return await test(client,c)
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True, headers={"User-Agent":"CLI-Market-Scanner/1.0"}) as client:
        results = await asyncio.gather(*[bd(c) for c in cands])
    
    working = [r for r in results if r["ok"]]
    elapsed = time.monotonic()-t0
    print(f"\n{len(working)} working | {len(results)-len(working)} failed | {elapsed:.1f}s")
    
    if working:
        lines_s = set(); cc_s = set()
        code = f"# Auto-generated — scanned {len(working)} verified VTEX stores\nSTORES = {{\n"
        for r in working:
            c = r["c"]
            code += f'    "{c["key"]}": {{"name":"{c["name"]} {c["cc"]}","base":"{c["url"]}","country":"{c["cc"]}","currency":"{c["curr"]}","emoji":"","line":"{c["line"]}"}},\n'
            lines_s.add(c["line"]); cc_s.add(c["cc"])
        code += "}\n"
        print(f"Countries: {len(cc_s)}  Lines: {len(lines_s)}")
        for r in working[:30]:
            c = r["c"]; print(f"  {c['name']:<20} {c['cc']} {c['curr']:<4} {c['line']:<18} ({r['n']} prod)")
        if len(working)>30: print(f"  ... and {len(working)-30} more")
        with open(OUTPUT,"w") as f: f.write(code)
        print(f"\nWrote {OUTPUT}")
    else:
        print("No working stores found.")

if __name__ == "__main__":
    asyncio.run(main())
