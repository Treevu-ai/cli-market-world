# PRD: Integración de Fuentes Externas de Comercio Exterior

## Contexto

CLI Market monitorea precio de góndola, catálogo y competencia en retailers de LATAM y España. Para el pipeline comercial con CITEs, gremios y gobiernos regionales, el precio de góndola es el punto de partida correcto, pero no el único dato que una MYPE necesita para decidir exportar.

Este PRD define la investigación y evaluación técnica necesaria para integrar fuentes externas de comercio exterior que complementen a CLI Market y permitan cerrar el ciclo: **precio de góndola → margen de canal → flete → arancel → precio FOB estimado → importadores potenciales**.

## Objetivo

Determinar qué fuentes de datos externas son técnicamente viables, legalmente utilizables y comercialmente valiosas para integrar con CLI Market en el contexto de asesoría a MYPEs exportadoras peruanas.

## Alcance

### Dentro del alcance
- Evaluación de APIs, datasets abiertos y fuentes scrapeables.
- Definición de arquitectura de integración ligera (no producto nuevo).
- Identificación de riesgos legales, de calidad y de mantenimiento.
- Propuesta de MVP de integración para el Laboratorio Comercial.

### Fuera del alcance
- Construcción de un módulo de exportaciones completo.
- Integración con sistemas aduaneros peruanos en tiempo real.
- Promesas de cobertura para mercados donde CLI Market no tiene datos de retail.

## Cadenas productivas prioritarias

| Prioridad | Cadena | Razón |
|---|---|---|
| 1 | Cacao | Mayor densidad de datos CLI Market + spread commodity/marca |
| 2 | Quinua | Cobertura sólida + valor agregado diferenciado |
| 3 | Arándano | Casos documentados con CITE Chavimochic + pipeline comercial claro |
| 4 | Palta Hass | Temporada contraria + flete refrigerado relevante |
| 5 | Café | Requiere filtrado técnico pero alto valor para MYPEs |
| 6 | Mango | Fresco/procesado + clima como variable clave |
| 7 | Uva | Mercado de Brasil como referencia |
| 8 | Alcachofa | Arancel y barreras técnicas determinantes |
| 9 | Espárrago | Alta prioridad regional, cobertura CLI Market en desarrollo |
| 10 | Pisco | Mercado doméstico fuerte, exportación en crecimiento |

## Fuentes a investigar

### 1. Precios internacionales de commodities

| Fuente | URL | Datos | Formato | Costo | Preguntas a responder |
|---|---|---|---|---|---|
| ICCO | icco.org | Precio diario cacao | Web / posible API | Gratis | ¿Hay API? ¿Frecuencia de actualización? ¿Licencia? |
| ICO | ico.org | Precio café | Web / API | Gratis | ¿Cobertura por origen? ¿Formato descargable? |
| Trading Economics | tradingeconomics.com | Commodities históricos | API pagada / web | Gratis limitado | ¿Qué commodities cubre Perú? ¿Precio de API? |
| World Bank Commodity Prices | worldbank.org | Series históricas | API / CSV | Gratis | ¿Actualización mensual suficiente? |

### 2. Comercio exterior

| Fuente | URL | Datos | Formato | Costo | Preguntas a responder |
|---|---|---|---|---|---|
| SIICEX | siicex.gob.pe | Exportaciones peruanas por empresa/producto | Web / descargas | Gratis con registro | ¿Tiene API? ¿Granularidad hasta empresa? ¿Actualización? |
| TradeMap (ITC) | trademap.org | Flujos bilaterales por HS | Web / API | Gratis con registro | ¿API estable? ¿Cobertura años? |
| UN Comtrade | comtrade.un.org | Datos oficiales de comercio | API / CSV | Gratis | ¿Latencia? ¿Calidad para Perú? |
| Export Genius | exportgenius.com | Embarques e importadores | Web / API | USD 200-500/mes | ¿Cobertura España/México/Colombia? ¿Precio exacto? |
| ImportGenius | importgenius.com | Importadores por producto | Web / API | Pagada | ¿Datos de importadores de cacao/chocolate? |
| Panjiva | panjiva.com | Datos de embarques | API | Pagada | ¿Cobertura LATAM? |

### 3. Fletes y logística

| Fuente | URL | Datos | Formato | Costo | Preguntas a responder |
|---|---|---|---|---|---|
| Freightos Baltic Index | freightos.com | Índices de flete marítimo | Web / API | Gratis para índice | ¿Rutas Perú → España/México/Colombia? ¿API? |
| Xeneta | xeneta.com | Tarifas contractuales | API | Pagada | ¿Precio para startup? ¿Cobertura LATAM? |
| Drewry | drewry.co.uk | Índices de contenedores | Web / informes | Pagada | ¿Acceso gratuito limitado? |

### 4. Aranceles y barreras técnicas

