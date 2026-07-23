# CLI Market — Brief Institucional

*Actualizado: 17 de julio de 2026 · Cifras de plataforma verificadas en vivo*

---

## Qué es

CLI Market es una plataforma de inteligencia de mercado retail para América
Latina. Monitorea en tiempo real precio, catálogo y competencia de
productos en supermercados y otros canales retail de la región, y pone
esa información a disposición mediante API, línea de comandos (CLI) y un
protocolo de acceso para agentes de inteligencia artificial (MCP).

No es un estudio de mercado puntual que se entrega una vez y queda
desactualizado: es una capa de datos viva, consultable en cualquier
momento, sobre la cual se puede tomar una decisión hoy y volver a
consultar mañana si el mercado cambió.

---

## Cómo funciona

| Método | Qué permite | Acceso |
|--------|-------------|--------|
| **API** | Integración directa a sistemas propios | `https://cli-market-api.fly.dev` |
| **CLI** | Consultas desde terminal (`market search`, `market compare`) | `pip install cli-market-world` |
| **MCP** | Consulta y compra por agentes de IA (Claude, Cursor, otros asistentes) | Servidor `market-mcp` |

Los datos se actualizan cada 4 horas. Toda cifra citada en un reporte o
propuesta puede volver a verificarse en vivo el mismo día de una reunión.

---

## Cobertura actual — cifras de plataforma (en vivo, hoy)

| Indicador | Valor |
|-----------|-------|
| Precios registrados | 75,379 |
| Productos únicos indexados | 69,502 |
| Tiendas activas | 40 |
| Países con al menos un retailer indexado | 9 |

**Cobertura geográfica por fuerza de datos:**

| Nivel | Mercados |
|-------|----------|
| Sólida | Perú, México, Argentina |
| Útil según categoría | Colombia, Brasil |
| Parcial / específica por SKU | Chile, España (varía mucho según producto — ver nota) |
| Sin cobertura de retail de alimentos hoy | Estados Unidos, Asia |

> **Nota de honestidad operativa:** la cobertura no es uniforme por país —
> varía por cadena y SKU específico. Por ejemplo, alcachofa tiene
> presencia verificada en España mientras que palta o arándano no la
> tienen ahí todavía. Cada categoría se valida en vivo antes de asignarla
> a un caso de uso concreto — nunca se proyecta cobertura sin verificarla.

---

## Por qué importa para cadenas productivas y MYPE exportadoras

Validamos en vivo la cobertura de las cadenas productivas peruanas más
representativas, con este resultado:

| Cadena | Cobertura | Detalle |
|--------|-----------|---------|
| Quinua | Alta | 57 SKUs, marcas peruanas de valor agregado real |
| Cacao | Alta | 111 SKUs, presencia en España y México |
| Palta Hass | Alta | Perú y Argentina |
| Arándano | Alta | Perú, México y Argentina |
| Alcachofa | Alta | Perú y España |
| Uva | Alta | Perú (fresco) y Brasil (volumen amplio) |
| Mango | Alta | Perú (fresco), procesados en España y México |
| Café | Intermedia | Requiere filtrar oferta peruana real vs. marcas internacionales |
| Espárrago | En desarrollo | Brecha notable — producto insignia de exportación |
| Pisco | En desarrollo | Solo mercado doméstico; sin rastro en destinos de exportación |

Esta capa de datos permite pasar de una decisión de producción basada en
intuición a una decisión calibrada contra el precio y la competencia real
del mercado de destino — antes de comprometer inversión.

---

## Lo que CLI Market no hace — límites claros

- **No entrega precio FOB ni precio al importador.** El dato es precio de
  góndola al consumidor final; el ejercicio de conversión hacia atrás
  (margen de retailer, distribuidor, importador) se hace junto con el
  cliente, no lo resuelve el dato solo.
- **No cubre mercados asiáticos ni supermercados de Estados Unidos hoy.**
  Si el destino de exportación es Asia o EE.UU., la plataforma no aporta
  información directa en esta etapa.
- **No mide volumen de ventas ni rotación.** Muestra a qué precio está un
  producto y cuántas marcas compiten, no cuánto se vende.
- **La incorporación de un nuevo catálogo a la plataforma es manual hoy**,
  coordinada directamente con el equipo — no existe todavía un proceso de
  autoservicio.

---

## Casos de uso activos en la región

- **Piloto de validación de mercado con MYPE agroexportadoras** — formato
  Academy Lab aplicado a categorías con cobertura sólida.
- **Diagnóstico de precio y competencia en destino** para gremios y
  asociaciones de productores.
- **Insumo técnico para instrumentos de planeamiento regional** —
  competitividad, diagnóstico exportador, evaluación de propuestas
  productivas.

---

## Quiénes somos

CLI Market es desarrollado por **Sinapsis Innovadora S.A.C.**, empresa
peruana con sede en Trujillo, fundada y dirigida por **Ricardo Cuba
Alván**. El producto es de código y operación propia, con despliegue en
producción activo (`cli-market-api.fly.dev`) y publicado en PyPI
(`pip install cli-market-world`).

---

## Contacto

**Ricardo Cuba Alván**
Fundador, CLI Market | Gerente General, Sinapsis Innovadora S.A.C.
hello@cli-market.dev
Trujillo, Perú
