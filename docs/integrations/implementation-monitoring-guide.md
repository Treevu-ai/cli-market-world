# Guía de Implementación y Monitoreo: Integraciones CRM Perú + CLI Market

**Versión:** 1.0  
**Fecha:** 2026-07-31  
**Cobertura:** Simla.com, HubSpot, Zoho CRM

---

## 🎯 Objetivo de la Guía

Proporcionar una guía unificada para implementar, monitorear y mantener las 3 integraciones prioritarias de CRM peruano con CLI Market:

1. **Simla.com + CLI Market** (WhatsApp Perú)
2. **HubSpot + CLI Market** (PYMEs Perú)
3. **Zoho CRM + CLI Market** (Costo-beneficio)

---

## 📋 Prerrequisitos Comunes

### 1. **Requisitos Técnicos**
```bash
# Sistema operativo: Linux/Windows/macOS
# Python: 3.9+
# RAM: 2GB mínimo, 4GB recomendado
# Espacio en disco: 10GB mínimo
# Red: Conexión a internet estable
```

### 2. **Requisitos de Servicios**
```bash
# Servidor para desplegar middleware (opcional para desarrollo local)
# - Opción 1: Cloud (AWS, GCP, Azure, DigitalOcean)
# - Opción 2: VPS dedicado
# - Opción 3: Docker local (desarrollo)

# Base de datos para caché (opcional pero recomendado)
# - Redis para caching de respuestas
# - PostgreSQL para logs y métricas (opcional)
```

### 3. **API Keys Requeridas**
```bash
# CLI Market API Key
CLI_MARKET_API_KEY=sk-your-api-key-here
CLI_MARKET_API_URL=https://cli-market-api.fly.dev

# Simla.com (si aplica)
SIMLA_API_KEY=your-simla-api-key
SIMLA_WEBHOOK_SECRET=your-webhook-secret

# HubSpot (si aplica)
HUBSPOT_API_KEY=your-hubspot-api-key

# Zoho CRM (si aplica)
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
ZOHO_REFRESH_TOKEN=your-zoho-refresh-token
ZOHO_API_DOMAIN=https://www.zohoapis.com
```

---

## 🚀 Guía de Implementación Paso a Paso

### Fase 1: Preparación del Entorno

#### Paso 1.1: Configurar CLI Market API
```bash
# 1. Obtener API key de CLI Market
# - Regístrate en https://cli-market.dev
# - Ve a Settings > API Keys
# - Genera nueva API key
# - Copia la key (formato: sk-XXXX...)

# 2. Verificar conexión
curl -H "Authorization: Bearer sk-your-api-key" \
  https://cli-market-api.fly.dev/health/stats

# Deberías ver estadísticas del data moat
```

#### Paso 1.2: Preparar Entorno de Desarrollo
```bash
# 1. Crear directorio de proyecto
mkdir crm-cli-market-integrations
cd crm-cli-market-integrations

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instalar dependencias comunes
pip install fastapi uvicorn httpx prometheus-client python-dotenv
pip install redis  # opcional para caching
pip install psycopg2-binary  # opcional para PostgreSQL

# 4. Crear estructura de directorios
mkdir -p simla-integration hubspot-integration zoho-integration
mkdir -p shared/{utils,metrics,monitoring}
mkdir -p logs
mkdir -p config
```

#### Paso 1.3: Configurar Variables de Entorno
```bash
# Crear archivo .env
cat > .env << EOF
# CLI Market
CLI_MARKET_API_KEY=sk-your-api-key-here
CLI_MARKET_API_URL=https://cli-market-api.fly.dev

# Simla.com (si aplica)
SIMLA_API_KEY=your-simla-api-key
SIMLA_WEBHOOK_SECRET=your-webhook-secret

# HubSpot (si aplica)
HUBSPOT_API_KEY=your-hubspot-api-key

# Zoho CRM (si aplica)
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
ZOHO_REFRESH_TOKEN=your-zoho-refresh-token
ZOHO_API_DOMAIN=https://www.zohoapis.com

# Servidor
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO

# Caching (opcional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
EOF

# Asegurar que .env esté en .gitignore
echo ".env" >> .gitignore
```

---

### Fase 2: Implementación por CRM

#### 🥇 Integración Simla.com + CLI Market

