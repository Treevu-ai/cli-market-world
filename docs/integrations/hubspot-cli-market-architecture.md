# Arquitectura Técnica: HubSpot + CLI Market (PYMEs Perú)

**Versión:** 1.0  
**Fecha:** 2026-07-31  
**Prioridad:** #2 - Líder PYMEs Perú + Ecosistema Completo

---

## 🎯 Objetivo de la Integración

Integrar inteligencia de mercado de CLI Market en el ecosistema HubSpot para PYMEs peruanas, permitiendo:

1. **Lead scoring enriquecido** con señales de estrés de canasta peruana
2. **Dashboard de inteligencia de mercado** dentro de HubSpot
3. **Alertas de precios** en oportunidades de venta
4. **Forecasting mejorado** con indicadores macro de Perú
5. **Segmentación de clientes** por poder adquisitivo regional

---

## 🏗️ Arquitectura General

```mermaid
graph TB
    A[HubSpot CRM] --> B[HubSpot API]
    B --> C[Middleware Python]
    C --> D{CLI Market API}
    D --> E[Intelligence Endpoints]
    E --> F[Market Data Peru]
    F --> C
    C --> G[Data Transformation]
    G --> H[HubSpot Custom Objects]
    H --> A
    
    I[HubSpot Workflows] --> J[Webhook Triggers]
    J --> C
    K[CLI Market Webhooks Enterprise] --> L[Alert Manager]
    L --> C
    C --> M[Slack/Email Notifications]
```

---

## 🔌 Componentes de la Integración

### 1. **HubSpot API Client (Python)**
```python
# hubspot_client.py
import httpx
import os
from typing import Dict, List, Optional
from hubspot import HubSpot

class HubSpotClient:
    def __init__(self):
        self.api_key = os.getenv("HUBSPOT_API_KEY")
        self.hubspot = HubSpot(api_key=self.api_key)
    
    def get_contact_by_id(self, contact_id: str) -> Dict:
        """Obtener contacto por ID"""
        try:
            contact = self.hubspot.crm.contacts.basic_api.get_by_id(contact_id)
            return contact.to_dict()
        except Exception as e:
            print(f"Error getting contact: {e}")
            return {}
    
    def get_deal_by_id(self, deal_id: str) -> Dict:
        """Obtener oportunidad por ID"""
        try:
            deal = self.hubspot.crm.deals.basic_api.get_by_id(deal_id)
            return deal.to_dict()
        except Exception as e:
            print(f"Error getting deal: {e}")
            return {}
    
    def update_contact_property(self, contact_id: str, property_name: str, value: str):
        """Actualizar propiedad de contacto"""
        try:
            self.hubspot.crm.contacts.basic_api.update(
                contact_id,
                {"properties": {property_name: value}}
            )
        except Exception as e:
            print(f"Error updating contact: {e}")
    
    def update_deal_property(self, deal_id: str, property_name: str, value: str):
        """Actualizar propiedad de oportunidad"""
        try:
            self.hubspot.crm.deals.basic_api.update(
                deal_id,
                {"properties": {property_name: value}}
            )
        except Exception as e:
            print(f"Error updating deal: {e}")
    
    def create_custom_object(self, object_type: str, data: Dict) -> Dict:
        """Crear registro en objeto personalizado"""
        try:
            response = self.hubspot.crm.objects.custom_object.basic_api.create(
                object_type,
                {"properties": data}
            )
            return response.to_dict()
        except Exception as e:
            print(f"Error creating custom object: {e}")
            return {}
    
    def get_deals_associated_with_contact(self, contact_id: str) -> List[Dict]:
        """Obtener oportunidades asociadas a un contacto"""
        try:
            associations = self.hubspot.crm.contacts.associations_api.get_all(
                contact_id,
                "deal"
            )
            return [assoc.to_dict() for assoc in associations.results]
        except Exception as e:
            print(f"Error getting associated deals: {e}")
            return []
```

