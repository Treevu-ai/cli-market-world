path = r"C:\Users\acuba\cli-market-world\.deps\cli-market-core\market_core\market_stores.py"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Insert ferretec_pe after promart line (line 61, 0-indexed 60)
new_line = '    "ferretec_pe": {"name":"Ferretec","base":"https://ferretec.pe","country":"PE","currency":"PEN","emoji":"\U0001f1f5\U0001f1ea","line":"hogar","platform":"shopify"},\n'
lines.insert(61, new_line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Done. Line 61-63:")
for i in range(59, 64):
    print(f"  {i+1}: {lines[i].rstrip()}")
