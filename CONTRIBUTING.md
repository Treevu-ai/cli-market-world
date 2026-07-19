# Contributing to CLI Market

Thanks for your interest in contributing to CLI Market — 82 retailers indexed, 37 verified active, 9 countries, open source.

## How to contribute

### Add a new retailer

Add a pattern to `expand_stores.py`:

```python
# In expand_stores.py, add a tuple to PATTERNS:
("Brand Name {cc}", "brand.{domain}", "linea", {"US":"com","MX":"com.mx","ES":"es"})
```

Then run:
```bash
python3 expand_stores.py
python3 gen_stores.py stores_curated.csv
```

### Add a feature

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run `python3 -c "import py_compile; py_compile.compile('market_server.py', doraise=True)"`
5. Submit a PR

### Report a bug

Open an issue with:
- OS and Python version
- Steps to reproduce
- Expected vs actual behavior

## Development setup

```bash
# Repos are private under Treevu-ai — request access from the maintainer.
git clone git@github.com:Treevu-ai/cli-market-world.git
cd cli-market-world
pip install -r requirements.txt
python3 market_server.py
```

## Project structure

```
market_server.py     → FastAPI backend (port 8765)
market_cli.py        → Rich CLI for humans
market_mcp.py        → MCP server for AI agents
market_stores.py     → Auto-generated store data (3,600+ entries)
gen_stores.py        → Regenerate market_stores.py from CSV
expand_stores.py     → Add retailers via pattern expansion
stores_curated.csv   → Curated retailer database
landing/             → Next.js landing page (cli-market.dev)
```

## License

MIT. All contributions are under the same license.