### 2. **CLI Market Intelligence Client**
```python
# cli_market_intelligence.py
import httpx
import os
from typing import Dict, List

class CLIMarketIntelligence:
    def __init__(self):
        self.api_url = os.getenv("CLI_MARKET_API_URL", "https://cli-market-api.fly.dev")
        self.api_key = os.getenv("CLI_MARKET_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_intel_brief(self, country: str = "PE", line: str = "supermercados", days: int = 7) -> Dict:
        """Obtener brief de inteligencia de mercado"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/v1/intel/brief",
                headers=self.headers,
                params={"country": country, "line": line, "days": days}
            )
            return response.json()
    
    async def get_scores(self, country: str = "PE", line: str = "supermercados") -> Dict:
        """Obtener scores compuestos de mercado"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/v1/intel/scores",
                headers=self.headers,
                params={"country": country, "line": line}
            )
            return response.json()
    
    async def get_inflation(self, country: str = "PE", line: str = "supermercados", days: int = 30) -> Dict:
        """Obtener datos de inflación de estantería"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/v1/intel/inflation",
                headers=self.headers,
                params={"country": country, "line": line, "days": days}
            )
            return response.json()
    
    async def get_price_risk(self, country: str = "PE", line: str = "supermercados", days: int = 7) -> Dict:
        """Obtener análisis de riesgo de precios"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/v1/intel/price_risk",
                headers=self.headers,
                params={"country": country, "line": line, "days": days}
            )
            return response.json()
    
    async def get_procurement_signal(self, country: str = "PE", line: str = "supermercados") -> Dict:
        """Obtener señales de procurement"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/v1/intel/procurement_signal",
                headers=self.headers,
                params={"country": country, "line": line}
            )
            return response.json()
```

