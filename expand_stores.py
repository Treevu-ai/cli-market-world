#!/usr/bin/env python3
"""expand_stores.py — Expande retailers a ~1000 aplicando patrones por país sobre VTEX."""

import csv
from pathlib import Path

CURRENCIES = {
    "PE":"PEN","AR":"ARS","BR":"BRL","MX":"MXN","CO":"COP","CL":"CLP","ES":"EUR","FR":"EUR","IT":"EUR","DE":"EUR","GB":"GBP","PT":"EUR","NL":"EUR","BE":"EUR","PL":"PLN","SE":"SEK","DK":"DKK","FI":"EUR","NO":"NOK","AT":"EUR","CH":"CHF","IE":"EUR","GR":"EUR","CZ":"CZK","RO":"RON","HU":"HUF","SK":"EUR","BG":"BGN","HR":"EUR","SI":"EUR","UY":"UYU","EC":"USD","BO":"BOB","PY":"PYG","VE":"USD","CR":"CRC","GT":"GTQ","SV":"USD","PA":"USD","DO":"DOP","US":"USD","CA":"CAD","AU":"AUD","NZ":"NZD","JP":"JPY","KR":"KRW","CN":"CNY","TW":"TWD","HK":"HKD","SG":"SGD","TH":"THB","IN":"INR","MY":"MYR","ID":"IDR","TR":"TRY","ZA":"ZAR","AE":"AED","SA":"SAR","RU":"RUB",
}

