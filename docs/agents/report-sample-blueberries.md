# 🫐 Price Pulse: Intelligence Report (Sample)
**Categoría:** Arándanos / Blueberries  
**Frecuencia:** Cada 4 horas  
**Golden Records Analizados:** 12 SKUs normalizados  
**Mercados:** Perú (Origen/Local) vs. España (Destino/Referencia)

---

## 🟢 SECCIÓN A: Para Exportadores (Dominio del Margen en Destino)

En los últimos 7 días, el precio del arándano convencional ha mostrado una asimetría crítica entre retailers de destino. Para un exportador, estar ciego ante el "Shelf Price" es ceder poder de negociación al distribuidor.

| Retailer | Mercado | SKU | Precio (Góndola) | Unit Price (Normalizado) | Confianza |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Wong** | PE (Lima) | 125g Clamshell | PEN 8.90 | **PEN 71.20/kg** | 🟢 98% |
| **Carrefour** | ES (Madrid) | 125g Clamshell | EUR 2.49 | **EUR 19.92/kg (~PEN 80)** | 🟢 95% |
| **El Corte Inglés**| ES (Madrid) | 125g Premium | EUR 3.99 | **EUR 31.92/kg (~PEN 128)** | 🟢 97% |

**Insight Estratégico:** Mientras que el precio en Lima es estable, en Madrid existe un **spread del 60%** entre retailers generalistas y premium. Si su producto está en Carrefour a precio de ECI, su rotación está en riesgo por falta de competitividad.

---

## 🔵 SECCIÓN B: Para Importadores y Retailers Locales (Optimización de Reposición)

Para quien compra o distribuye en el mercado local, la visibilidad de la góndola digital permite anticipar movimientos de la competencia y ajustar el "Cost-to-Serve".

**1. Benchmark de Competitividad Local (Perú)**
Monitoreo de spreads entre los principales jugadores para el SKU `prod_berries_conv_125`:
*   **Retailer A:** PEN 8.50 (Líder en precio, 12% por debajo de la media).
*   **Retailer B:** PEN 11.20 (Posible sobrestock o pricing ineficiente).
*   **Retailer C:** PEN 9.90 (Precio de equilibrio).

**2. Alerta de Quiebre de Stock (Stock-out Risk)**
*   Detectamos que el 30% de las tiendas digitales del **Retailer B** muestran "Producto no disponible" en las últimas 12 horas. 
*   **Oportunidad:** Ventana para capturar demanda insatisfecha ajustando el pauta de marketing o reposición en puntos de venta cercanos.

---

## 🛠️ El Activo Tecnológico: Golden Records

A diferencia de un scraping genérico de nombres, CLI Market utiliza **Entity Resolution** para consolidar la data:

1.  **ID Único:** El sistema identifica que "Arándano Azul 125g", "Berry Pack" y "Mora Azul" son el mismo **Golden Record** (`prod_berries_conv_125`).
2.  **Normalización:** Todos los precios se llevan a **Precio por kg**, eliminando la distorsión de los distintos gramajes de empaque.
3.  **Filtro de Ruido:** Se eliminan automáticamente precios de liquidación o errores de carga del retailer que podrían sesgar sus promedios de Revenue Strategy.

---

### ¿Cómo capitalizar esta información?

*   **Exportador:** "Sabemos que el retailer X subió el unit price un 20%, ajustemos el precio de exportación para capturar parte de ese incremento de margen."
*   **Importador/Distribuidor:** "Mi competencia está sin stock en el sector norte de Lima; es momento de empujar mi inventario en ese clúster."
*   **Revenue Manager:** "La inflación real de la categoría en góndola es de 4.2% mensual, muy por encima del reporte oficial. Debemos ajustar precios hoy."

---

**¿Quiere el reporte completo y automatizado de su categoría?**
Este es un extracto de la capa **Intelligence**. El programa piloto ($300-$500/mo) le entrega acceso total a los Golden Records de su sector y alertas en tiempo real.

**CLI Market: El Bloomberg de la góndola LatAm.**