### 3. **Middleware de Integración**
```python
# hubspot_cli_market_middleware.py
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import asyncio
from hubspot_client import HubSpotClient
from cli_market_intelligence import CLIMarketIntelligence

app = FastAPI()
hubspot = HubSpotClient()
cli_market = CLIMarketIntelligence()

class HubSpotWebhook(BaseModel):
    subscription_type: str
    event_id: str
    object_id: str
    change_source: str
    occurred_at: int
    attempt_number: int

class MarketIntelligenceData(BaseModel):
    country: str = "PE"
    line: str = "supermercados"
    days: int = 7

async def enrich_contact_with_market_intelligence(contact_id: str):
    """Enriquecer contacto con inteligencia de mercado"""
    
    # Obtener datos del contacto
    contact = hubspot.get_contact_by_id(contact_id)
    if not contact:
        return
    
    # Obtener región del contacto (asumimos que está en custom property)
    region = contact.get("properties", {}).get("region", "PE")
    
    # Obtener inteligencia de mercado
    intel_brief = await cli_market.get_intel_brief(country=region)
    scores = await cli_market.get_scores(country=region)
    
    # Calcular estrés de canasta personalizado basado en datos del contacto
    basket_stress = calculate_personal_basket_stress(contact, scores)
    
    # Actualizar propiedades del contacto
    hubspot.update_contact_property(
        contact_id,
        "market_basket_stress",
        str(basket_stress)
    )
    hubspot.update_contact_property(
        contact_id,
        "market_inflation_signal",
        intel_brief.get("shelf_signal", "neutral")
    )
    hubspot.update_contact_property(
        contact_id,
        "market_price_fairness",
        str(scores.get("price_fairness", 0))
    )
    hubspot.update_contact_property(
        contact_id,
        "market_retail_aggression",
        str(scores.get("retail_aggression", 0))
    )
    hubspot.update_contact_property(
        contact_id,
        "market_data_updated",
        intel_brief.get("timestamp", "")
    )

def calculate_personal_basket_stress(contact: Dict, scores: Dict) -> float:
    """Calcular estrés de canasta personalizado"""
    # Lógica personalizada basada en datos del contacto
    # Por ejemplo, ingresos, familia, ubicación, etc.
    
    base_stress = scores.get("basket_stress", 0)
    
    # Ajustar por ingresos del contacto
    income_level = contact.get("properties", {}).get("income_level", "medium")
    income_multiplier = {
        "low": 1.5,
        "medium": 1.0,
        "high": 0.7
    }.get(income_level, 1.0)
    
    # Ajustar por tamaño de familia
    family_size = int(contact.get("properties", {}).get("family_size", 1))
    family_multiplier = 1.0 + (family_size - 1) * 0.2
    
    personal_stress = base_stress * income_multiplier * family_multiplier
    
    return min(personal_stress, 1.0)  # Cap at 1.0

async def enrich_deal_with_price_intelligence(deal_id: str):
    """Enriquecer oportunidad con inteligencia de precios"""
    
    # Obtener datos de la oportunidad
    deal = hubspot.get_deal_by_id(deal_id)
    if not deal:
        return
    
    # Obtener productos de la oportunidad (asumimos custom property)
    products = deal.get("properties", {}).get("products", "")
    if not products:
        return
    
    # Analizar riesgo de precios para los productos
    price_risk = await cli_market.get_price_risk(country="PE")
    
    # Obtener señales de procurement
    procurement_signal = await cli_market.get_procurement_signal(country="PE")
    
    # Actualizar propiedades de la oportunidad
    hubspot.update_deal_property(
        deal_id,
        "price_risk_level",
        price_risk.get("risk_level", "moderate")
    )
    hubspot.update_deal_property(
        deal_id,
        "procurement_signal",
        procurement_signal.get("signal", "monitor")
    )
    hubspot.update_deal_property(
        deal_id,
        "market_recommended_action",
        get_recommended_action(procurement_signal)
    )
    hubspot.update_deal_property(
        deal_id,
        "price_intelligence_updated",
        datetime.utcnow().isoformat()
    )

def get_recommended_action(procurement_signal: Dict) -> str:
    """Obtener acción recomendada basada en señal de procurement"""
    signal = procurement_signal.get("signal", "monitor")
    
    actions = {
        "buy_now": "Contactar ahora - oportunidad de compra óptima",
        "monitor": "Monitorear - mercado estable, no hay urgencia",
        "wait": "Esperar - se esperan mejores precios pronto"
    }
    
    return actions.get(signal, "Monitorear mercado")

@app.post("/webhook/hubspot")
async def hubspot_webhook(webhook: HubSpotWebhook, background_tasks: BackgroundTasks):
    """Webhook principal de HubSpot"""
    
    if webhook.subscription_type == "contact.creation":
        # Enriquecer nuevo contacto con inteligencia de mercado
        background_tasks.add_task(
            enrich_contact_with_market_intelligence,
            webhook.object_id
        )
        return {"status": "contact_enrichment_scheduled"}
    
    elif webhook.subscription_type == "deal.creation":
        # Enriquecer nueva oportunidad con inteligencia de precios
        background_tasks.add_task(
            enrich_deal_with_price_intelligence,
            webhook.object_id
        )
        return {"status": "deal_enrichment_scheduled"}
    
    elif webhook.subscription_type == "contact.propertyChange":
        # Actualizar inteligencia si cambian propiedades relevantes
        # (ingresos, región, familia, etc.)
        background_tasks.add_task(
            enrich_contact_with_market_intelligence,
            webhook.object_id
        )
        return {"status": "contact_update_scheduled"}
    
    return {"status": "no_action_required"}

@app.post("/api/enrich-contact/{contact_id}")
async def manual_enrich_contact(contact_id: str):
    """Endpoint para enriquecimiento manual de contacto"""
    await enrich_contact_with_market_intelligence(contact_id)
    return {"status": "enriched", "contact_id": contact_id}

@app.post("/api/enrich-deal/{deal_id}")
async def manual_enrich_deal(deal_id: str):
    """Endpoint para enriquecimiento manual de oportunidad"""
    await enrich_deal_with_price_intelligence(deal_id)
    return {"status": "enriched", "deal_id": deal_id}

@app.get("/api/market-intelligence/summary")
async def market_intelligence_summary(country: str = "PE"):
    """Endpoint para resumen de inteligencia de mercado"""
    
    intel_brief = await cli_market.get_intel_brief(country=country)
    scores = await cli_market.get_scores(country=country)
    inflation = await cli_market.get_inflation(country=country)
    
    return {
        "country": country,
        "timestamp": datetime.utcnow().isoformat(),
        "intel_brief": intel_brief,
        "scores": scores,
        "inflation": inflation
    }
```

