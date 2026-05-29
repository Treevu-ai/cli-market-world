#!/usr/bin/env python3
"""Generate LinkedIn Day-08..Day-30 publish-ready drafts from calendar."""

from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs" / "linkedin"

DAYS = {
    8: {
        "title": "Arroz Lima — variación entre supermercados",
        "pillar": "data-stories",
        "lang": "es",
        "hooks": [
            "Data shock: el precio del arroz no es uno solo en Lima — varía fuerte entre cadenas esta semana.",
            "Mismo producto, distinto supermercado, distinto precio. Nuestro collector lo ve cada 8 horas.",
            "¿Tu agente sabe comparar arroz en PE? El nuestro sí — con APIs reales, no scraping.",
        ],
        "post": """El precio del arroz no es un solo número en Lima.

Esta semana nuestro collector indexó miles de precios reales de góndola en supermercados peruanos — actualizados cada 8 horas vía APIs VTEX, sin scraping.

Lo que vemos:

→ El mismo SKU puede variar significativamente entre cadenas
→ Las farmacias y supermercados no compiten solo en promo — compiten en datos
→ Un agente de IA puede comparar en menos de un segundo lo que a un humano le toma abrir 4 apps

Esto no es un índice oficial de inflación. Es señal de mercado en tiempo casi real — lo que un agente necesita para recomendar, comparar o comprar.

8,000+ precios indexados. 28 retailers activos hoy. 8 países.

Si construyes agentes que toman decisiones de compra, necesitan esta capa de infraestructura.

¿Qué producto te gustaría ver comparado en PE la próxima semana?""",
        "comment": "Dashboard + comparar en terminal 👇\n\nhttps://cli-market.dev\n\n```\npip install cli-market\nmarket compare \"arroz\" --country PE\n```\n\nDatos: [[metrics/price-pulse-2026-W22]]",
        "tags": "#AI #ecommerce #data #retail #Peru",
        "gate": True,
    },
    9: {
        "title": "Canasta básica PE — comparación multi-tienda",
        "pillar": "data-stories",
        "lang": "es",
        "hooks": [
            "Canasta básica: ¿cuánto cuesta realmente según el supermercado? Nuestro agente lo calcula.",
            "Arroz + leche + aceite. Tres productos. Precios distintos en cada cadena.",
            "La canasta no es abstracta — es JSON comparado en tiempo real.",
        ],
        "post": """¿Cuánto cuesta una canasta básica en Perú?

Depende del supermercado.

Con CLI Market un agente puede armar una canasta (arroz, leche, aceite, pan) y comparar el total entre Wong, Metro, Plaza Vea y más — en una sola llamada API.

No es estimación. Son precios de góndola de retailers reales.

→ Herramienta MCP: `market_basket`
→ 30 retailers verificados en 8 países
→ Refresh cada 8 horas

Los comparadores de precio para humanos existen hace años.

Los comparadores para agentes de IA casi no existen.

Estamos construyendo esa capa.

¿Qué productos incluirías en tu canasta de prueba?""",
        "comment": "Probar canasta 👇\n\nhttps://cli-market.dev\n\nVer [[linkedin/data-gate]] antes de publicar cifras exactas.",
        "tags": "#AI #ecommerce #Peru #data #MCP",
        "gate": True,
    },
    10: {
        "title": "Inflación — señal cada 8 horas",
        "pillar": "data-stories",
        "lang": "es",
        "hooks": [
            "¿Inflación real? Nuestro collector corre cada 8 horas. Esto es lo que vemos.",
            "No reemplazamos al INEI. Pero sí damos señal de mercado a agentes cada 8h.",
            "8,000+ precios frescos. Un snapshot cada 8 horas. Así se ve el retail desde IA.",
        ],
        "post": """¿Inflación real?

No somos el INEI ni el INDEC. No publicamos un índice oficial.

Pero sí tenemos algo que casi nadie tiene para agentes de IA: **8,000+ precios de góndola actualizados cada 8 horas** en 8 países.

Nuestro collector:

→ Corre automático en Railway + PostgreSQL
→ Cero intervención humana
→ APIs reales (VTEX + Magento), cero scraping
→ Snapshots históricos para ver variación

Herramienta MCP `market_inflation` devuelve delta de precios por país y línea.

Para un agente, eso es oro: señal de mercado accionable, no un PDF trimestral.

Para un retailer, es presión: ahora compites también en búsquedas de IA.

Stripe convirtió pagos en APIs.

Nosotros convertimos precios de góndola en APIs.

¿Qué país te interesa monitorear primero?""",
        "comment": "Stats en vivo 👇\n\nhttps://cli-market.dev\n\n```\nmarket stats\n```",
        "tags": "#AI #data #ecommerce #inflation #buildinpublic",
        "gate": False,
    },
    11: {
        "title": "Escala por retailer — electro y hogar",
        "pillar": "data-stories",
        "lang": "es",
        "hooks": [
            "Motorola, Electrolux, Whirlpool — miles de precios indexados por retailer.",
            "No es un catálogo estático. Es un moat de datos que crece cada 8 horas.",
            "Electro LATAM tiene spreads enormes. Los agentes pueden verlos. ¿Tú?",
        ],
        "post": """CLI Market no es solo supermercados.

También indexamos electro, hogar, moda y farmacias — 6 líneas de negocio, 30 retailers.

Esta semana en nuestro data moat:

→ Miles de precios en supermercados (AR, PE, BR)
→ Electro y tecnología con spreads altos entre países
→ Farmacias con markup significativo vs supermercados

Un agente puede preguntar "¿cuánto cuesta X en AR vs PE?" y obtener JSON en segundos.

Eso es infraestructura — no un chatbot que inventa precios.

Open source. MIT. `pip install cli-market`

¿En qué vertical retail te gustaría ver más cobertura?""",
        "comment": "Explorar líneas 👇\n\nhttps://cli-market.dev\n\n```\nmarket lines\n```",
        "tags": "#AI #retail #data #LATAM #MCP",
        "gate": True,
    },
    12: {
        "title": "Carousel — Top 10 búsquedas",
        "pillar": "data-stories",
        "lang": "es",
        "hooks": [
            "¿Qué compra un agente? Top búsquedas esta semana en CLI Market.",
            "Carousel: los 10 productos que más buscan los agentes conectados a nuestro MCP.",
            "Leche, arroz, aceite… ¿adivinas el #1?",
        ],
        "post": """¿Qué compra un agente de IA?

Esta semana analizamos las búsquedas más frecuentes en CLI Market:

**Carousel (8 slides):**
1. Hook: ¿Qué compra un agente?
2. #1 — Leche (PE, AR, BR)
3. #2 — Arroz
4. #3 — Aceite
5. #4 — Pañales / farmacia
6. #5 — Electro (celulares)
7. Insight: supermercados dominan, farmacias tienen mayor spread
8. CTA: `pip install cli-market`

Los agentes no compran como humanos — buscan, comparan, optimizan.

Si tu producto no aparece en APIs de retailers, no existe para ellos.

¿Qué buscarías tú con un agente conectado?""",
        "comment": "Conectar MCP 👇\n\nhttps://cli-market.dev/tools",
        "tags": "#AI #ecommerce #MCP #data #agents",
        "carousel": True,
        "gate": True,
    },
    13: {
        "title": "Retailers vs búsquedas IA",
        "pillar": "data-stories",
        "lang": "en",
        "hooks": [
            "Retailers don't just compete with retailers anymore. They compete in AI search results.",
            "When an agent compares prices, your store either shows up in JSON — or it doesn't exist.",
            "The next SEO is agent discoverability. Is your store in the API?",
        ],
        "post": """Retailers don't just compete with other retailers anymore.

They compete in AI search results.

When a user asks their agent "find the cheapest milk in Lima", your store either:

→ Appears in structured JSON from a commerce API
→ Or it doesn't exist for that agent

CLI Market gives 30 verified retailers a unified API surface for AI agents — search, compare, cart, checkout.

No scraping. No fragile HTML parsers. Real VTEX and Magento APIs.

If you're a retailer on VTEX or Magento: your products can already appear in agent searches.

List your store free: 30 seconds. No code.

The next SEO is agent discoverability.

Are you in the API?""",
        "comment": "List your store 👇\n\nhttps://cli-market.dev/retailers",
        "tags": "#AI #ecommerce #retail #VTEX #agents",
        "gate": False,
    },
    14: {
        "title": "3 insights de 8K+ precios",
        "pillar": "data-stories",
        "lang": "es",
        "hooks": [
            "3 cosas que aprendí indexando 8,000+ precios esta semana.",
            "Los precios cambian más rápido de lo que crees. Tres insights del collector.",
            "Farmacia vs supermercado: el spread más alto que vimos en el data moat.",
        ],
        "post": """3 cosas que aprendí indexando 8,000+ precios esta semana:

**1. Los precios cambian más rápido de lo que crees.**
Con refresh cada 8 horas ya vemos variación significativa en SKUs de alta rotación.

**2. Las farmacias tienen el spread más alto.**
Mismo principio activo, distinto precio — y los agentes lo detectan al instante.

**3. Casi nadie tiene este dato en formato agent-ready.**
PDFs, dashboards humanos, scraping frágil… pero no JSON unificado para MCP.

Por eso construimos CLI Market: infraestructura de comercio para agentes.

30 retailers. 36 herramientas MCP. 8 países. Open source.

¿Cuál insight te sorprende más?""",
        "comment": "Exportar datos (Pro) 👇\n\nhttps://cli-market.dev",
        "tags": "#AI #data #ecommerce #insights #buildinpublic",
        "gate": False,
    },
    15: {
        "title": "De 1 conector VTEX a 30 retailers",
        "pillar": "build-in-public",
        "lang": "es",
        "hooks": [
            "Arranqué CLI Market con un solo conector VTEX. Hoy son 30 retailers en 8 países.",
            "Build in public: de un script Python a infraestructura de comercio para agentes.",
            "El MVP era buscar leche en Wong. El producto es 36 herramientas MCP.",
        ],
        "post": """Arranqué CLI Market con un solo conector VTEX y una pregunta:

¿Puede un agente de IA comparar precios reales de supermercados en Perú?

Hoy:

→ 30 retailers verificados
→ 8 países (PE, AR, BR, MX, CO, CL, IT, FR)
→ 36 herramientas MCP
→ Collector automático cada 8 horas
→ Open source, MIT

El salto no fue "más código". Fue abstraer VTEX + Magento + auth + checkout detrás de una API.

Cada retailer que sumamos es un experimento: ¿responde la API? ¿Es estable? ¿Vale la pena?

Algunas tiendas fallaron. Las desactivamos. Las que funcionan, escalan.

Build in public no es solo marketing — es filtro de calidad.

¿Qué retailer te gustaría ver integrado?""",
        "comment": "GitHub 👇\n\nhttps://github.com/Treevu-ai/cli-market-world",
        "tags": "#buildinpublic #AI #startup #ecommerce #opensource",
    },
    16: {
        "title": "30 APIs sincronizadas",
        "pillar": "build-in-public",
        "lang": "es",
        "hooks": [
            "El mayor desafío no fue el código. Fue mantener 30 APIs externas sincronizadas.",
            "30 retailers = 30 formas distintas de fallar. Así lo manejamos.",
            "Async fan-out a 30 APIs: lo que nadie te cuenta del agent commerce.",
        ],
        "post": """El mayor desafío técnico de CLI Market no fue escribir Python.

Fue mantener **30 APIs externas sincronizadas**.

Cada retailer VTEX o Magento tiene:

→ Rate limits distintos
→ Schemas que cambian sin aviso
→ Tokens que expiran
→ Catálogos de 10K+ SKUs

Nuestra respuesta:

→ `httpx` + `asyncio` para fan-out paralelo
→ Health checks por tienda (dashboard en vivo)
→ Collector cada 8h con retry y alertas
→ Desactivar tiendas rotas — calidad > cantidad

Hoy: 31 en catálogo, 16 saludables, 51% success rate.

No es 100%. Pero es honesto — y mejora cada semana.

Los agentes merecen datos reales, no promesas.

¿Qué stack usarías para fan-out a N APIs?""",
        "comment": "Arquitectura 👇\n\nhttps://github.com/Treevu-ai/cli-market-world",
        "tags": "#python #asyncio #buildinpublic #ecommerce #AI",
    },
    17: {
        "title": "Python httpx asyncio",
        "pillar": "build-in-public",
        "lang": "es",
        "hooks": [
            "¿Por qué Python + httpx + asyncio + FastAPI? Porque fan-out a 30 APIs lo exige.",
            "Un search en CLI Market dispara N requests paralelos. Así lo construimos.",
            "FastAPI + asyncio: la stack que eligió un commerce API para agentes.",
        ],
        "post": """¿Por qué Python para infraestructura de comercio para agentes?

Porque **`httpx` + `asyncio` + `FastAPI`** es imbatible para fan-out:

```python
# Simplificado: buscar en N retailers en paralelo
async with httpx.AsyncClient() as client:
    tasks = [search_store(client, store, query) for store in stores]
    results = await asyncio.gather(*tasks, return_exceptions=True)
```

Un `market search "leche"` dispara requests paralelos a Wong, Metro, Cencosud, Carrefour…

El agente recibe JSON unificado en <2 segundos.

Alternativas que evaluamos:

→ Node: bueno, pero ecosystem PyPI para CLI
→ Go: rápido, pero DX para data scientists peor
→ Sync requests: muerte a los 30 retailers

Python ganó por DX + async + ecosistema IA.

¿Tu agent stack es Python-first también?""",
        "comment": "Quickstart 👇\n\nhttps://cli-market.dev\n\n```\npip install cli-market\n```",
        "tags": "#python #FastAPI #asyncio #AI #developers",
    },
    18: {
        "title": "36 MCP tools MIT",
        "pillar": "build-in-public",
        "lang": "es",
        "hooks": [
            "36 herramientas MCP. Todas documentadas. Open source. MIT.",
            "No es un wrapper de scraping. Son 36 primitivas de comercio para agentes.",
            "El catálogo MCP más completo para e-commerce que conozco — y es open source.",
        ],
        "post": """36 herramientas MCP.

Todas documentadas.

Open source.

MIT.

Desde `market_search` hasta `market_inflation`, `market_ticket` (OCR de tickets), `market_voice` (audio → texto), `market_export` (data moat).

Por qué 36 y no 1 tool genérica "shop"?

Porque los LLM eligen mejor con primitivas específicas:

→ Buscar ≠ comparar ≠ canasta ≠ checkout
→ Cada tool tiene schema claro y errores accionables
→ Menos alucinación, más transacciones reales

Copia la config en Cursor/Claude: **cli-market.dev/tools**

`pip install cli-market`

¿Qué tool te falta para tu agente?""",
        "comment": "Configs MCP 👇\n\nhttps://cli-market.dev/tools",
        "tags": "#MCP #opensource #AI #ecommerce #agents",
    },
    19: {
        "title": "Collector PostgreSQL Railway",
        "pillar": "build-in-public",
        "lang": "es",
        "hooks": [
            "El collector corre cada 8 horas. PostgreSQL. Railway. Cero intervención humana.",
            "Build in public: cómo automatizamos 8,000+ precios sin tocar un botón.",
            "Cron + asyncio + Postgres = data moat que crece solo.",
        ],
        "post": """El collector de CLI Market corre cada 8 horas.

PostgreSQL en Railway.

Cero intervención humana.

Pipeline:

1. GitHub Actions trigger (monday-ops)
2. Fan-out async a 31 retailers
3. Snapshots → Postgres
4. Dashboard + Price Pulse markdown export
5. Alertas si success rate cae

Resultado: **8,000+ precios frescos** listos para agentes vía MCP.

No es un side project manual. Es infraestructura.

El moat no es el código — es la **frecuencia y confiabilidad** del dato.

¿Automatizas data pipelines en tu producto?""",
        "comment": "Dashboard 👇\n\nhttps://cli-market-production.up.railway.app/dashboard",
        "tags": "#buildinpublic #data #postgresql #railway #AI",
    },
    20: {
        "title": "Roadmap self-serve PayPal",
        "pillar": "build-in-public",
        "lang": "es",
        "hooks": [
            "¿Qué sigue? Self-serve retailers. Pro live. Reportes semanales de precios.",
            "Roadmap público: de Alpha a GA en 15 días.",
            "Jun 1 Alpha · Jun 8 Beta · Jun 15 GA — esto viene.",
        ],
        "post": """¿Qué sigue en CLI Market?

**Ya shipped (Alpha):**
→ Billing Pro manual (email + PayPal)
→ Form self-serve en /retailers
→ 36 MCP tools + landing /tools
→ Collector + Price Pulse semanal

**Jun 8 Beta:**
→ HN launch + waitlist
→ 10 retailers self-serve
→ SEO agent-first live

**Jun 15 GA:**
→ Outbound escalado VTEX/Magento
→ Reportes Price Pulse PDF (Pro)
→ Path a $500 MRR

Transparencia total: collector hoy al 52% health — trabajando en llegar a 80%+.

Build in public = mostrar los números reales, no solo los buenos.

¿Qué feature priorizarías?""",
        "comment": "Roadmap + PRD 👇\n\nhttps://cli-market.dev/retailers",
        "tags": "#buildinpublic #roadmap #startup #AI #ecommerce",
    },
    21: {
        "title": "Error APIs VTEX inestables",
        "pillar": "build-in-public",
        "lang": "es",
        "hooks": [
            "Mi error más grande: asumir que las APIs VTEX eran estables. Spoiler: no lo son.",
            "10 retailers desactivados. Lección aprendida en build in public.",
            "La integración feliz en demo ≠ producción con 30 APIs.",
        ],
        "post": """Mi error más grande construyendo CLI Market:

Asumir que las APIs VTEX eran estables.

Spoiler: **no lo son**.

→ Tokens que expiran sin aviso
→ Endpoints que devuelven HTML en vez de JSON
→ Rate limits opacos
→ Catálogos que cambian de schema

Resultado: desactivamos 10 tiendas del catálogo. Mejor 31 que funcionan parcialmente que 41 en paper.

Dashboard en vivo muestra health por store — sin maquillaje.

Lección: **agent commerce necesita observabilidad por retailer**, no un boolean "integrado".

¿Has tenido APIs de terceros que rompen producción un domingo?""",
        "comment": "Store health 👇\n\nhttps://cli-market-production.up.railway.app/dashboard",
        "tags": "#buildinpublic #VTEX #ecommerce #failures #AI",
    },
    22: {
        "title": "Case study retailer PE",
        "pillar": "social-proof",
        "lang": "es",
        "hooks": [
            "Un retailer peruano listó su tienda en CLI Market. 30 segundos. Sin código.",
            "Case study: de invisible para agentes → discoverable en búsquedas IA.",
            "¿Tu tienda VTEX aparece cuando un agente busca 'leche'?",
        ],
        "post": """Este retailer peruano listó su tienda en CLI Market.

30 segundos.

Sin código.

Formulario en cli-market.dev/retailers → validación automática → productos en búsquedas de agentes.

Antes: invisible para cualquier agente de IA.

Después: aparece en JSON cuando alguien pregunta "¿cuánto cuesta X en PE?"

Gratis para retailers en Beta.

VTEX, Magento, Shopify — si tienes API, podemos conectarte.

Los agentes ya están comprando (o intentando).

La pregunta es si te encuentran.

¿Tienes tienda online en LATAM?""",
        "comment": "Listar tienda 👇\n\nhttps://cli-market.dev/retailers",
        "tags": "#retail #VTEX #Peru #AI #ecommerce",
    },
    23: {
        "title": "VTEX Magento listado",
        "pillar": "social-proof",
        "lang": "es",
        "hooks": [
            "Si su tienda usa VTEX o Magento, sus productos ya pueden aparecer en búsquedas de IA.",
            "CTA directo: registre su tienda. Gratis. 30 segundos.",
            "VTEX partners: sus agentes buscan productos. ¿Están los suyos?",
        ],
        "post": """Si su tienda usa **VTEX** o **Magento**:

Tus productos **ya pueden** aparecer en búsquedas de agentes de IA.

CLI Market unifica APIs de retail en una capa agent-ready:

→ Search, compare, cart, checkout
→ 36 herramientas MCP
→ 8 países LATAM + EU

**Registrar su tienda:**
1. cli-market.dev/retailers
2. Completa el form (30 seg)
3. Validación automática
4. Apareces en agent searches

Gratis en Beta.

No es marketplace. Es infraestructura.

Los agentes no visitan su sitio web: llaman APIs.

¿Estás en la API?""",
        "comment": "Formulario 👇\n\nhttps://cli-market.dev/retailers?utm_source=linkedin&utm_campaign=30d-d23",
        "tags": "#VTEX #Magento #retail #AI #LATAM",
    },
    24: {
        "title": "3 razones listar tienda",
        "pillar": "social-proof",
        "lang": "es",
        "hooks": [
            "3 razones para registrar su tienda en CLI Market hoy.",
            "Gratis. 30 segundos. Agentes IA ya buscan productos.",
            "List post para retailers: por qué aparecer en agent commerce.",
        ],
        "post": """3 razones para registrar su tienda en CLI Market:

**1. Gratis** (Beta)
Sin costo de integración. Sin revenue share en Beta.

**2. 30 segundos**
Formulario self-serve. Sin código. Sin llamada de ventas.

**3. Agentes IA ya buscan**
Cuando un usuario pide a su agente "compara precios de leche", su tienda aparece — o no.

VTEX. Magento. Retail LATAM.

cli-market.dev/retailers

El e-commerce no es solo mobile-first.

Es **agent-first**.

¿Registramos su tienda esta semana?""",
        "comment": "Empezar 👇\n\nhttps://cli-market.dev/retailers",
        "tags": "#retail #AI #ecommerce #VTEX #startup",
    },
    25: {
        "title": "pip install CTA",
        "pillar": "social-proof",
        "lang": "es",
        "hooks": [
            "Pruebe CLI Market ahora: pip install + market search en 60 segundos.",
            "Copy-paste challenge: ¿funciona en tu terminal?",
            "El CTA más simple del mundo developer-first.",
        ],
        "post": """Pruebe CLI Market ahora.

Copy-paste en tu terminal:

```
pip install cli-market
market search "leche" --country PE
```

60 segundos.

Precios reales de retailers peruanos.

JSON listo para tu agente.

Conectar MCP en Cursor: **cli-market.dev/tools**

Open source. MIT. Gratis.

Si eres developer: pruébalo y dime qué falta.

Si eres retailer: cli-market.dev/retailers

El futuro del comercio es agent-first.

¿Lo corres en tu máquina?""",
        "comment": "Tools + GitHub 👇\n\nhttps://cli-market.dev/tools\n\nhttps://github.com/Treevu-ai/cli-market-world",
        "tags": "#opensource #python #MCP #AI #developers",
    },
    26: {
        "title": "Agent-first vision EN",
        "pillar": "social-proof",
        "lang": "en",
        "hooks": [
            "The future of e-commerce isn't mobile-first. It's agent-first.",
            "PC → Mobile → Agent. The platform shift is here.",
            "Commerce infrastructure for the agent economy — not another chatbot.",
        ],
        "post": """The future of e-commerce isn't mobile-first.

It's **agent-first**.

Platform shifts:

PC → Mobile (2007)
Mobile → Agent (2025+)

What agents need:
→ Structured product data (not HTML)
→ Unified APIs (not 30 integrations)
→ Real prices (not hallucinations)
→ Checkout primitives (not "I can't purchase")

Stripe turned payments into APIs.

CLI Market turns commerce into APIs.

30 retailers. 8 countries. 36 MCP tools. Open source.

`pip install cli-market`

Who's building agent-first commerce in your market?""",
        "comment": "Get started 👇\n\nhttps://cli-market.dev",
        "tags": "#AI #ecommerce #agents #future #startup",
    },
    27: {
        "title": "1000 agentes tiempo real",
        "pillar": "social-proof",
        "lang": "es",
        "hooks": [
            "¿Qué pasa cuando 1,000 agentes comparan precios en tiempo real?",
            "Eso estamos construyendo — infraestructura, no demo.",
            "Agent commerce a escala: el problema de N requests paralelos.",
        ],
        "post": """¿Qué pasa cuando 1,000 agentes comparan precios en tiempo real?

Eso estamos construyendo.

No es demo de ChatGPT comprando regalos.

Es infraestructura:

→ API con fan-out async a 30 retailers
→ Rate limits por tier (Free / Pro)
→ Data moat con refresh 8h
→ MCP para Cursor, Claude, Windsurf

Cada agente que conecta es un nodo en la red.

Cada retailer que lista es inventario discoverable.

El flywheel: más agentes → más valor data → más retailers → más agentes.

Estamos en día 30 del launch público.

El hard part empieza ahora: escala + confiabilidad.

¿Qué construirías encima de esta API?""",
        "comment": "API docs 👇\n\nhttps://cli-market-production.up.railway.app/docs",
        "tags": "#AI #infrastructure #ecommerce #scale #agents",
    },
    28: {
        "title": "Recap métricas 30 días",
        "pillar": "social-proof",
        "lang": "es",
        "hooks": [
            "30 días. 30 retailers. 8 países. 36 MCP tools. Recap.",
            "Milestone: lo que construimos en un mes de build in public.",
            "Números reales — no vanity metrics.",
        ],
        "post": """30 días de CLI Market en público.

Recap honesto:

→ **30 retailers** verificados (31 catálogo, 16 healthy hoy)
→ **8 países** — PE, AR, BR, MX, CO, CL, IT, FR
→ **36 herramientas MCP**
→ **8,000+ precios** indexados (refresh 8h)
→ **Billing Pro** live (manual + PayPal)
→ **Self-serve** retailers en /retailers
→ **Open source** MIT

No llegamos a 41/41 stores al 100%.

Sí llegamos a infraestructura real que agentes pueden usar hoy.

Próximo: Beta Jun 8, HN, 10 retailers self-serve, path $500 MRR.

Gracias a quienes probaron, comentaron, listaron tiendas.

¿Qué metric te importa más para el mes 2?""",
        "comment": "Dashboard 👇\n\nhttps://cli-market.dev",
        "tags": "#buildinpublic #milestone #AI #ecommerce #startup",
    },
    29: {
        "title": "Gracias retailers",
        "pillar": "social-proof",
        "lang": "es",
        "hooks": [
            "Gracias a los retailers que confiaron. A los que faltan: la puerta está abierta.",
            "30 tiendas en el catálogo. Gratitud + invitación.",
            "Sin retailers reales no hay agent commerce — gracias.",
        ],
        "post": """Gracias a los retailers que confiaron en CLI Market.

Sin APIs reales de Wong, Metro, Cencosud, Carrefour, farmacias, electro…

…no hay agent commerce. Solo alucinaciones.

A los que faltan:

→ La puerta está abierta
→ cli-market.dev/retailers
→ Gratis en Beta
→ 30 segundos

VTEX. Magento. LATAM + EU.

Los agentes no esperan.

Registre su tienda.""",
        "comment": "Formulario 👇\n\nhttps://cli-market.dev/retailers",
        "tags": "#retail #gratitude #AI #ecommerce #LATAM",
    },
    30: {
        "title": "Milestone 30 días",
        "pillar": "social-proof",
        "lang": "es",
        "hooks": [
            "30 días. Esto es lo que construí. Esto es lo que viene.",
            "Cierre del calendario 30d — founder POV.",
            "De idea a infraestructura de comercio para agentes en un mes.",
        ],
        "post": """30 días.

Esto es lo que construí:

Infraestructura de comercio para agentes de IA.

`pip install cli-market`

Esto es lo que viene:

→ Beta pública (HN, Reddit, DEV)
→ 10 retailers self-serve por semana
→ Price Pulse reports para Pro
→ Collector al 80%+ health
→ Agent-first SEO en Claude/ChatGPT

Stripe convirtió pagos en APIs.

Estamos convirtiendo comercio en APIs.

Si llegaste hasta aquí en el calendario — gracias.

Si eres developer: prueba el CLI.

Si es retailer: registre su tienda.

Nos vemos en el mes 2.""",
        "comment": "Todo en un link 👇\n\nhttps://cli-market.dev?utm_source=linkedin&utm_campaign=30d-fin\n\n```\npip install cli-market\nmarket hello\n```",
        "tags": "#AI #ecommerce #MCP #buildinpublic #milestone",
    },
}


