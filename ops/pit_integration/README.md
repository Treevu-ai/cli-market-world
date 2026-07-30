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
python ops/market_evidence_package.py --mode mock --merge-ficha
```

Salidas:

- `ops/generated/pit/last-market-evidence-package.json`
- `ops/generated/pit/last-ficha-merged.json` (con `--merge-ficha`)
- `ops/generated/pit/last-ficha-merged.md`

### Live (API CLI Market)

```bash
export MARKET_API_URL=https://cli-market-api.fly.dev
export MARKET_API_TOKEN=...   # recomendado para /v1/intel/*

python ops/market_evidence_package.py --mode live \
  --query "arandanos" --country PE --pit-run-id demo-run-1 --merge-ficha
```

### Tests

```bash
python -m pytest tests/test_market_evidence_package.py -q
```

## Qué es / qué no es

| Sí | No |
|----|-----|
| Schema v0.1 del Market Evidence Package | Research runs / papers (PIT) |
| Merge delgado ficha stub + góndola | Endpoint prod `/v1/intel/market-evidence` (fase 4) |
| Llamadas live a search/compare/intel | Unificar auth PIT ↔ CLI Market |

Cuando PIT exponga ficha real, el consumidor solo necesita:

1. Llamar este script o importar `build_package` / `fetch_live_package` / `merge_ficha`
2. Adjuntar `market_evidence` al payload de ficha / PDF