---

## 🔄 Flujos de Datos Específicos

### Flujo 1: Creación de Contacto
```mermaid
sequenceDiagram
    participant H as HubSpot
    participant W as Webhook
    participant M as Middleware
    participant CLI as CLI Market API
    participant HS as HubSpot API
    
    H->>W: contact.creation
    W->>M: POST /webhook/hubspot
    M->>HS: GET contact data
    HS->>M: contact properties
    M->>CLI: GET /v1/intel/brief
    CLI->>M: intel brief
    M->>CLI: GET /v1/intel/scores
    CLI->>M: scores
    M->>M: calculate_personal_basket_stress()
    M->>HS: UPDATE contact properties
    HS->>H: Contact enriched
```

### Flujo 2: Creación de Oportunidad
```mermaid
sequenceDiagram
    participant H as HubSpot
    participant W as Webhook
    participant M as Middleware
    participant CLI as CLI Market API
    participant HS as HubSpot API
    
    H->>W: deal.creation
    W->>M: POST /webhook/hubspot
    M->>HS: GET deal data
    HS->>M: deal properties
    M->>CLI: GET /v1/intel/price_risk
    CLI->>M: price risk analysis
    M->>CLI: GET /v1/intel/procurement_signal
    CLI->>M: procurement signal
    M->>M: get_recommended_action()
    M->>HS: UPDATE deal properties
    HS->>H: Deal enriched
```

### Flujo 3: Actualización de Propiedades
```mermaid
sequenceDiagram
    participant H as HubSpot
    participant W as Webhook
    participant M as Middleware
    participant CLI as CLI Market API
    participant HS as HubSpot API
    
    H->>W: contact.propertyChange (income_level)
    W->>M: POST /webhook/hubspot
    M->>HS: GET updated contact
    HS->>M: new income_level
    M->>CLI: GET /v1/intel/brief
    CLI->>M: updated intel
    M->>M: recalculate_basket_stress()
    M->>HS: UPDATE contact properties
    HS->>H: Contact re-enriched
```

---

## 🎯 Casos de Uso Específicos Perú

### Caso 1: Lead Scoring para PYME Peruana
```python
# Contexto: Nuevo contacto de empresa peruana
contact_data = {
    "properties": {
        "firstname": "Juan",
        "lastname": "Pérez",
        "company": "Tienda ABC",
        "region": "PE",
        "income_level": "medium",
        "family_size": "4",
        "industry": "retail"
    }
}

# Middleware enriquece automáticamente
await enrich_contact_with_market_intelligence(contact_id)

# Propiedades actualizadas en HubSpot:
updated_properties = {
    "market_basket_stress": "0.65",  # Estrés moderado-alto
    "market_inflation_signal": "stable",  # Señal estable
    "market_price_fairness": "89.1",  # Precios justos
    "market_retail_aggression": "85.6",  # Alta agresión de promos
    "market_data_updated": "2026-07-31T10:30:00Z"
}

# Lead scoring se ajusta automáticamente:
# - Estrés de canasta alto → Prioridad de contacto aumentada
# - Agresión de retail alta → Oportunidad de venta promocional
```

### Caso 2: Oportunidad de Venta B2B
```python
# Contexto: Nueva oportunidad de venta a restaurante
deal_data = {
    "properties": {
        "dealname": "Suministro mensual Restaurante Lima",
        "amount": "5000",
        "products": "arroz, aceite, azúcar, especias",
        "region": "PE",
        "dealstage": "qualifiedtobuy"
    }
}

# Middleware enriquece con inteligencia de precios
await enrich_deal_with_price_intelligence(deal_id)

# Propiedades actualizadas en HubSpot:
updated_deal_properties = {
    "price_risk_level": "moderate",  # Riesgo moderado
    "procurement_signal": "buy_now",  # Señal de compra ahora
    "market_recommended_action": "Contactar ahora - oportunidad de compra óptima",
    "price_intelligence_updated": "2026-07-31T10:30:00Z"
}

# Sales team recibe alerta en HubSpot:
# "Procurement signal: BUY_NOW - Contactar cliente ahora"
```

