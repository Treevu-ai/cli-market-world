# PIT ↔ CLI Market — thin integration

Contrato: [`docs/PIT-INTEGRATION.md`](../../docs/PIT-INTEGRATION.md).

## Layout

```
ops/pit_integration/
  README.md                 # este archivo
  mocks/
    market_evidence_package.example.json
    pit_ficha_stub.example.json
    ficha_merged.example.json
ops/market_evidence_package.py   # builder + CLI
ops/generated/pit/               # salidas locales (gitignored si aplica)
```

## Comandos

### Mock (sin red)

```bash
python ops/market_evidence_package.py --mode mock
python ops/market_evidence_package.py --mode mock --merge-ficha --write-trace
```

Salidas:

- `ops/generated/pit/last-market-evidence-package.json`
- `ops/generated/pit/last-ficha-merged.json` (con `--merge-ficha`)
- `ops/generated/pit/last-ficha-merged.md`
- `ops/generated/pit/last-trace-receipt.json` (fase 3; también auto si hay `--pit-run-id` o merge)

### Live (API CLI Market)

```bash
export MARKET_API_URL=https://cli-market-api.fly.dev
export MARKET_API_TOKEN=...   # recomendado para /v1/intel/*

python ops/market_evidence_package.py --mode live \
  --query "arandanos" --country PE --pit-run-id demo-run-1 --merge-ficha --write-trace
```

### PIT (fase 3 — best-effort)

```bash
export PIT_API_URL=https://cli-market-pit-backend.fly.dev
export PIT_API_TOKEN=...   # opcional; sin token se registra 401 en el receipt

python ops/market_evidence_package.py --mode mock \
  --create-pit-run --merge-ficha --write-trace \
  --query "blueberry functional beverage" --country PE
```

Módulos:

- `ops/pit_integration/trace.py` — receipt de auditoría
- `ops/pit_integration/pit_client.py` — health / research-runs / ficha

### Tests

```bash
python -m pytest tests/test_market_evidence_package.py tests/test_pit_phase3_trace.py -q
```

## Qué es / qué no es

| Sí | No |
|----|-----|
| Schema v0.1 del Market Evidence Package | Research runs / papers (PIT) |
| Merge delgado ficha stub + góndola | Endpoint prod `/v1/intel/market-evidence` (fase 4) |
| Llamadas live a search/compare/intel | Unificar auth PIT ↔ CLI Market |
| Trace receipt package_id ↔ pit_run_id | Persistencia forzada del ref dentro de PIT (auth/API del lado PIT) |

Cuando PIT exponga ficha real, el consumidor solo necesita:

1. Llamar este script o importar `build_package` / `fetch_live_package` / `merge_ficha` / `build_trace_receipt`
2. Adjuntar `market_evidence` (+ opcionalmente el receipt) al payload de ficha / PDF