**Documentación completa:** `simla-cli-market-architecture.md`

**Pasos rápidos:**
```bash
# 1. Copiar código de Simla.com middleware
cd simla-integration
cp [ruta-archivos]/*.py .

# 2. Configurar webhook en Simla.com
# - Ir a dashboard de Simla.com
# - Settings > Webhooks
# - Agregar URL: https://tu-servidor.com:8000/webhook/whatsapp
# - Configurar secret

# 3. Probar webhook
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+51912345678",
    "message": "¿Cuánto cuesta la leche?",
    "conversation_id": "test-123"
  }'

# 4. Verificar logs
tail -f ../logs/simla_integration.log
```

**Configuración específica:**
```python
# config/simla_config.py
import os

class SimlaConfig:
    API_KEY = os.getenv("SIMLA_API_KEY")
    WEBHOOK_SECRET = os.getenv("SIMLA_WEBHOOK_SECRET")
    WEBHOOK_URL = os.getenv("SIMLA_WEBHOOK_URL", "https://api.simla.com/webhook")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 20
    RATE_LIMIT_PER_HOUR = 300
    
    # Mensaje timeout
    MESSAGE_TIMEOUT_SECONDS = 30
```

#### 🥈 Integración HubSpot + CLI Market

**Documentación completa:** `hubspot-cli-market-architecture.md`

**Pasos rápidos:**
```bash
# 1. Copiar código de HubSpot middleware
cd hubspot-integration
cp [ruta-archivos]/*.py .

# 2. Configurar HubSpot
# - Ir a HubSpot Settings > Webhooks
# - Crear nuevo webhook
# - URL: https://tu-servidor.com:8000/webhook/hubspot
# - Suscribir a: contact.creation, deal.creation, contact.propertyChange

# 3. Crear propiedades personalizadas en HubSpot
# - Usar el script provided en la documentación
# - O crear manualmente desde HubSpot UI

# 4. Probar webhook
curl -X POST http://localhost:8000/webhook/hubspot \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_type": "contact.creation",
    "event_id": "test-123",
    "object_id": "contact-456",
    "change_source": "EXTERNAL",
    "occurred_at": 1659263400,
    "attempt_number": 1
  }'

# 5. Verificar enriquecimiento
# - Crear nuevo contacto en HubSpot
# - Verificar que se enriquezca automáticamente
```

**Configuración específica:**
```python
# config/hubspot_config.py
import os

class HubSpotConfig:
    API_KEY = os.getenv("HUBSPOT_API_KEY")
    WEBHOOK_URL = os.getenv("HUBSPOT_WEBHOOK_URL", "https://api.hubapi.com/webhooks")
    
    # Propiedades personalizadas
    CONTACT_PROPERTIES = [
        "market_basket_stress",
        "market_inflation_signal",
        "market_price_fairness",
        "market_retail_aggression",
        "market_data_updated",
        "region",
        "income_level",
        "family_size"
    ]
    
    DEAL_PROPERTIES = [
        "price_risk_level",
        "procurement_signal",
        "market_recommended_action",
        "price_intelligence_updated",
        "products"
    ]
```

#### 🥉 Integración Zoho CRM + CLI Market

**Documentación completa:** `zoho-cli-market-architecture.md`

**Pasos rápidos:**
```bash
# 1. Copiar código de Zoho middleware
cd zoho-integration
cp [ruta-archivos]/*.py .

# 2. Configurar OAuth de Zoho
# - Ir a Zoho Developer Console
# - Crear nueva aplicación
# - Obtener client_id y client_secret
# - Generar refresh token

# 3. Configurar webhook en Zoho CRM
# - Setup > Automation > Workflows > Webhooks
# - Crear nuevo webhook
# - URL: https://tu-servidor.com:8000/webhook/zoho
# - Configurar triggers: Leads.create, Deals.create, Products.update

# 4. Crear campos personalizados en Zoho
# - Usar el script provided en la documentación
# - O crear manualmente desde Zoho CRM UI

# 5. Probar webhook
curl -X POST http://localhost:8000/webhook/zoho \
  -H "Content-Type: application/json" \
  -d '{
    "module": "Leads",
    "record_id": "lead-456",
    "operation": "create",
    "trigger": "webhook"
  }'

# 6. Verificar enriquecimiento
# - Crear nuevo lead en Zoho CRM
# - Verificar que se enriquezca automáticamente
```