### Caso 3: Dashboard de Inteligencia de Mercado
```python
# Contexto: Dashboard personalizado en HubSpot
market_summary = await market_intelligence_summary(country="PE")

# Datos disponibles en el dashboard:
dashboard_data = {
    "shelf_signal": "4.3 pp below official CPI",
    "retail_aggression": 85.6,  # Alta agresión de promos
    "price_fairness": 89.1,  # Precios justos
    "basket_stress": 0.0,  # Sin estrés
    "inflation_rpv": -61.6%,  # Deflación
    "procurement_signal": "buy_now",  # Buen momento para comprar
    "price_risk": "moderate"  # Riesgo moderado
}

# Visualización en HubSpot Dashboard:
# - Gráfico de inflación de estantería vs CPI oficial
# - Indicador de agresión de retail
# - Señal de procurement con recomendación de acción
# - Mapa de calor de estrés de canasta por región
```

---

## 🔐 Configuración de HubSpot

### 1. **Crear Propiedades Personalizadas en HubSpot**

```python
# Propiedades de Contacto:
contact_properties = [
    {
        "name": "market_basket_stress",
        "label": "Market Basket Stress",
        "type": "number",
        "description": "Estrés de canasta personalizado (0-1)"
    },
    {
        "name": "market_inflation_signal",
        "label": "Market Inflation Signal",
        "type": "string",
        "description": "Señal de inflación de mercado"
    },
    {
        "name": "market_price_fairness",
        "label": "Market Price Fairness",
        "type": "number",
        "description": "Índice de justicia de precios (0-100)"
    },
    {
        "name": "market_retail_aggression",
        "label": "Market Retail Aggression",
        "type": "number",
        "description": "Índice de agresión de retail (0-100)"
    },
    {
        "name": "market_data_updated",
        "label": "Market Data Updated",
        "type": "datetime",
        "description": "Última actualización de datos de mercado"
    },
    {
        "name": "region",
        "label": "Region",
        "type": "string",
        "description": "Región del contacto (PE, AR, MX, etc.)"
    },
    {
        "name": "income_level",
        "label": "Income Level",
        "type": "enumeration",
        "description": "Nivel de ingresos (low, medium, high)"
    },
    {
        "name": "family_size",
        "label": "Family Size",
        "type": "number",
        "description": "Tamaño de familia"
    }
]

# Propiedades de Deal (Oportunidad):
deal_properties = [
    {
        "name": "price_risk_level",
        "label": "Price Risk Level",
        "type": "enumeration",
        "description": "Nivel de riesgo de precios (low, moderate, high)"
    },
    {
        "name": "procurement_signal",
        "label": "Procurement Signal",
        "type": "enumeration",
        "description": "Señal de procurement (buy_now, monitor, wait)"
    },
    {
        "name": "market_recommended_action",
        "label": "Market Recommended Action",
        "type": "string",
        "description": "Acción recomendada basada en inteligencia de mercado"
    },
    {
        "name": "price_intelligence_updated",
        "label": "Price Intelligence Updated",
        "type": "datetime",
        "description": "Última actualización de inteligencia de precios"
    },
    {
        "name": "products",
        "label": "Products",
        "type": "string",
        "description": "Productos de la oportunidad (separados por comas)"
    }
]
```

### 2. **Configurar Webhooks en HubSpot**

```python
# En HubSpot Settings > Webhooks:
# 1. Crear nuevo webhook:
#    URL: https://tu-server.com/webhook/hubspot
#    Auth Type: API Key
#    API Key: tu-hubspot-api-key

# 2. Suscribir a eventos:
#    - contact.creation
#    - contact.propertyChange
#    - deal.creation
#    - deal.propertyChange

# 3. Seleccionar propiedades específicas para monitorear:
#    - contact: region, income_level, family_size
#    - deal: products, amount, region
```

### 2b. **Endpoint privado: deals recientes** ⚠️ PRIVADO — no exponer en documentación pública ni en `/docs` (OpenAPI) sin auth

