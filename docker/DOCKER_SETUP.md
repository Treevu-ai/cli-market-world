# CLI Market Docker Setup

## Setup rápido (con auth persistente)

### 1. Construir la imagen
```bash
docker build -t cli-market:latest .
```

### 2. Opción A: Correr con docker-compose (desarrollo)
```bash
docker-compose up -d
docker-compose exec market-cli market search "leche" --country PE
```

### 3. Opción B: Correr con volumen nombrado (producción)
```bash
docker run -it --name cli-market \
  -v market-creds:/root/.market \
  -v market-cache:/root/.cache \
  -e MARKET_API_URL=https://cli-market-api.fly.dev \
  cli-market:latest \
  market init
```

### 4. Reutilizar credenciales en futuros contenedores
```bash
# El volumen persiste, así que nuevos contenedores usan las mismas credenciales
docker run -it \
  -v market-creds:/root/.market \
  -v market-cache:/root/.cache \
  cli-market:latest \
  market search "arroz" --country PE
```

## Con Token Pre-autenticado

Si tienes el token (`sk-...`) ya guardado:

```bash
docker run -it \
  -e MARKET_API_TOKEN=[ROTATED 2026-07-17 — MARKET_API_TOKEN] \
  -v market-creds:/root/.market \
  cli-market:latest \
  market search "leche" --country PE
```

## Archivo .env para docker-compose

Crea un `.env` en la raíz:
```
MARKET_API_TOKEN=[ROTATED 2026-07-17 — MARKET_API_TOKEN]
MARKET_AGENT_ID=cli_7a87d3b3297442c2988c
```

Luego:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## MCP en Docker (para Cursor/Claude/Windsurf)

Servicio MCP que expondrá las 31 herramientas:
```bash
docker-compose -f docker-compose.prod.yml up market-mcp-server
```

Conecta en tu IDE apuntando a `localhost` (si usas Docker Desktop).

## Volúmenes persistentes

| Volumen | Propósito |
|---------|-----------|
| `market-credentials` | Almacena credenciales CLI (`~/.market`) |
| `market-cache` | Cache de búsquedas y precios |

Verifica con:
```bash
docker volume ls
docker volume inspect market-credentials
```

## Ejecutar comandos sin entrar al contenedor

```bash
# Búsqueda
docker-compose exec market-cli market search "leche" --country PE

# Comparativa
docker-compose exec market-cli market compare "aceite" --country AR

# Carrito
docker-compose exec market-cli market cart

# Doctor (verificar salud)
docker-compose exec market-cli market doctor
```

## Troubleshooting

**"No authentication found"**: Verifica que el volumen persiste:
```bash
docker volume inspect market-credentials
```

**"API timeout"**: Aumenta timeout en requests:
```bash
docker run -it \
  -e MARKET_API_URL=https://cli-market-api.fly.dev \
  -e HTTPX_TIMEOUT=60 \
  -v market-creds:/root/.market \
  cli-market:latest \
  market doctor
```

**Rebuild después de cambios**:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