def render(day: int, spec: dict) -> str:
    status = "ready" if not spec.get("gate") else "ready"
    gate_note = ""
    if spec.get("gate"):
        gate_note = "\n> ⚠️ Verificar datos en [[linkedin/data-gate]] antes de publicar.\n"
    carousel = ""
    if spec.get("carousel"):
        carousel = "\n## Carousel (8 slides)\n\nVer cuerpo del post — slides numerados.\n"
    return f"""---
title: Day {day:02d}
status: {status}
day: {day}
pillar: {spec["pillar"]}
lang: {spec["lang"]}
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day {day:02d} — {spec["title"]}

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]
{gate_note}
## Hooks (elegir 1)

1. **Hook 1:** {spec["hooks"][0]}
2. **Hook 2:** {spec["hooks"][1]}
3. **Hook 3:** {spec["hooks"][2]}

## Post (copiar a LinkedIn — sin link en cuerpo)

{spec["post"]}

## Primer comentario

{spec["comment"]}

## Hashtags

{spec["tags"]}
{carousel}
## Assets

- [ ] GIF terminal / screenshot (si aplica)
- [ ] Carousel Canva (días 5, 12)

## Checklist

- [ ] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] Datos verificados ([[linkedin/data-gate]] / [[metrics/price-pulse-YYYY-WW]]) si aplica
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
"""


def main() -> None:
    for day, spec in DAYS.items():
        path = DOCS / f"Day-{day:02d}.md"
        path.write_text(render(day, spec), encoding="utf-8")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