`GET /api/crm/deals/recent` en el adapter (`cli_market_integrations/adapters/hubspot/app.py`). Requiere el header `X-CRM-Api-Key`; sin él, o si no coincide, responde `401` — incluso si `CRM_API_KEY` no está configurado en el servidor (nunca "abre" el endpoint por falta de configuración). Si `HUBSPOT_ACCESS_TOKEN` no está seteado, responde `503` antes de intentar la llamada a HubSpot.

Internamente usa `POST /crm/v3/objects/deals/search` (no el `GET` de listado — ese no soporta `filterGroups`), filtrando `createdate` con un timestamp Unix en milisegundos (formato que exige HubSpot para propiedades de fecha).

**Request:**
```
GET /api/crm/deals/recent?limit=5&days=365
X-CRM-Api-Key: <CRM_API_KEY>
```

**Response 200 — ejemplo real, verificado en vivo contra producción el 2026-08-10:**
```json
{
  "count": 1,
  "days": 365,
  "limit": 5,
  "pipeline": null,
  "deals": [
    {
      "deal_id": "63361085465",
      "dealname": "Integraciones ERP - Estación 90",
      "amount": "1500",
      "dealstage": "appointmentscheduled",
      "pipeline": "default",
      "createdate": "2026-08-03T01:18:12.560Z",
      "closedate": "2026-08-05T02:05:47.261Z",
      "hubspot_url": "https://app.hubspot.com/contacts/51814253/deal/63361085465"
    }
  ]
}
```
Con `days=3` en vez de `365` este mismo deal cae fuera del filtro (`count: 0`) — confirma que `createdate >= now - days` filtra de verdad, no solo pagina.

`hubspot_url` es `null` únicamente si `HUBSPOT_PORTAL_ID` no está seteado — en `cli-market-hubspot` **sí lo está** (`51814253`, el `portalId` de la cuenta, obtenido vía `GET /account-info/v3/details` con el mismo `HUBSPOT_ACCESS_TOKEN`; no es secreto, es el identificador público que usan las URLs de HubSpot).

**Errores:** `401` (API key faltante/incorrecta) · `422` (`limit`/`days` fuera de rango — `limit` 1-100, `days` 1-365) · `503` (HubSpot sin token configurado, o la búsqueda a HubSpot falló).

**Config en producción (Fly secrets, NO en `fly.hubspot.toml`) — ya seteada en `cli-market-hubspot`:**
```
CRM_API_KEY        # generado con secrets.token_urlsafe(32), rotar vía fly secrets import si se filtra
HUBSPOT_ACCESS_TOKEN   # pat-na1-... (Private App, scope deals.read)
HUBSPOT_PORTAL_ID  # 51814253
```
Para rotar o setear en otro entorno: `printf 'NOMBRE=valor\n' | fly secrets import --app cli-market-hubspot --stage`, luego `fly deploy --app cli-market-hubspot --config fly.hubspot.toml --remote-only` para que tome efecto (import por sí solo solo deja el secreto en staged). Guardar el valor de `CRM_API_KEY` en un gestor de secretos aparte al generarlo — Fly no permite leerlo de vuelta después de seteado.
`CRM_API_KEY` se lee como cualquier otro secreto (`os.getenv`) — deliberadamente **no** se agregó al bloque `[env]` de `fly.hubspot.toml` como pedía la instrucción original, porque ese archivo está versionado en git y `[env]` queda en texto plano en el repo.

### 3. **Crear Workflows de HubSpot**