PATTERNS = [
    ("Carrefour {cc}", "carrefour.{domain}", "supermercados", {"AR":"com.ar","BR":"com.br","ES":"es","FR":"fr","IT":"it","BE":"be","RO":"ro","PL":"pl"}),
    ("Lider {cc}", "lider.{domain}", "supermercados", {"CL":"cl"}),
    ("Santa Isabel {cc}", "santaisabel.{domain}", "supermercados", {"CL":"cl","PE":"pe"}),
    ("Cencosud {cc}", "cencosud.{domain}", "supermercados", {"AR":"com.ar","CL":"cl","PE":"pe","CO":"co","BR":"com.br","UY":"uy"}),
    ("Dia {cc}", "dia.{domain}", "supermercados", {"AR":"com.ar","BR":"com.br","ES":"es","PT":"pt"}),
    ("Walmart {cc}", "walmart.{domain}", "supermercados", {"MX":"com.mx","CL":"cl","AR":"com.ar","US":"com"}),
    ("Éxito {cc}", "exito.{domain}", "supermercados", {"CO":"com","UY":"uy","EC":"ec"}),
    ("Sodimac {cc}", "sodimac.{domain}", "hogar", {"CO":"com.co","CL":"cl","PE":"pe","AR":"com.ar","BR":"com.br","MX":"com.mx","UY":"com.uy"}),
    ("Easy {cc}", "easy.{domain}", "hogar", {"AR":"com.ar","CL":"cl","CO":"co","PE":"pe"}),
    ("Ripley {cc}", "ripley.{domain}", "departamentales", {"CL":"cl","PE":"pe","CO":"co","MX":"com.mx","AR":"com.ar"}),
    ("Falabella {cc}", "falabella.{domain}", "departamentales", {"CL":"cl","PE":"pe","CO":"co","AR":"com.ar","BR":"com.br","MX":"com.mx","UY":"com.uy"}),
    ("Samsung {cc}", "samsung.{domain}", "electro", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co","ES":"es","FR":"fr","IT":"it","GB":"uk","DE":"de","US":"us","PT":"pt"}),
    ("LG {cc}", "lg.{domain}", "electro", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","ES":"es","FR":"fr","IT":"it","DE":"de","US":"us","PT":"pt"}),
    ("Motorola {cc}", "motorola.{domain}", "electro", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","ES":"es","IT":"it","GB":"co.uk","DE":"de","US":"com"}),
    ("Electrolux {cc}", "electrolux.{domain}", "electro", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","ES":"es","IT":"it","FR":"fr","DE":"de","SE":"se","PT":"pt","NL":"nl"}),
    ("Whirlpool {cc}", "whirlpool.{domain}", "electro", {"BR":"com.br","MX":"com.mx","AR":"com.ar","ES":"es","IT":"it","FR":"fr","DE":"de","GB":"co.uk","US":"com","PT":"pt"}),
    ("C&A {cc}", "cea.{domain}", "moda", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co","ES":"es","FR":"fr","DE":"de","IT":"it","PT":"pt","NL":"nl"}),
    ("Hering {cc}", "hering.{domain}", "moda", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co"}),
    ("Zara {cc}", "zara.{domain}", "moda", {"ES":"es","FR":"fr","IT":"it","DE":"de","GB":"co.uk","PT":"pt","NL":"nl","CL":"cl","MX":"com.mx","AR":"com.ar","CO":"co","PE":"pe","BR":"com.br"}),
    ("Mango {cc}", "mango.{domain}", "moda", {"ES":"com","FR":"fr","IT":"it","DE":"de","GB":"co.uk","PT":"pt","NL":"nl"}),
    ("Decathlon {cc}", "decathlon.{domain}", "deportes", {"FR":"fr","ES":"es","IT":"it","DE":"de","GB":"co.uk","PT":"pt","NL":"nl","BE":"be","PL":"pl","BR":"com.br","CL":"cl","PE":"pe","CO":"com.co","AR":"com.ar","MX":"com.mx","SE":"se"}),
    ("Nike {cc}", "nike.{domain}", "deportes", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co","ES":"es","FR":"fr","IT":"it","DE":"de","GB":"com","PT":"pt","NL":"nl","SE":"se","PL":"pl"}),
    ("Adidas {cc}", "adidas.{domain}", "deportes", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co","ES":"es","FR":"fr","IT":"it","DE":"de","GB":"co.uk","PT":"pt","NL":"nl","PL":"pl","SE":"se"}),
    ("Puma {cc}", "puma.{domain}", "deportes", {"BR":"com.br","MX":"com.mx","AR":"com.ar","ES":"es","FR":"fr","IT":"it","DE":"de","GB":"co.uk","PT":"pt","NL":"nl"}),
    ("O Boticário {cc}", "oboticario.{domain}", "belleza", {"BR":"com.br","PT":"pt","AR":"com.ar","CL":"cl","PE":"pe","CO":"co","MX":"com.mx","BO":"com.bo","PY":"com.py","UY":"com.uy","ES":"es","FR":"fr","IT":"it","DE":"de","GB":"co.uk","US":"com"}),
    ("Natura {cc}", "natura.{domain}", "belleza", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","PE":"pe","CO":"co","BO":"com.bo","FR":"fr"}),
    ("Avon {cc}", "avon.{domain}", "belleza", {"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","ES":"es","FR":"fr","IT":"it","DE":"de","GB":"com","PT":"pt","PL":"pl"}),
    ("Leroy Merlin {cc}", "leroymerlin.{domain}", "hogar", {"BR":"com.br","ES":"es","FR":"fr","IT":"it","PT":"pt","PL":"pl","RO":"ro"}),
    ("Rosen {cc}", "rosen.{domain}", "hogar", {"CL":"cl","PE":"pe","CO":"co","MX":"com.mx","AR":"com.ar","EC":"com"}),
    ("Nestlé {cc}", "nestle.{domain}", "alimentos", {"BR":"com.br","MX":"com.mx","AR":"com.ar","ES":"es","FR":"fr","IT":"it","DE":"de","PT":"pt","CL":"cl","CO":"co","PE":"pe","GB":"co.uk"}),
    ("Unilever {cc}", "unilever.{domain}", "alimentos", {"BR":"com.br","MX":"com.mx","AR":"com.ar","ES":"es","FR":"fr","IT":"it","DE":"de","GB":"co.uk","PT":"pt","NL":"nl"}),
    ("Danone {cc}", "danone.{domain}", "alimentos", {"BR":"com.br","MX":"com.mx","AR":"com.ar","ES":"es","FR":"fr","IT":"it","DE":"de","PT":"pt"}),
    ("Leonisa {cc}", "leonisa.{domain}", "moda", {"CO":"com","PE":"pe","MX":"com.mx","ES":"es","US":"com"}),
    ("Totto {cc}", "totto.{domain}", "moda", {"CO":"com","PE":"pe","EC":"com","MX":"com.mx","CR":"co.cr","GT":"com.gt","PA":"com.pa","BO":"com.bo"}),
    ("Farmatodo {cc}", "farmatodo.{domain}", "farmacias", {"CO":"com.co","MX":"com.mx","VE":"com.ve","AR":"com.ar"}),
    ("Cruz Verde {cc}", "cruzverde.{domain}", "farmacias", {"CO":"com.co","CL":"cl","PE":"pe","MX":"com.mx"}),
    ("Office Depot {cc}", "officedepot.{domain}", "libreria", {"MX":"com.mx","ES":"es","FR":"fr","GB":"co.uk","US":"com","PE":"pe"}),
    ("H&M {cc}", "hm.{domain}", "moda", {"ES":"es","FR":"fr","IT":"it","DE":"de","GB":"com","PT":"pt","NL":"nl","CL":"cl","MX":"com.mx","AR":"com.ar","PE":"pe","CO":"co","BR":"com.br"}),
    ("Farmacias Guadalajara {cc}", "farmaciasguadalajara.{domain}", "farmacias", {"MX":"com.mx"}),
    ("Farmacias del Ahorro {cc}", "farmaciasdelahorro.{domain}", "farmacias", {"MX":"com.mx"}),
    ("Coppel {cc}", "coppel.{domain}", "departamentales", {"MX":"com","AR":"com.ar"}),
    ("Garbarino {cc}", "garbarino.{domain}", "electro", {"AR":"com.ar"}),
    ("MediaMarkt {cc}", "mediamarkt.{domain}", "electro", {"ES":"es","DE":"de","IT":"it","NL":"nl","PL":"pl","PT":"pt","AT":"at"}),
    ("AutoZone {cc}", "autozone.{domain}", "autopartes", {"MX":"com.mx","US":"com","BR":"com.br"}),
    ("Swift {cc}", "swift.{domain}", "alimentos", {"BR":"com.br","AR":"com.ar","UY":"com.uy"}),
    ("Petlove {cc}", "petlove.{domain}", "mascotas", {"BR":"com.br"}),
    ("Petz {cc}", "petz.{domain}", "mascotas", {"BR":"com.br"}),
    ("Cobasi {cc}", "cobasi.{domain}", "mascotas", {"BR":"com.br"}),
    ("Saraiva {cc}", "saraiva.{domain}", "libreria", {"BR":"com.br"}),
    ("Livraria Cultura {cc}", "livrariacultura.{domain}", "libreria", {"BR":"com.br"}),
    ("Centauro {cc}", "centauro.{domain}", "deportes", {"BR":"com.br"}),
    ("Casas Bahia {cc}", "casasbahia.{domain}", "electro", {"BR":"com.br"}),
    ("Ponto Frio {cc}", "pontofrio.{domain}", "electro", {"BR":"com.br"}),
    ("Marisa {cc}", "marisa.{domain}", "moda", {"BR":"com.br","AR":"com.ar"}),
    ("Riachuelo {cc}", "riachuelo.{domain}", "moda", {"BR":"com.br"}),
    ("Magazine Luiza {cc}", "magazineluiza.{domain}", "electro", {"BR":"com.br"}),
]

KEY_MAP = {
    " ":"_",".":"",",":"","'":"","’":"","(":"",")":"","&":"","+":"","!":"","?":"","/":"","\\":"","\u00e1":"a","\u00e9":"e","\u00ed":"i","\u00f3":"o","\u00fa":"u","\u00f1":"n","\u00e4":"a","\u00eb":"e","\u00ef":"i","\u00f6":"o","\u00fc":"u","\u00e0":"a","\u00e8":"e","\u00ec":"i","\u00f2":"o","\u00f9":"u","\u00e2":"a","\u00ea":"e","\u00ee":"i","\u00f4":"o","\u00fb":"u"
}

def make_key(name, cc):
    name_clean = "".join(KEY_MAP.get(c, c) for c in name.lower()).replace("__","_").strip("_")
    return f"{name_clean}_{cc.lower()}"

SCORE = "5,5,4,3,5"

def main():
    existing = set()
    if Path("stores_curated.csv").exists():
        with open("stores_curated.csv", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                existing.add(row["key"])

    new_rows = []
    for name_tpl, base_tpl, line, countries in PATTERNS:
        for cc, domain in countries.items():
            name = name_tpl.replace("{cc}", cc)
            key = make_key(name, cc)
            base = f"https://www.{base_tpl.replace('{domain}', domain)}"
            currency = CURRENCIES.get(cc, "USD")
            if key not in existing:
                new_rows.append(f"{key},{name},{base},{cc},{currency},{line},{SCORE}")
                existing.add(key)

    with open("stores_curated.csv", "a", newline="", encoding="utf-8") as f:
        for row in new_rows:
            f.write(row + "\n")

    print(f"Added {len(new_rows)} new retailers to CSV")

PATTERNS += [
    ("Sephora {cc}","sephora.{domain}","belleza",{"BR":"com.br","MX":"com.mx","ES":"es","FR":"fr","IT":"it","DE":"de","GB":"co.uk","PT":"pt"}),
    ("MAC {cc}","maccosmetics.{domain}","belleza",{"BR":"com.br","MX":"com.mx","AR":"com.ar","ES":"es","FR":"fr","IT":"it","DE":"de","GB":"co.uk","PT":"pt"}),
    ("IKEA {cc}","ikea.{domain}","hogar",{"ES":"es","FR":"fr","IT":"it","DE":"de","GB":"com","PT":"pt","NL":"nl","BE":"be","PL":"pl"}),
    ("Lidl {cc}","lidl.{domain}","supermercados",{"DE":"de","ES":"es","FR":"fr","IT":"it","GB":"co.uk","PT":"pt","NL":"nl","BE":"be","PL":"pl"}),
    ("Aldi {cc}","aldi.{domain}","supermercados",{"DE":"de","US":"us","GB":"co.uk","FR":"fr","ES":"es","IT":"it","NL":"nl"}),
    ("Tesco {cc}","tesco.{domain}","supermercados",{"GB":"com","IE":"ie","PL":"pl","CZ":"cz","SK":"sk","HU":"hu"}),
    ("Dafiti {cc}","dafiti.{domain}","moda",{"BR":"com.br","MX":"com.mx","AR":"com.ar","CL":"cl","CO":"co","PE":"pe"}),
    ("Mobly {cc}","mobly.{domain}","hogar",{"BR":"com.br"}),
    ("Netshoes {cc}","netshoes.{domain}","deportes",{"BR":"com.br"}),
    ("Converse {cc}","converse.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au","JP":"jp","KR":"kr"}),
    ("Vans {cc}","vans.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au","JP":"jp"}),
    ("Skechers {cc}","skechers.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au"}),
    ("Crocs {cc}","crocs.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au","JP":"jp","KR":"kr","CN":"cn","IN":"in"}),
    ("Fila {cc}","fila.{domain}","deportes",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au","JP":"jp","KR":"kr","CN":"cn","IN":"in","SG":"sg"}),
    ("Reebok {cc}","reebok.{domain}","deportes",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au","JP":"jp","KR":"kr","CN":"cn","IN":"in"}),
    ("Calvin Klein {cc}","calvinklein.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl"}),
    ("Tommy Hilfiger {cc}","tommy.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au"}),
    ("Lacoste {cc}","lacoste.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr"}),
    ("Columbia {cc}","columbia.{domain}","deportes",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au","JP":"jp","KR":"kr"}),
    ("The North Face {cc}","thenorthface.{domain}","deportes",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au","JP":"jp","KR":"kr","CN":"cn"}),
    ("Forever 21 {cc}","forever21.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","SE":"se","DK":"dk","FI":"fi","NO":"no","AT":"at","CH":"ch","IE":"ie","GR":"gr","CZ":"cz","RO":"ro","HU":"hu","ZA":"co.za","AU":"com.au","JP":"jp","KR":"kr","CN":"cn"}),
    ("Levis {cc}","levis.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","SE":"se","DK":"dk","FI":"fi","NO":"no","AT":"at","CH":"ch","IE":"ie","GR":"gr","CZ":"cz","RO":"ro","HU":"hu","TR":"com.tr","ZA":"co.za","AU":"com.au","JP":"jp","KR":"kr","CN":"cn","IN":"in","SG":"sg"}),
    ("Asics {cc}","asics.{domain}","deportes",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au","JP":"jp","KR":"kr","CN":"cn"}),
    ("Timberland {cc}","timberland.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr","AU":"com.au"}),
    ("Gap {cc}","gap.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","CL":"cl","AR":"com.ar","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","SE":"se","DK":"dk","FI":"fi","NO":"no","AT":"at","CH":"ch","IE":"ie","GR":"gr","CZ":"cz","RO":"ro","HU":"hu","TR":"com.tr","ZA":"co.za","AU":"com.au","JP":"jp","CN":"cn","SG":"sg"}),
    ("Guess {cc}","guess.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","TR":"com.tr"}),
    ("Diesel {cc}","diesel.{domain}","moda",{"US":"com","MX":"com.mx","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl"}),
    ("Pandora {cc}","pandora.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","AT":"at","AU":"com.au"}),
    ("Swatch {cc}","swatch.{domain}","moda",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","CH":"ch","AT":"at"}),
    ("Bose {cc}","bose.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","AU":"com.au"}),
    ("Sony {cc}","sony.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","SE":"se","DK":"dk","FI":"fi","NO":"no","AT":"at","CH":"ch","IE":"ie","GR":"gr","CZ":"cz","RO":"ro","HU":"hu","TR":"com.tr","ZA":"co.za","AU":"com.au","JP":"jp","KR":"kr","CN":"cn","IN":"in","SG":"sg"}),
    ("Philips {cc}","philips.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","AT":"at","AU":"com.au"}),
    ("Dell {cc}","dell.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","AT":"at","AU":"com.au","JP":"jp","CN":"cn","IN":"in"}),
    ("HP {cc}","hp.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","PL":"pl","AT":"at","AU":"com.au","JP":"jp","CN":"cn","IN":"in"}),
    ("Apple {cc}","apple.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"uk","DE":"de","IT":"it","PT":"pt","NL":"nl","AU":"au","JP":"jp","KR":"kr","CN":"cn","IN":"in","SG":"sg"}),
    ("Microsoft {cc}","microsoft.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","AU":"com.au","JP":"jp","KR":"kr","CN":"cn","IN":"in"}),
    ("Canon {cc}","canon.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","AU":"com.au","JP":"jp"}),
    ("Nikon {cc}","nikon.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","AU":"com.au","JP":"jp"}),
    ("JBL {cc}","jbl.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","AU":"com.au"}),
    ("GoPro {cc}","gopro.{domain}","electro",{"US":"com","MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","AU":"com.au"}),
    ("Huawei {cc}","huawei.{domain}","electro",{"MX":"com.mx","BR":"com.br","ES":"es","FR":"fr","GB":"co.uk","DE":"de","IT":"it","PT":"pt","NL":"nl","CL":"cl","AR":"com.ar","PE":"pe","CO":"co"}),
]
if __name__ == "__main__":
    main()
