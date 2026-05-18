#!/usr/bin/env python3
"""gen_stores.py — Generates STORES dict from curated CSV with scoring."""

import csv, sys
from pathlib import Path

SCORE_WEIGHTS = {"comparability":0.35,"frequency":0.25,"catalog_vol":0.15,"geo_coverage":0.15,"relevance":0.10}
PRIORITY_THRESHOLD = 3.0
INCLUSION_THRESHOLD = 2.0

COUNTRY_EMOJIS = {"PE":"🇵🇪","AR":"🇦🇷","BR":"🇧🇷","MX":"🇲🇽","CO":"🇨🇴","CL":"🇨🇱","ES":"🇪🇸","FR":"🇫🇷","IT":"🇮🇹","GB":"🇬🇧","US":"🇺🇸","PT":"🇵🇹","UY":"🇺🇾","EC":"🇪🇨","CR":"🇨🇷","PA":"🇵🇦","DO":"🇩🇴","RO":"🇷🇴","BE":"🇧🇪","DE":"🇩🇪"}

LINE_EMOJIS = {"supermercados":"🛒","farmacias":"💊","electro":"📱","moda":"👕","deportes":"⚽","hogar":"🏠","belleza":"💄","mascotas":"🐾","libreria":"📚","departamentales":"🏬","alimentos":"🍔","autopartes":"🔧","juguetes":"🧸","bebes":"🍼"}

def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows

def compute_score(row):
    s = 0.0
    for dim, w in SCORE_WEIGHTS.items():
        s += float(row.get(dim,1)) * w
    return round(s,2)

def generate_stores(rows):
    scored = []
    for r in rows:
        r["_score"] = compute_score(r)
        scored.append(r)
    scored.sort(key=lambda r: r["_score"], reverse=True)
    included = [r for r in scored if r["_score"] >= INCLUSION_THRESHOLD]

    lines_order = list(dict.fromkeys(r["line"] for r in included))
    server_lines = []
    cli_lines = []
    for line in lines_order:
        line_stores = [r for r in included if r["line"] == line]
        server_lines.append(f"\n    # ── {line.upper()} ──")
        cli_lines.append(f"\n    # ── {line.upper()} ──")
        for r in line_stores:
            flag = COUNTRY_EMOJIS.get(r["country"], "🌐")
            server_lines.append(f'    "{r["key"]}": {{"name":"{r["name"]}","base":"{r["base_url"]}","country":"{r["country"]}","currency":"{r["currency"]}","emoji":"{flag}","line":"{r["line"]}"}},')
            cli_lines.append(f'    "{r["key"]}": {{"name":"{r["name"]}","country":"{r["country"]}","currency":"{r["currency"]}","emoji":"{flag}","line":"{r["line"]}"}},')

    server_dict = "STORES = {\n" + "\n".join(server_lines) + "\n}\n"
    cli_dict = "STORES = {\n" + "\n".join(cli_lines) + "\n}\n"
    return server_dict, cli_dict, scored

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "stores_curated.csv"
    rows = load_csv(csv_path)
    server_dict, cli_dict, scored = generate_stores(rows)
    priority = [r for r in scored if r["_score"] >= PRIORITY_THRESHOLD]
    included = [r for r in scored if r["_score"] >= INCLUSION_THRESHOLD]

    lines = {}; countries = {}
    for r in included:
        lines[r["line"]] = lines.get(r["line"],0)+1
        countries[r["country"]] = countries.get(r["country"],0)+1

    print(f"CSV loaded: {len(rows)}")
    print(f"Priority (score>={PRIORITY_THRESHOLD}): {len(priority)}")
    print(f"Included (score>={INCLUSION_THRESHOLD}): {len(included)}")
    print(f"Lines: {len(lines)}  Countries: {len(countries)}")

    Path("market_stores.py").write_text(f"# Auto-generated — {len(included)} retailers\n{server_dict}\n")
    Path("market_stores_cli.py").write_text(f"# Auto-generated — {len(included)} retailers\n{cli_dict}\n")
    print("Wrote market_stores.py + market_stores_cli.py")

if __name__ == "__main__":
    main()