```python
# Workflow 1: Lead Scoring con Inteligencia de Mercado
workflow_lead_scoring = {
    "name": "Lead Scoring - Market Intelligence",
    "trigger": "Contact created or property changed",
    "conditions": [
        {
            "property": "market_basket_stress",
            "operator": "greater_than",
            "value": "0.7"
        }
    ],
    "actions": [
        {
            "type": "increase_score",
            "value": 20,
            "reason": "Alto estrés de canasta - alta prioridad"
        },
        {
            "type": "send_notification",
            "channel": "slack",
            "message": "Lead con alto estrés de canasta: {{contact.firstname}} {{contact.lastname}}"
        }
    ]
}

# Workflow 2: Alertas de Oportunidades de Venta
workflow_deal_alerts = {
    "name": "Deal Alerts - Procurement Signal",
    "trigger": "Deal created or property changed",
    "conditions": [
        {
            "property": "procurement_signal",
            "operator": "equals",
            "value": "buy_now"
        }
    ],
    "actions": [
        {
            "type": "send_notification",
            "channel": "email",
            "recipients": ["sales-team@company.com"],
            "template": "Procurement signal BUY_NOW - Contactar cliente {{deal.dealname}}"
        },
        {
            "type": "create_task",
            "assignee": "sales_rep",
            "task": "Contactar cliente - señal de compra óptima"
        }
    ]
}
```

---

## 📊 Monitoreo y Analytics

### 1. **Métricas de Integración**
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Contadores
hubspot_webhooks_total = Counter(
    'hubspot_webhooks_total',
    'Total de webhooks recibidos de HubSpot',
    ['subscription_type', 'status']
)

contact_enrichments_total = Counter(
    'contact_enrichments_total',
    'Total de enriquecimientos de contactos',
    ['status']
)

deal_enrichments_total = Counter(
    'deal_enrichments_total',
    'Total de enriquecimientos de oportunidades',
    ['status']
)

cli_market_api_calls_total = Counter(
    'cli_market_api_calls_total',
    'Total de llamadas a CLI Market API',
    ['endpoint', 'status']
)

# Histogramas
enrichment_duration = Histogram(
    'enrichment_duration_seconds',
    'Duración del proceso de enriquecimiento',
    ['enrichment_type']
)

# Gauges
market_basket_stress_avg = Gauge(
    'market_basket_stress_avg',
    'Promedio de estrés de canasta en contactos'
)

retail_aggression_avg = Gauge(
    'retail_aggression_avg',
    'Promedio de agresión de retail'
)
```

### 2. **Dashboard de Monitoreo**
```python
# monitoring.py
from fastapi import FastAPI
from prometheus_client import generate_latest

@app.get("/metrics")
async def metrics():
    """Endpoint para Prometheus metrics"""
    return generate_latest()