| Fuente | URL | Datos | Formato | Costo | Preguntas a responder |
|---|---|---|---|---|---|
| WTO Tariff Database | tariff.wto.org | Aranceles por país/HS | Web / descargas | Gratis | ¿API? ¿Actualización? |
| SUNAT | sunat.gob.pe | Tipo de cambio, normativa | API | Gratis | ¿Endpoints estables? |
| SENASA | senasa.gob.pe | Requisitos fitosanitarios | Web | Gratis | ¿Estructura scrapeable? |

### 5. Clima y oferta agrícola

| Fuente | URL | Datos | Formato | Costo | Preguntas a responder |
|---|---|---|---|---|---|
| USDA FAS | fas.usda.gov | Producción por país | API / informes | Gratis | ¿Cobertura de palta, uva, mango, cacao? |
| NOAA / CHIRPS | chc.ucsb.edu | Precipitación histórica | API / NetCDF | Gratis | ¿Resolución espacial útil para Perú? |
| Senamhi | senamhi.gob.pe | Clima local La Libertad | Web | Gratis | ¿API o solo web? |

## Arquitectura de integración propuesta

### Opción A: Dashboard manual del consultor (MVP)
- El consultor consulta CLI Market + fuentes externas en vivo durante el Laboratorio Comercial.
- Resultados se registran en una hoja de cálculo estándar.
- Sin desarrollo de software.
- **Tiempo**: inmediato.
- **Costo**: cero.

### Opción B: Script de análisis semi-automatizado
- Script en Python que reciba SKU de CLI Market y parámetros de origen/destino.
- Aplique reglas de margen por país y reste flete estimado.
- Genere rango FOB y lo exporte a PDF o hoja.
- **Tiempo**: 1-2 semanas.
- **Costo**: bajo (solo desarrollo interno).

### Opción C: Endpoint de integración ligera
- Nuevo endpoint en CLI Market que combine precio de góndola + flete + arancel + commodity.
- No almacena datos externos, solo los consulta en tiempo real o cachea brevemente.
- **Tiempo**: 1-2 meses.
- **Costo**: medio (infraestructura + licencias).

### Opción D: Módulo de inteligencia de exportación
- Producto completo con integraciones, alertas y reportes.
- **Tiempo**: 3-6 meses.
- **Costo**: alto.

## Recomendación de enfoque

Iniciar con **Opción A** para validar valor en el piloto de CITE Chavimochic, y paralelamente investigar **Opción B** para estandarizar el ejercicio. No avanzar a Opción C/D sin evidencia de que las MYPEs pagan o el CITE cofinancia.

## Criterios de evaluación por fuente

| Criterio | Peso | Descripción |
|---|---|---|
| Viabilidad técnica | 25% | ¿API estable? ¿Formato usable? ¿Frecuencia de actualización? |
| Costo | 20% | ¿Gratis, freemium o pago? ¿Escalable? |
| Legal / licencia | 20% | ¿Permite uso comercial? ¿Atribución requerida? |
| Calidad de datos | 20% | ¿Granularidad suficiente? ¿Cobertura geográfica útil? |
| Mantenimiento | 15% | ¿Fuente confiable a largo plazo? ¿Documentación? |

## Entregables esperados del equipo

1. **Matriz de evaluación** de cada fuente con puntaje por criterio.
2. **Arquitectura recomendada** (A, B o C) con justificación.
3. **Prototipo funcional** de Opción B si se recomienda avanzar.
4. **Análisis legal** breve sobre términos de uso de cada fuente.
5. **Roadmap** de integración con milestones de 2, 4 y 8 semanas.

## Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Fuente externa deja de funcionar | Alto | No depender de una sola fuente; tener fallback manual |
| Datos desactualizados | Medio | Documentar fecha de última actualización en cada reporte |
| Uso no autorizado de datos | Alto | Revisar términos de uso antes de integrar |
| Sobre-prometer cobertura | Alto | Ser explícito sobre qué mercados y productos cubre cada fuente |
| Complejidad técnica alta | Medio | Empezar con MVP manual antes de automatizar |

## Métricas de éxito

- Al menos 3 fuentes evaluadas con puntaje completo en 2 semanas.
- Script de Opción B funcional para cacao y quinua en 4 semanas.
- Validación con 2 MYPEs del piloto de que el análisis combinado cambió su decisión.

## Notas

- Este PRD no autoriza gastos. Cada licencia paga requiere aprobación previa.
- La integración debe respetar las restricciones de cobertura de CLI Market: no cubrir US/Asia food retail ni prometer datos que no existen.
- El lenguaje hacia el cliente debe seguir siendo honesto: "precio de góndola como punto de partida", no "precio FOB exacto".

---

*Documento preparado para el equipo de producto e ingeniería de CLI Market.*
*Fecha: 2026-07-17*