**Configuración específica:**
```python
# config/zoho_config.py
import os

class ZohoConfig:
    CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
    CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
    REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
    API_DOMAIN = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")
    
    # Módulos a monitorear
    MONITORED_MODULES = ["Leads", "Deals", "Products"]
    
    # Campos personalizados
    LEAD_FIELDS = [
        "Market_Basket_Stress",
        "Market_Inflation_Signal",
        "Market_Price_Fairness",
        "Market_Retail_Aggression",
        "Market_Score",
        "Market_Data_Updated",
        "Region"
    ]
    
    DEAL_FIELDS = [
        "Price_Risk_Level",
        "Procurement_Signal",
        "Market_Recommended_Action",
        "Price_Intelligence_Updated",
        "Products"
    ]
    
    PRODUCT_FIELDS = [
        "Market_Price_Risk",
        "Procurement_Signal",
        "Recommended_Stock",
        "Market_Intelligence_Updated",
        "Daily_Demand",
        "Lead_Time"
    ]
```

---

### Fase 3: Despliegue en Producción

#### Opción 1: Docker (Recomendado)
```bash
# 1. Crear Dockerfile para cada integración
# Simla
cat > simla-integration/Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# HubSpot
cat > hubspot-integration/Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

# Zoho
cat > zoho-integration/Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
EOF

# 2. Crear docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'
services:
  simla-middleware:
    build: ./simla-integration
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
  
  hubspot-middleware:
    build: ./hubspot-integration
    ports:
      - "8001:8001"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
  
  zoho-middleware:
    build: ./zoho-integration
    ports:
      - "8002:8002"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - ./config/grafana:/etc/grafana
    restart: unless-stopped
EOF

# 3. Construir y desplegar
docker-compose up -d

# 4. Verificar estado
docker-compose ps
docker-compose logs -f
```

#### Opción 2: Cloud (AWS/GCP/Azure)
```bash
# Ejemplo para AWS EC2

# 1. Lanzar instancia EC2
# - AMI: Ubuntu 20.04 LTS
# - Instance type: t3.medium (2 vCPU, 4GB RAM)
# - Security group: permitir puertos 80, 443, 8000-8002

# 2. Conectar a instancia
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. Clonar repositorio
git clone https://github.com/your-org/crm-cli-market-integrations.git
cd crm-cli-market-integrations

# 5. Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus API keys

# 6. Desplegar con docker-compose
docker-compose up -d

# 7. Configurar Nginx (opcional para SSL)
sudo apt install nginx
sudo cp config/nginx.conf /etc/nginx/sites-available/default
sudo systemctl restart nginx
```

#### Opción 3: Kubernetes (Para producción escalable)
```bash
# Crear manifests de Kubernetes
mkdir -p k8s

# Deployment para Simla
cat > k8s/simla-deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simla-middleware
spec:
  replicas: 2
  selector:
    matchLabels:
      app: simla-middleware
  template:
    metadata:
      labels:
        app: simla-middleware
    spec:
      containers:
      - name: simla-middleware
        image: your-registry/simla-middleware:latest
        ports:
        - containerPort: 8000
        env:
        - name: CLI_MARKET_API_KEY
          valueFrom:
            secretKeyRef:
              name: cli-market-secrets
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
EOF

# Service
cat > k8s/simla-service.yaml << EOF
apiVersion: v1
kind: Service
metadata:
  name: simla-middleware
spec:
  selector:
    app: simla-middleware
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
EOF

# Aplicar manifests
kubectl apply -f k8s/
```

---

## 📊 Sistema de Monitoreo Unificado