@app.get("/health/integration")
async def integration_health():
    """Health check específico de la integración"""
    hubspot_health = await check_hubspot_health()
    cli_market_health = await check_cli_market_health()
    
    return {
        "status": "healthy" if all([hubspot_health, cli_market_health]) else "degraded",
        "hubspot_api": hubspot_health,
        "cli_market_api": cli_market_health,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/analytics/enrichment-stats")
async def enrichment_stats():
    """Estadísticas de enriquecimiento"""
    return {
        "total_contacts_enriched": contact_enrichments_total._value.get(),
        "total_deals_enriched": deal_enrichments_total._value.get(),
        "avg_basket_stress": market_basket_stress_avg._value.get(),
        "avg_retail_aggression": retail_aggression_avg._value.get(),
        "success_rate": calculate_success_rate()
    }
```

---

## 🚀 Implementación

### Paso 1: Configuración Inicial
```bash
# 1. Clonar repositorio
git clone https://github.com/your-org/hubspot-cli-market-integration.git
cd hubspot-cli-market-integration

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install fastapi uvicorn httpx hubspot-api prometheus-client python-dotenv

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys
```

### Paso 2: Configurar HubSpot
```bash
# 1. Ir a HubSpot Settings > Webhooks
# 2. Crear nuevo webhook con URL de tu servidor
# 3. Configurar las propiedades personalizadas mencionadas arriba
# 4. Crear los workflows automatizados
```

### Paso 3: Desplegar Middleware
```bash
# Usando Docker
docker build -t hubspot-cli-market-middleware .
docker run -p 8000:8000 --env-file .env hubspot-cli-market-middleware

# O usando uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🧪 Testing

### 1. **Unit Tests**
```python
# tests/test_hubspot_client.py
import pytest
from hubspot_client import HubSpotClient

@pytest.mark.asyncio
async def test_get_contact_by_id():
    client = HubSpotClient()
    contact = client.get_contact_by_id("12345")
    
    assert contact is not None
    assert "properties" in contact

@pytest.mark.asyncio
async def test_update_contact_property():
    client = HubSpotClient()
    result = client.update_contact_property("12345", "test_property", "test_value")
    
    assert result is not None  # HubSpot API no retorna mucho en updates

# tests/test_cli_market_intelligence.py
import pytest
from cli_market_intelligence import CLIMarketIntelligence

@pytest.mark.asyncio
async def test_get_intel_brief():
    client = CLIMarketIntelligence()
    intel = await client.get_intel_brief(country="PE")
    
    assert "shelf_signal" in intel
    assert "scores" in intel
```

### 2. **Integration Tests**
```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_hubspot_webhook():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/webhook/hubspot",
            json={
                "subscription_type": "contact.creation",
                "event_id": "test-event-123",
                "object_id": "contact-456",
                "change_source": "EXTERNAL",
                "occurred_at": 1659263400,
                "attempt_number": 1
            }
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "contact_enrichment_scheduled"
```

---

## 📝 Documentación API

### Endpoint: POST /webhook/hubspot
**Propósito:** Recibir webhooks de HubSpot

**Request Body:**
```json
{
  "subscription_type": "contact.creation",
  "event_id": "evt-abc-123",
  "object_id": "contact-456",
  "change_source": "EXTERNAL",
  "occurred_at": 1659263400,
  "attempt_number": 1
}
```

**Response:**
```json
{
  "status": "contact_enrichment_scheduled",
  "object_id": "contact-456"
}
```

### Endpoint: POST /api/enrich-contact/{contact_id}
**Propósito:** Enriquecimiento manual de contacto

**Response:**
```json
{
  "status": "enriched",
  "contact_id": "contact-456"
}
```

### Endpoint: GET /api/market-intelligence/summary
**Propósito:** Resumen de inteligencia de mercado

**Parameters:**
- `country` (optional): País para análisis (default: "PE")

**Response:**
```json
{
  "country": "PE",
  "timestamp": "2026-07-31T10:30:00Z",
  "intel_brief": {
    "shelf_signal": "4.3 pp below official CPI"
  },
  "scores": {
    "retail_aggression": 85.6,
    "price_fairness": 89.1
  },
  "inflation": {
    "rpv": -61.6
  }
}
```

---

## 🎯 Métricas de Éxito

### KPIs de la Integración
- **Tiempo de enriquecimiento:** < 5 segundos por contacto
- **Precisión de lead scoring:** Mejora del 25% en conversión
- **Tasa de adopción:** > 80% de contactos enriquecidos automáticamente
- **Impacto en ventas:** Incremento del 15% en cierre de oportunidades
- **Satisfacción del equipo:** > 4.5/5.0 en encuestas internas

---

## 🔄 Mantenimiento y Soporte

### Logs y Debugging
```python
# logging_config.py
import logging
from pythonjsonlogger import jsonlogger

formatter = jsonlogger.JsonFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger("hubspot_cli_market")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Uso en el middleware
logger.info(
    "contact_enrichment_completed",
    extra={
        "contact_id": contact_id,
        "basket_stress": basket_stress,
        "duration_ms": duration
    }
)
```

### Alertas
```python
# alerts.py
from prometheus_client import Gauge

integration_errors = Gauge(
    'hubspot_integration_errors',
    'Errores en la integración HubSpot'
)

# Monitorear errores
try:
    await enrich_contact_with_market_intelligence(contact_id)
except Exception as e:
    integration_errors.inc()
    logger.error("enrichment_error", extra={"error": str(e), "contact_id": contact_id})
    # Enviar alerta a Slack
```

---

## 📚 Recursos Adicionales

- **Documentación HubSpot API:** https://developers.hubspot.com/docs/api/crm
- **Documentación CLI Market API:** https://cli-market.dev/docs
- **GitHub Repository:** [Repositorio de la integración]
- **Slack Support:** #cli-market-integrations

---

**Próxima versión:** Implementación de objetos personalizados para tracking histórico de inteligencia de mercado.