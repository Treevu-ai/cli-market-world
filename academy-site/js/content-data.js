/**
 * Copy aprovechable del zip cli-market-academy + ecosystem-brief + guardrails GTM.
 * Números de terminal = SIMULACIÓN (no live moat).
 * No promesas de plan premium incluido · no % de ahorro inventados · no IPC fake.
 */
window.AcademyContent = {
  intelModules: [
    {
      n: "00",
      title: "Bienvenida — primer brief",
      desc: "Configuración inicial y primer pipeline de lectura de góndola formal.",
      key: "Credenciales de lab, objetivos del track y primer corte documentado.",
    },
    {
      n: "01",
      title: "El problema — 5 brechas de señal",
      desc: "Por qué el e-commerce tradicional rompe series comparables y cómo no inventar el mercado.",
      key: "Asimetría informativa y lag del IPC vs. monitoreo de góndola formal.",
    },
    {
      n: "02",
      title: "El moat como instrumento",
      desc: "Estructura del motor de datos, frescura, cobertura y confianza de recolección.",
      key: "Ingesta, normalización y quality block como instrumentos, no magia.",
    },
    {
      n: "03",
      title: "Search, compare, history",
      desc: "Búsquedas multi-retailer y reconstrucción de evidencia de precio (normalizada).",
      key: "Evidencia con as_of, retailers_n y unidades comparables.",
    },
    {
      n: "04",
      title: "Nowcast y shelf inflation",
      desc: "Señales de inflación de estantería formal (7d/30d). Complementa el IPC; no lo reemplaza.",
      key: "Ventanas cortas vs. ruido; semáforo antes de publicar.",
    },
    {
      n: "05",
      title: "Riesgo comercial",
      desc: "Volatilidad, asimetrías de precio, promos dudosas y alertas accionables a 72 h.",
      key: "Memo multi-lente: qué hacer en 72 h sin inventar cobertura.",
    },
    {
      n: "06",
      title: "Categoría y diseño de oferta",
      desc: "Spreads por categoría, mapa de marcas y whitespace de surtido con evidencia.",
      key: "One-pager de categoría con claims defendibles.",
    },
    {
      n: "07",
      title: "Affordability, cross-country, CPI bridge",
      desc: "Poder de compra, comparación entre países y puente narrativo al IPC sin claims inválidos.",
      key: "Puente metodológico: traza, no equivalencia con el instituto.",
    },
    {
      n: "08",
      title: "Capstone y certificación",
      desc: "Desk brief + risk + category + methods bajo rúbrica de rigor metodológico.",
      key: "Pack completo; inventar IPC o informal = no aprueba.",
    },
  ],
  procureModules: [
    {
      n: "00",
      title: "Bienvenida y primer comando",
      desc: "Primer contacto con el CLI de compras y autenticación del entorno de trabajo.",
      key: "Setup de locación, perfil y primer search controlado.",
    },
    {
      n: "01",
      title: "El problema del e-commerce para comprar",
      desc: "Por qué pestañas y Excel no escalan en abastecimiento institucional.",
      key: "Fricción de cotización y costo de no comparar multi-retailer.",
    },
    {
      n: "02",
      title: "Ecosistema y retailers",
      desc: "Mapa de retailers formales indexados en LATAM y señales de confianza.",
      key: "Catálogo formal vs. informal: qué entra al moat y qué no.",
    },
    {
      n: "03",
      title: "Primer contacto — búsqueda",
      desc: "Búsqueda de insumos con filtros de país, stock y especificación.",
      key: "Filtros, stock y sustitutos aceptables documentados.",
    },
    {
      n: "04",
      title: "Comparación inteligente",
      desc: "Normalización de unidades (kg, L, pack) para el costo real comparable.",
      key: "Precio por unidad real, no por etiqueta de góndola.",
    },
    {
      n: "05",
      title: "Construcción de compras",
      desc: "Canastas multi-retailer minimizando costo total (incluido envío cuando aplica).",
      key: "Trade-off producto vs. logística; criterios explícitos.",
    },
    {
      n: "06",
      title: "Del carrito al pedido",
      desc: "Ejecución, seguimiento, sustitutos y registro de la orden.",
      key: "Expediente de compra: de la decisión al pedido registrado.",
    },
    {
      n: "07",
      title: "Automatización y agentes",
      desc: "Recompras recurrentes con reglas, límites y aprobaciones.",
      key: "Reglas con techo de gasto; automatizar sin ceder el juicio.",
    },
    {
      n: "08",
      title: "Cierre y certificación",
      desc: "Ciclo de compra del trimestre documentado (ahorro solo si se midió en el lab).",
      key: "Ciclo DDM completo; ROI solo con evidencia del workbook.",
    },
  ],

  methodologySteps: {
    SIRI: [
      {
        step: "Sense",
        title: "Cifrar la señal",
        desc: "Captura de precios, stock y promos en góndola formal online del corte (país, línea, ventana).",
      },
      {
        step: "Interpret",
        title: "Interpretar",
        desc: "Separar ruido de tendencia (7d vs 30d). Shelf formal no es headline del IPC.",
      },
      {
        step: "Risk",
        title: "Evaluar riesgo",
        desc: "Exposición de margen, asimetrías y semáforo de calidad antes de cualquier claim externo.",
      },
      {
        step: "Insight",
        title: "Acción",
        desc: "Brief multi-lente: qué hacer esta semana con disclaimers y as_of visibles.",
      },
    ],
    DDM: [
      {
        step: "Detect",
        title: "Detectar",
        desc: "Sondear catálogo formal por necesidad, umbral de precio o quiebre de stock.",
      },
      {
        step: "Compare",
        title: "Comparar",
        desc: "Benchmark multi-retailer con unidades normalizadas y criterios explícitos.",
      },
      {
        step: "Decide",
        title: "Decidir",
        desc: "Elegir split de compra: costo total, entrega, reputación y límites del rol.",
      },
      {
        step: "Execute",
        title: "Ejecutar",
        desc: "Carrito/orden documentada; no es compra real hasta el paso de ejecución del lab.",
      },
      {
        step: "Improve",
        title: "Mejorar",
        desc: "Auditoría del ciclo, reglas de recompra y límites — sin % de ahorro inventados.",
      },
    ],
  },

  moatPillars: {
    title: "Retail formal online ≠ IPC oficial ≠ comercio informal",
    subtitle: "Tres capas de precio que no se deben mezclar en un claim.",
    pillars: [
      {
        n: "01",
        label: "Retail formal online",
        title: "La góndola digital",
        accent: "Alta frecuencia",
        desc: "Precios de lista y promos en e-commerce formal indexado. Frescura medible, multi-retailer, quality scores. Es el termómetro del canal online — no del país entero.",
      },
      {
        n: "02",
        label: "IPC gubernamental",
        title: "La medición oficial",
        accent: "Rezago · ponderaciones",
        desc: "Canasta oficial, metodología del instituto y publicación con lag. Sirve de ancla macro; no es lo que indexa CLI Market ni se sustituye con un 7d de góndola.",
      },
      {
        n: "03",
        label: "Comercio informal / cercanía",
        title: "El mercado físico tradicional",
        accent: "Fuera del moat",
        desc: "Ferias, barrio, cash y micro-negocios sin digitalización comparable. El moat no lo mide. Afirmarlo con datos de e-commerce formal es claim inválido en Academy.",
      },
    ],
  },

  pipeline: {
    title: "¿Ese descuento es real, o es maquillaje?",
    subtitle: "Comparamos el precio de lista de los días previos al anuncio de la oferta. Si subió justo antes de la \"oferta\", el descuento es falso — se lo mostramos así de simple, no como un gráfico suelto. El detector de promos ya corre en producción; abajo, una simulación didáctica de cómo se arma ese dato.",
    stages: [
      {
        k: "INGESTA",
        title: "Recolección de góndola",
        desc: "Precios y atributos de retailers formales online del catálogo activo.",
      },
      {
        k: "NORMALIZACIÓN",
        title: "Taxonomía y unidades",
        desc: "SKU, marca, kg/L/pack y series comparables entre cadenas.",
      },
      {
        k: "CORE",
        title: "Motor de datos",
        desc: "Series, frescura, confidence y scores listos para consulta.",
      },
      {
        k: "CONSUMO",
        title: "API · CLI · MCP",
        desc: "Desks, labs de Academy y agentes con el mismo contrato de datos.",
      },
    ],
    /** SIMULACIÓN didáctica — no telemetría live ni conteos de SKU reales */
    logDisclaimer:
      "SIMULACIÓN DIDÁCTICA · no es el stream live del moat · sin conteos ni % inventados",
    logSeed: [
      "✓ [INIT] Pipeline de demo Academy conectado (sandbox).",
      "✓ [SCOPE] Alcance: góndola formal online · no IPC · no informal.",
      "✓ [LAYERS] Ingesta → normalización → core → consumo (API / CLI / MCP).",
    ],
    logRotate: [
      "⚡ [INGESTA] Paso de recolección sobre retailers formales del catálogo (demo).",
      "✓ [NORMALIZACIÓN] Unidades y taxonomía de ejemplo — kg / L / pack.",
      "✓ [QUALITY] Semáforo de calidad: usar | monitorear | no publicar.",
      "⚡ [CORE] Corte con as_of y frescura (campos del payload real en el lab).",
      "✓ [CONSUMO] Superficie lista para API, CLI o tools MCP del curso.",
      "⚡ [SIRI] Sense → Interpret → Risk → Insight (track Intelligence).",
      "✓ [DDM] Detect → Compare → Decide → Execute → Improve (track Procure).",
      "✓ [DISCLAIMER] formal online ≠ IPC oficial ≠ comercio informal.",
    ],
  },

  mcp: {
    title: "¿Compro ahora, o espero?",
    subtitle: "Miramos si el precio de un producto está más alto o más bajo de lo normal para él — como una alerta de clima, pero de precios. Si está \"raro\", se lo decimos antes de que pierda tiempo comparando a mano. Esta señal ya corre en producción; el protocolo MCP de abajo es cómo un agente de IA la consulta.",
    features: [
      {
        title: "Protocolo estándar",
        desc: "Model Context Protocol para conectar agentes (Claude, Cursor, otros) a tools curadas de góndola formal.",
      },
      {
        title: "Consultas de producto",
        desc: "Search, compare e intel sobre retailers formales. El agente hereda frescura y límites del payload.",
      },
      {
        title: "Labs con criterio",
        desc: "En Academy el MCP es medio de evidencia: todo número sale de una tool call, no de una anécdota.",
      },
    ],
    schemaNote:
      "Esquema ilustrativo del contrato MCP (tools · resources · prompts). En el lab se usa el servidor real; aquí no hay precios ni series live.",
    schema: {
      tools: {
        tools: [
          {
            name: "market_search",
            description:
              "Busca productos en góndola formal online por país y query. Devuelve evidencia con frescura cuando el payload la trae.",
            inputSchema: {
              type: "object",
              properties: {
                query: { type: "string", description: "Producto o texto de búsqueda" },
                country: {
                  type: "string",
                  description: "Código de país del corte (ej. PE, CO, MX)",
                },
              },
              required: ["query", "country"],
            },
          },
          {
            name: "market_intel_brief",
            description:
              "Estructura de brief / nowcast de góndola formal (ventanas y quality). No sustituye el IPC oficial.",
            inputSchema: {
              type: "object",
              properties: {
                country: { type: "string" },
                line: { type: "string", description: "Línea o categoría del corte" },
                days: { type: "number", description: "Ventana orientativa (ej. 7)" },
              },
              required: ["country"],
            },
          },
          {
            name: "market_cart_optimize",
            description:
              "Comparación multi-retailer / canasta con unidades normalizadas (lab Procure). Ahorro solo si se midió.",
            inputSchema: {
              type: "object",
              properties: {
                items: {
                  type: "array",
                  items: {
                    type: "object",
                    properties: {
                      query: { type: "string" },
                      quantity: { type: "number" },
                    },
                  },
                },
                country: { type: "string" },
              },
              required: ["items", "country"],
            },
          },
        ],
      },
      resources: {
        resources: [
          {
            uri: "cli-market://docs/quality-block",
            name: "Quality block (methods)",
            description:
              "Campos de frescura, confidence y cobertura que el alumno debe citar en el workbook.",
            mimeType: "application/json",
          },
          {
            uri: "cli-market://docs/disclaimers",
            name: "Disclaimers de canal",
            description:
              "formal online ≠ IPC oficial ≠ informal — texto canónico para claims.",
            mimeType: "text/plain",
          },
          {
            uri: "cli-market://catalog/retailers",
            name: "Retailers del catálogo (referencia)",
            description:
              "Listado de cadenas del catálogo formal; cifras canónicas solo desde marketStats / GTM-Hub.",
            mimeType: "application/json",
          },
        ],
      },
      prompts: {
        prompts: [
          {
            name: "desk-brief-anomaly",
            description:
              "Plantilla de brief: headline, 7d vs 30d, quality, semáforo y bullets por lente.",
            arguments: [
              { name: "country", description: "País del corte", required: true },
              { name: "category", description: "Categoría o línea", required: true },
            ],
          },
          {
            name: "procure-cycle-ddm",
            description:
              "Plantilla DDM: detect → compare → decide → execute → improve con criterios explícitos.",
            arguments: [
              { name: "basket", description: "Lista de insumos", required: true },
              { name: "country", description: "País", required: true },
            ],
          },
          {
            name: "claim-guardrail",
            description:
              "Revisa si un claim confunde góndola formal con IPC o informal; sugiere redacción defendible.",
            arguments: [
              { name: "draft_claim", description: "Texto a auditar", required: true },
            ],
          },
        ],
      },
    },
    ctaPrimary: { label: "Ver tools en producto", href: "https://cli-market.dev/tools" },
    ctaSecondary: { label: "Solicitar acceso Academy", href: "#cta" },
  },

  workbookDeliverables: [
    {
      title: "Research / desk brief",
      desc: "Headline, ventanas, calidad y bullets por lente — una página.",
    },
    {
      title: "Risk memo + category",
      desc: "Riesgo a 72 h y one-pager de categoría o surtido con evidencia.",
    },
    {
      title: "Methods & quality block",
      desc: "as_of, retailers_n, confidence, disclaimers: formal ≠ IPC ≠ informal.",
    },
    {
      title: "Capstone del track",
      desc: "Pack Intelligence o ciclo DDM Procure bajo rúbrica (sin claims falsos).",
    },
  ],

  rubric: [
    {
      pct: "25%",
      title: "Alineación metodológica",
      desc: "SIRI o DDM aplicados con criterio; no checklist vacío.",
    },
    {
      pct: "25%",
      title: "Rigor de datos",
      desc: "Trazabilidad, quality block, semáforo. Cero IPC/informal inventados.",
    },
    {
      pct: "25%",
      title: "Entregable de valor",
      desc: "Brief/risk/category o expediente de compra usable por el rol.",
    },
    {
      pct: "25%",
      title: "Defensa del caso",
      desc: "Qué claim puede emitir y cuál queda bloqueado — oral o escrita.",
    },
  ],

  roles: [
    {
      id: "comercial",
      name: "Comercial / B2B",
      badge: "Benchmark & Pitch",
      track: "Intelligence",
      description:
        "Cuentas clave y directores comerciales que sustentan negociaciones con datos reales de góndola.",
      example:
        "Comparar en un cuadro el precio de su marca vs competidores en varios supermercados formales del corte (con as_of y frescura).",
      tip: "Útil para evitar sorpresas de precio en góndola antes de la reunión de categoría.",
    },
    {
      id: "pricing",
      name: "Pricing / Revenue",
      badge: "Ancla de list price",
      track: "Intelligence",
      description:
        "Pricing y revenue que calibran spreads y presión de la competencia sin esperar un mes al reporte.",
      example:
        "Señales 7d y 30d por categoría para decidir si congelar, monitorear o preparar un ajuste — con semáforo de calidad.",
      tip: "Lea el canal online formal antes de reescribir el forecast solo con anécdota de pasillo.",
    },
    {
      id: "research",
      name: "Research / Fintech",
      badge: "Methods citables",
      track: "Intelligence",
      description:
        "Analistas y economistas que necesitan nowcast de consumo masivo formal con metadata de calidad.",
      example:
        "Quality block (cobertura, frescura, confidence) para justificar el sesgo de muestra respecto al IPC nacional.",
      tip: "Nunca asuma góndola formal = inflación total del país. Use disclaimers.",
    },
    {
      id: "growth",
      name: "Growth / Marketing",
      badge: "Dato de la semana",
      track: "Intelligence",
      description:
        "Growth y contenido que publican variaciones de básicos con datos duros y atribución.",
      example:
        "Un dato citable de la semana con as_of, retailers_n y disclaimer de canal formal.",
      tip: "Solo publique con semáforo verde. Semáforo amarillo = interno o con advertencia fuerte.",
    },
    {
      id: "compras",
      name: "Compras / Abastecimiento",
      badge: "Optimización de gasto",
      track: "Procure",
      description:
        "Compradores y facilities que administran insumos para una o varias locaciones.",
      example:
        "Ciclo documentado: búsqueda → normalización → comparación multi-retailer → carrito/orden con criterios explícitos.",
      tip: "Reduzca el tiempo en re-tipear y compare sistemáticamente antes de negociar el contrato marco.",
    },
  ],
  faq: [
    {
      q: "¿Es un curso genérico de e-commerce o marketing digital?",
      a: "No. No enseñamos a pautar ni a armar tiendas. Es formación aplicada sobre el motor de datos de CLI Market: leer señales de góndola formal (Intelligence) o comprar con método (Procure).",
    },
    {
      q: "¿Necesito saber programar?",
      a: "No es un bootcamp de software. Los labs están pensados para profesionales de negocios, compras, pricing o research. Se guían CLI/API/MCP paso a paso; estar cómodo con datos acelera, no es requisito ser developer.",
    },
    {
      q: "¿Shelf inflation es lo mismo que el IPC oficial?",
      a: "No. El IPC mide una canasta oficial ponderada (y no es lo que indexamos). CLI Market lee precios de góndola formal online de retailers indexados. Da velocidad (nowcast) y complementa; no reemplaza INEI, DANE, INDEC, IBGE u otros institutos.",
    },
    {
      q: "¿Puedo cursar ambos tracks a la vez?",
      a: "Recomendamos secuencia, no paralelo. Procure pregunta “¿cómo compro mejor hoy?”; Intelligence pregunta “¿qué señala el mercado y qué claim puedo defender?”. Entregables y lentes mentales distintos.",
    },
    {
      q: "¿La inscripción incluye el plan pago de la API o Procure?",
      a: "El form de esta página es acceso prioritario a formación (waitlist): sin tarjeta y sin cargo automático. El acceso a labs depende de la oferta activa (p. ej. trial o credenciales de curso cuando existan). Los planes corporativos de producto son un paso posterior y opcional según su rol.",
    },
    {
      q: "¿Qué validez tiene la certificación?",
      a: "No se certifica por asistencia. Exige capstone con rúbrica (umbral orientativo ≥80%) y cero tolerancia a claims falsos (p. ej. vender góndola formal como inflación nacional o medir informal). Es un sello de rigor analítico, no un diploma decorativo.",
    },
    {
      q: "¿Cuánto tiempo necesito?",
      a: "Orientativo: ~12–18 h por track, self-paced (~2–3 semanas a 5–7 h/semana). Puede ir más lento; el capstone no se salta si busca la certificación.",
    },
  ],
  pedagogy: [
    { n: "01", title: "El problema", text: "Caso de fallo o sesgo real de retail / compras / pricing en LATAM." },
    { n: "02", title: "El concepto", text: "Fundamentos DDM o SIRI para enmarcar el juicio, no solo el comando." },
    { n: "03", title: "La demo", text: "Queries reales (o lab guiado) contra el moat de góndola formal." },
    { n: "04", title: "La práctica", text: "El alumno corre el lab equivalente y documenta en el workbook." },
    { n: "05", title: "La reflexión", text: "¿Qué claim puedo emitir con este corte — y cuál está prohibido?" },
  ],
  levels: [
    {
      id: "L3",
      title: "Intelligence Desk Lead",
      text: "Orquesta nowcast y risk para comités de pricing o comercial. Domina disclaimers y puente narrativo al IPC (sin equivalencia).",
    },
    {
      id: "L2",
      title: "Market Intelligence Pro / Procurement Lead",
      text: "Reportes avanzados de presión y riesgo, o automatiza recompras multi-retailer con límites y registro.",
    },
    {
      id: "L1",
      title: "Shelf Analyst / Purchasing Specialist",
      text: "Extrae y compara con normalización de unidades; arma brief o expediente de compra sin inventar cobertura.",
    },
  ],
  /** Terminal: SIMULACIÓN didáctica — no datos live */
  terminal: {
    intro:
      "$ academy_sandbox  # SIMULACIÓN DIDÁCTICA (no es la API live)\n\n" +
      "Elija un comando abajo para ver el tipo de salida que se entrena en cada track.\n" +
      "Los números son de ejemplo; en el curso se reemplazan por tool calls reales.",
    intel:
      "$ market intel brief --country PE --line supermercados --days 7\n\n" +
      "[SIMULACIÓN] Estructura de salida del lab Intelligence\n" +
      "[INFO] Corte: país + línea + ventana (as_of del alumno)\n" +
      "[QUALITY] data_confidence · freshness · retailers_n  ← del payload real\n\n" +
      "RESULTADO (campos a completar en el workbook):\n" +
      "  - Headline: presión | alivio | mixto\n" +
      "  - 7d vs 30d: ¿misma dirección o solo ruido corto?\n" +
      "  - Categoría a revisar: (desde trending / evidence)\n" +
      "  - Semáforo: usar | monitorear | no publicar\n\n" +
      "[ADVERTENCIA ACADEMY] Solo góndola formal online.\n" +
      "No extrapolable al IPC oficial ni al comercio informal.",
    procure:
      "$ market cart optimize  # SIMULACIÓN — flujo Procure\n\n" +
      "[SIMULACIÓN] Estructura de salida del lab Procure\n" +
      "[PROCESS] Normalizar unidades (kg / L / pack)\n" +
      "[PROCESS] Comparar multi-retailer del corte\n\n" +
      "RECOMENDACIÓN (plantilla):\n" +
      "  - Ítem A: retailer X vs Y (precio por unidad normalizado)\n" +
      "  - Ítem B: trade-off precio vs entrega / reputación\n" +
      "  - Nota flete: consolidar envíos si el lab lo mide\n" +
      "  - Ahorro: solo si se calculó en la práctica (no inventar %)\n\n" +
      "[ADVERTENCIA] Documente criterios y as_of. No es una orden real hasta Execute.",
    qualityGreen:
      "$ quality-check --coverage 90 --confidence 90 --informal=false\n\n" +
      "[EVAL] Validez metodológica para publicación…\n\n" +
      "  [CORRECTO] VERDE (USAR)\n" +
      "  Cobertura y confianza por encima del umbral orientativo.\n" +
      "  Acción: brief publicable con disclaimer de canal formal.",
    qualityYellow:
      "$ quality-check --coverage 65 --confidence 72 --informal=false\n\n" +
      "[EVAL] Validez metodológica…\n\n" +
      "  [ADVERTENCIA] AMARILLO (MONITOREAR)\n" +
      "  Lagunas de cobertura o confidence media.\n" +
      "  Acción: solo uso interno o difusión limitada con advertencias.",
    qualityRed:
      "$ quality-check --coverage 40 --confidence 50 --informal=false\n\n" +
      "[EVAL] Validez metodológica…\n\n" +
      "  [BLOQUEADO] ROJO (NO PUBLICAR)\n" +
      "  El corte no sostiene un claim externo.\n" +
      "  Acción: esperar refresh o ampliar evidencia.",
    qualityInformal:
      "$ quality-check --informal=true\n\n" +
      "[EVAL] Validez metodológica…\n\n" +
      "  [CRÍTICO] RECHAZADO\n" +
      "  No está permitido afirmar informal / ferias / 'inflación del país'\n" +
      "  a partir del moat de góndola formal online.\n" +
      "  Riesgo reputacional: alto. Claim indefendible.",
  },
  semaforo: {
    green: {
      label: "Semáforo verde (usar)",
      desc: "Cobertura y confianza orientativas altas. Publicación externa posible si cita metodología de góndola formal y as_of.",
    },
    yellow: {
      label: "Semáforo amarillo (monitorear)",
      desc: "Muestra parcial. Preferible análisis interno o reportes con advertencia explícita de rango y cobertura.",
    },
    red: {
      label: "Semáforo rojo (no publicar)",
      desc: "Confianza o cobertura insuficiente. No sostener claims externos con este corte.",
    },
    informal: {
      label: "Rechazado (claim inválido)",
      desc: "Prohibido extrapolar e-commerce formal a informal, ferias o 'inflación nacional' sin ser el IPC.",
    },
  },
};