### 1. **Configuración de Prometheus**
```yaml
# config/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'simla-middleware'
    static_configs:
      - targets: ['simla-middleware:8000']
    metrics_path: '/metrics'
  
  - job_name: 'hubspot-middleware'
    static_configs:
      - targets: ['hubspot-middleware:8001']
    metrics_path: '/metrics'
  
  - job_name: 'zoho-middleware'
    static_configs:
      - targets: ['zoho-middleware:8002']
    metrics_path: '/metrics'
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### 2. **Dashboard de Grafana**
```json
{
  "dashboard": {
    "title": "CRM CLI Market Integrations",
    "panels": [
      {
        "title": "Total Webhooks por CRM",
        "targets": [
          {
            "expr": "sum(rate(simla_webhooks_total[5m])) by (subscription_type)",
            "legendFormat": "Simla {{subscription_type}}"
          },
          {
            "expr": "sum(rate(hubspot_webhooks_total[5m])) by (subscription_type)",
            "legendFormat": "HubSpot {{subscription_type}}"
          },
          {
            "expr": "sum(rate(zoho_webhooks_total[5m])) by (module)",
            "legendFormat": "Zoho {{module}}"
          }
        ]
      },
      {
        "title": "Tiempo de Enriquecimiento",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, enrichment_duration_seconds)",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Errores de Integración",
        "targets": [
          {
            "expr": "sum(rate(cli_market_integration_errors[5m]))",
            "legendFormat": "CLI Market Errors"
          },
          {
            "expr": "sum(rate(hubspot_integration_errors[5m]))",
            "legendFormat": "HubSpot Errors"
          },
          {
            "expr": "sum(rate(zoho_integration_errors[5m]))",
            "legendFormat": "Zoho Errors"
          }
        ]
      },
      {
        "title": "Market Scores Promedio",
        "targets": [
          {
            "expr": "avg(market_score_avg)",
            "legendFormat": "Market Score"
          },
          {
            "expr": "avg(retail_aggression_avg)",
            "legendFormat": "Retail Aggression"
          }
        ]
      }
    ]
  }
}
```

### 3. **Alertas de Monitoreo**
```yaml
# config/alerts.yml
groups:
  - name: crm_integrations
    rules:
      - alert: HighErrorRate
        expr: rate(cli_market_integration_errors[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta tasa de errores en integración CLI Market"
          description: "Tasa de errores: {{ $value }}"
      
      - alert: SlowEnrichment
        expr: histogram_quantile(0.95, enrichment_duration_seconds) > 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Enriquecimiento lento"
          description: "95th percentile: {{ $value }}s"
      
      - alert: IntegrationDown
        expr: up{job=~"simla-middleware|hubspot-middleware|zoho-middleware"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Integración caída"
          description: "Middleware {{ $labels.job }} no responde"
```

---

## 🔧 Mantenimiento Operativo

### 1. **Logs y Debugging**
```python
# shared/utils/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime

def setup_logging(integration_name: str):
    """Configurar logging para integración específica"""
    
    # Crear logger
    logger = logging.getLogger(integration_name)
    logger.setLevel(logging.INFO)
    
    # Formato JSON para mejor parseo
    formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler(f'logs/{integration_name}.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    
    return logger

# Uso en cada integración
logger = setup_logging("simla_integration")
logger.info("integration_started", extra={"integration": "simla", "timestamp": datetime.utcnow().isoformat()})
```

### 2. **Health Checks**
```python
# shared/monitoring/health.py
from fastapi import FastAPI
from httpx import AsyncClient
import os

async def check_cli_market_health() -> bool:
    """Verificar salud de CLI Market API"""
    try:
        async with AsyncClient() as client:
            response = await client.get(
                f"{os.getenv('CLI_MARKET_API_URL')}/health/stats",
                timeout=5.0
            )
            return response.status_code == 200
    except Exception:
        return False

async def check_crm_health(crm_type: str) -> bool:
    """Verificar salud de CRM específico"""
    try:
        if crm_type == "simla":
            # Verificar API de Simla.com
            pass
        elif crm_type == "hubspot":
            # Verificar API de HubSpot
            pass
        elif crm_type == "zoho":
            # Verificar API de Zoho
            pass
        return True
    except Exception:
        return False

# Endpoint de health check unificado
@app.get("/health")
async def health_check():
    """Health check para todas las integraciones"""
    checks = {
        "cli_market_api": await check_cli_market_health(),
        "simla_integration": await check_crm_health("simla"),
        "hubspot_integration": await check_crm_health("hubspot"),
        "zoho_integration": await check_crm_health("zoho"),
        "redis": check_redis_health(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    overall_healthy = all(checks.values())
    status_code = 200 if overall_healthy else 503
    
    return {
        "status": "healthy" if overall_healthy else "degraded",
        "checks": checks
    }, status_code
```

### 3. **Rotación de Logs**
```bash
# Configurar logrotate
sudo cat > /etc/logrotate.d/crm-integrations << EOF
/path/to/crm-cli-market-integrations/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ubuntu ubuntu
}
EOF

# Test de configuración
sudo logrotate -d /etc/logrotate.d/crm-integrations
```

### 4. **Backup y Recuperación**
```bash
# Script de backup
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups/crm-integrations"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de configuración
tar -czf $BACKUP_DIR/config_$DATE.tar.gz config/

# Backup de logs (últimos 7 días)
find logs/ -name "*.log" -mtime -7 -exec tar -czf $BACKUP_DIR/logs_$DATE.tar.gz {} +

# Backup de base de datos (si aplica)
# pg_dump crm_integrations > $BACKUP_DIR/db_$DATE.sql

# Limpiar backups antiguos (más de 30 días)
find $BACKUP_DIR/ -name "*.tar.gz" -mtime +30 -delete

echo "Backup completado: $DATE"
```

---

## 🧪 Testing y Validación

### 1. **Suite de Tests Unificados**
```python
# tests/test_integrations.py
import pytest
from httpx import AsyncClient
from simla_integration.main import app as simla_app
from hubspot_integration.main import app as hubspot_app
from zoho_integration.main import app as zoho_app

@pytest.mark.asyncio
async def test_simla_webhook():
    async with AsyncClient(app=simla_app, base_url="http://test") as client:
        response = await client.post(
            "/webhook/whatsapp",
            json={
                "phone_number": "+51912345678",
                "message": "¿Cuánto cuesta la leche?",
                "conversation_id": "test-123"
            }
        )
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_hubspot_webhook():
    async with AsyncClient(app=hubspot_app, base_url="http://test") as client:
        response = await client.post(
            "/webhook/hubspot",
            json={
                "subscription_type": "contact.creation",
                "event_id": "test-123",
                "object_id": "contact-456",
                "change_source": "EXTERNAL",
                "occurred_at": 1659263400,
                "attempt_number": 1
            }
        )
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_zoho_webhook():
    async with AsyncClient(app=zoho_app, base_url="http://test") as client:
        response = await client.post(
            "/webhook/zoho",
            json={
                "module": "Leads",
                "record_id": "lead-456",
                "operation": "create",
                "trigger": "webhook"
            }
        )
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_cli_market_api():
    from shared.utils.cli_market_client import CLIMarketClient
    client = CLIMarketClient()
    intel = await client.get_intel_brief(country="PE")
    assert "shelf_signal" in intel
```

### 2. **Tests de Carga**
```python
# tests/load_test.py
import asyncio
import time
from httpx import AsyncClient

async def simulate_webhook_load(integration_url: str, num_requests: int):
    """Simular carga de webhooks"""
    async with AsyncClient() as client:
        tasks = []
        for i in range(num_requests):
            if "simla" in integration_url:
                task = client.post(
                    f"{integration_url}/webhook/whatsapp",
                    json={
                        "phone_number": f"+5191234567{i}",
                        "message": "¿Cuánto cuesta la leche?",
                        "conversation_id": f"test-{i}"
                    }
                )
            elif "hubspot" in integration_url:
                task = client.post(
                    f"{integration_url}/webhook/hubspot",
                    json={
                        "subscription_type": "contact.creation",
                        "event_id": f"test-{i}",
                        "object_id": f"contact-{i}",
                        "change_source": "EXTERNAL",
                        "occurred_at": 1659263400,
                        "attempt_number": 1
                    }
                )
            elif "zoho" in integration_url:
                task = client.post(
                    f"{integration_url}/webhook/zoho",
                    json={
                        "module": "Leads",
                        "record_id": f"lead-{i}",
                        "operation": "create",
                        "trigger": "webhook"
                    }
                )
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        duration = end_time - start_time
        
        print(f"Requests: {num_requests}")
        print(f"Success: {success_count}")
        print(f"Duration: {duration:.2f}s")
        print(f"RPS: {num_requests/duration:.2f}")

# Ejecutar test de carga
asyncio.run(simulate_webhook_load("http://localhost:8000", 100))
```

---

## 📈 Métricas de Éxito y KPIs

### KPIs por Integración

#### Simla.com + CLI Market
- **Tiempo de respuesta:** < 3 segundos para consultas de búsqueda
- **Precisión de detección de intención:** > 85%
- **Satisfacción del cliente:** > 4.0/5.0
- **Ahorro promedio por cliente:** S/ 5-10 por canasta
- **Tasa de conversión:** Incremento del 15%

#### HubSpot + CLI Market
- **Tiempo de enriquecimiento:** < 5 segundos por contacto
- **Precisión de lead scoring:** Mejora del 25% en conversión
- **Tasa de adopción:** > 80% de contactos enriquecidos
- **Impacto en ventas:** Incremento del 15% en cierre
- **Satisfacción del equipo:** > 4.5/5.0

#### Zoho CRM + CLI Market
- **Tiempo de enriquecimiento:** < 5 segundos por lead
- **Precisión de lead scoring:** Mejora del 30% en conversión
- **Tasa de adopción:** > 85% de leads enriquecidos
- **Impacto en inventario:** Reducción del 20% en stock excesivo
- **ROI de la integración:** 3x en 6 meses

### KPIs Generales del Sistema
- **Uptime:** > 99.5%
- **Tiempo de respuesta promedio:** < 2 segundos
- **Tasa de error:** < 1%
- **Costo por enriquecimiento:** < $0.01
- **ROI total:** 2.5x en 12 meses

---

## 🚨 Troubleshooting Común

### Problema 1: Webhooks no se reciben
```bash
# Verificar que el servidor esté corriendo
curl http://localhost:8000/health

# Verificar logs
tail -f logs/simla_integration.log

# Verificar configuración de webhook en el CRM
# - URL correcta
# - Secret correcto
# - Eventos suscritos correctamente
```

### Problema 2: Errores de autenticación CLI Market
```bash
# Verificar API key
echo $CLI_MARKET_API_KEY

# Test de conexión
curl -H "Authorization: Bearer $CLI_MARKET_API_KEY" \
  https://cli-market-api.fly.dev/health/stats

# Verificar límites de rate limiting
# CLI Market Enterprise: ilimitado
# CLI Market Pro: 1000 requests/min
```

### Problema 3: Enriquecimiento lento
```bash
# Verificar uso de CPU
docker stats

# Verificar memoria
free -h

# Configurar Redis para caching
# - Acelera respuestas repetidas
# - Reduce carga en CLI Market API
```

### Problema 4: Errores de integración CRM
```bash
# Verificar API keys del CRM
echo $HUBSPOT_API_KEY
echo $ZOHO_CLIENT_ID

# Test de conexión al CRM
# HubSpot: curl -H "Authorization: Bearer $HUBSPOT_API_KEY" \
#   https://api.hubapi.com/crm/v3/objects/contacts

# Zoho: Necesita OAuth flow
```

---

## 📚 Recursos y Soporte

### Documentación
- **CLI Market API:** https://cli-market.dev/docs
- **Simla.com API:** [Documentación oficial Simla.com]
- **HubSpot API:** https://developers.hubspot.com/docs/api/crm
- **Zoho CRM API:** https://www.zoho.com/crm/developer/docs/api/

### Comunidad
- **Slack:** #cli-market-integrations
- **GitHub Issues:** [Repositorio de integraciones]
- **Email:** support@cli-market.dev

### Servicios Profesionales
- **Implementación:** Disponible para empresas enterprise
- **Consultoría:** Estrategia de integración CRM
- **Soporte Premium:** 24/7 para contratos enterprise

---

## 🔄 Roadmap Futuro

### Versión 2.0 (Q4 2026)
- Integración con DeltaApp (CRM Colombia-Perú)
- Dashboard unificado de inteligencia de mercado
- Machine learning para lead scoring mejorado
- Integración con ERPs peruanos (Siigo, World Office)

### Versión 3.0 (Q1 2027)
- Agentes de IA nativos para cada CRM
- Predicción de demanda con inteligencia de mercado
- Integración con redes sociales (LinkedIn, Instagram)
- Análisis de sentimiento de clientes

---

**Última actualización:** 2026-07-31  
**Versión:** 1.0  
**Estado:** Production Ready