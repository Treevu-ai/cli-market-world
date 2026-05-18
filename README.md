<p align="center">
  <img src="https://img.shields.io/badge/retailers-100-brightgreen" alt="100 retailers">
  <img src="https://img.shields.io/badge/lines-12-blue" alt="12 lines">
  <img src="https://img.shields.io/badge/countries-12-orange" alt="12 countries">
  <img src="https://img.shields.io/badge/MCP%20tools-12-00d75f" alt="MCP">
  <img src="https://img.shields.io/badge/python-3.10+-306998" alt="py">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT">
</p>

<p align="center">
  <img src="https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&h=300&fit=crop&crop=edges&fm=jpg&q=80" width="100%" alt="code" />
</p>

> Infrastructure layer that transforms VTEX retailers into AI-agent compatible commerce systems. One connector. 100 retailers. 12 countries.

---

## English

### What

CLI Market is the middleware between VTEX and AI agents. 100 retailers in 12 countries. CLI for humans. MCP tools for agents. JSON for LLMs.

```bash
pip install git+https://github.com/Treevu-ai/cli-market-latam.git
market-server & market login
market search "leche" --country PE
market compare "aceite"
market add 3 --qty 2
market checkout --payment yape
```

### Coverage

100 retailers · 12 lines · 12 countries

| Line | N | Key retailers |
|------|---|--------------|
| 🛒 Supermarkets | 27 | Wong, Metro, Plaza Vea, Carrefour, Jumbo, Coto, Dia, Pao de Acucar, Chedraui, HEB, Exito, Lider, Soriana, Carulla |
| 💊 Pharmacy | 6 | Droga Raia, Drogasil, Pacheco, Farmatodo, Inkafarma |
| 📱 Electronics | 14 | Magazine Luiza, Samsung, LG, Motorola, Electrolux, Whirlpool, Alkosto, Fravega, Casas Bahia |
| ⚽ Sports | 15 | Centauro, Nike, Adidas, Decathlon (10 countries), Marti |
| 👕 Fashion | 8 | Renner, C&A, Marisa, Riachuelo, Arturo Calle, Leonisa |
| 🏠 Home | 7 | Homecenter, Sodimac, Easy, Leroy Merlin, Promart |
| 💄 Beauty | 6 | O Boticario, Natura (4 countries), Avon |
| 🏬 Department | 7 | Liverpool, Palacio de Hierro, Sears, Sanborns, Oechsle, Paris, La Polar |
| 🐾 Pets | 3 | Petlove, Petz, Cobasi |
| 📚 Books | 3 | Saraiva, Office Depot, Tai Loy |
| 🍔 Food | 3 | Nestle, Unilever, Swift |
| 🔧 Auto | 1 | AutoZone |

PE(11) · AR(12) · BR(37) · MX(18) · CO(14) · CL(9) · ES(3) · FR(3) · IT(3) · GB(2) · PT(1) · UY(1)

### Commands

`market login` `lines` `search` `compare` `add` `cart` `cart-update` `cart-remove` `cart-clear` `checkout` `orders` `reorder` `ask` `--json`

### MCP Server

12 tools. Compatible with DeepSeek TUI, Claude, Cursor. `python market_mcp.py`

### API v1

```bash
GET /v1/feed/prices?query=cafe&country=PE&format=csv
GET /v1/feed/stats?period=7d
GET /v1/pricing
```

---

## Español

### Qué es

CLI Market es el middleware entre VTEX y los agentes de IA. 100 retailers en 12 países. CLI para humanos. Herramientas MCP para agentes. JSON para LLMs.

```bash
pip install git+https://github.com/Treevu-ai/cli-market-latam.git
market-server & market login
market search "leche" --country PE
market add 3 --qty 2
market checkout --payment yape
```

### Cobertura

100 retailers · 12 líneas · 12 países

| Línea | N | Retailers clave |
|-------|---|----------------|
| 🛒 Supermercados | 27 | Wong, Metro, Plaza Vea, Carrefour, Jumbo, Coto, Dia, Pao de Acucar, Chedraui, HEB, Exito, Lider, Soriana |
| 💊 Farmacias | 6 | Droga Raia, Drogasil, Pacheco, Farmatodo, Inkafarma |
| 📱 Electro | 14 | Magazine Luiza, Samsung, LG, Motorola, Electrolux, Alkosto, Fravega, Casas Bahia |
| ⚽ Deportes | 15 | Centauro, Nike, Adidas, Decathlon (10 países), Marti |
| 👕 Moda | 8 | Renner, C&A, Marisa, Riachuelo, Arturo Calle, Leonisa |
| 🏠 Hogar | 7 | Homecenter, Sodimac, Easy, Leroy Merlin, Promart |
| 💄 Belleza | 6 | O Boticario, Natura (4 países), Avon |
| 🏬 Departamentales | 7 | Liverpool, Palacio, Sears, Sanborns, Oechsle, Paris, La Polar |
| 🐾 Mascotas | 3 | Petlove, Petz, Cobasi |
| 📚 Librería | 3 | Saraiva, Office Depot, Tai Loy |
| 🍔 Alimentos | 3 | Nestle, Unilever, Swift |
| 🔧 Autopartes | 1 | AutoZone |

### Comandos

`market login` `lines` `search` `compare` `add` `cart` `cart-update` `cart-remove` `cart-clear` `checkout` `orders` `reorder` `ask` `--json`

### Servidor MCP

12 herramientas. Compatible con DeepSeek TUI, Claude, Cursor. `python market_mcp.py`

---

🌎 [cli-market.dev](https://cli-market.dev) · 💻 [GitHub](https://github.com/Treevu-ai/cli-market-latam) · 📡 [API](https://cli-market-api-production.up.railway.app)
