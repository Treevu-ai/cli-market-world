# CLI Market — Secrets Inventory

> Last updated: 2026-06-22  
> Scope: cli-market-world + cli-market-core (runtime secrets)

## Groups

### 1. Database (`database`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `DATABASE_URL` | prod | world, core | PostgreSQL connection string. Railway auto-injects. |
| `INDEX_DATABASE_URL` | optional | world | Separate Postgres for index. Falls back to `DATABASE_URL`. |
| `PG_SSL_MODE` | optional | core | Default `prefer`. Override for stricter SSL. |

### 2. PayPal (`payments-paypal`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `PAYPAL_CLIENT_ID` | prod | core | REST API client ID |
| `PAYPAL_CLIENT_SECRET` | prod | core | REST API secret |
| `PAYPAL_WEBHOOK_ID` | prod | core | For webhook signature verification |
| `PAYPAL_SANDBOX` | always | core, world | `true` for sandbox, `false` for production |
| `PAYPAL_PLAN_ID` | prod | core | Pro monthly subscription plan |
| `PAYPAL_STARTER_PLAN_ID` | prod | core, world | Starter subscription plan |
| `PAYPAL_PRO_FOUNDING_PLAN_ID` | prod | core | Founding member plan |
| `PAYPAL_PRO_ANNUAL_PLAN_ID` | prod | core | Annual plan |
| `PAYPAL_E2E_API_KEY` | CI only | world | E2E test API key |

### 3. MercadoPago (`payments-mercadopago`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `MERCADOPAGO_ACCESS_TOKEN` | prod | core | Generic access token (sandbox or prod) |
| `MERCADOPAGO_ACCESS_TOKEN_PRODUCTION` | prod | core | Explicit production token |
| `MERCADOPAGO_ACCESS_TOKEN_PROD` | prod | core | Alias for production token |
| `MERCADOPAGO_PUBLIC_KEY` | optional | core | For client-side tokenization |
| `MERCADOPAGO_SANDBOX` | always | core | `true`/`false` |
| `MERCADOPAGO_WEBHOOK_URL` | prod | core | Notification URL |
| `MERCADOPAGO_WEBHOOK_SECRET` | prod | core | HMAC signature secret |
| `MP_SANDBOX` | optional | core | Legacy alias for `MERCADOPAGO_SANDBOX` |

### 4. Other Payment Providers (`payments-other`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `LEMON_API_KEY` | optional | core | Lemon Cash (Argentina crypto) |
| `LEMON_API_URL` | optional | core | Lemon endpoint override |
| `WISE_API_TOKEN` | optional | core | Wise international transfers |
| `WISE_PROFILE_ID` | optional | core | Wise profile ID |
| `WISE_WEBHOOK_SECRET` | optional | core | Wise webhook verification |
| `WISE_PAY_ME_URL` | optional | world | Pay.me link for QR |
| `CHECKOUT_WEBHOOK_SECRET` | prod | world, core | Generic checkout webhook HMAC |

### 5. Auth & API Keys (`auth`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `MARKET_API_TOKEN` | always | world | Default admin bearer token |
| `MARKET_ADMIN_PASSWORD` | prod | world | Admin panel password |
| `MARKET_USER_TOKEN` | optional | world | User-level token override |

### 6. Railway Infrastructure (`infra-railway`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `RAILWAY_ENVIRONMENT` | auto | world | Injected by Railway (`production`/`staging`) |
| `RAILWAY_API_TOKEN` | ops | world | For Railway API calls (redeploy, etc.) |
| `RAILWAY_PROJECT_ID` | ops | world | Project identifier |
| `RAILWAY_ENVIRONMENT_ID` | ops | world | Environment identifier |
| `RAILWAY_API_SERVICE_ID` | ops | world | API service identifier |
| `RAILWAY_PROJECT_TOKEN` | ops | world | Alternative project-level token |
| `PORT` | auto | world | Injected by Railway |

### 7. Slack (`notifications-slack`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `SLACK_BOT_TOKEN` | prod | world | Bot OAuth token (xoxb-) |
| `SLACK_SIGNING_SECRET` | prod | world | For Slack event verification |
| `SLACK_WEBHOOK_BITACORA` | prod | world | Ops log channel webhook |
| `SLACK_WEBHOOK_COMMAND_CONTROL` | prod | world | Daily metrics webhook |
| `SLACK_WEBHOOK_FUNNEL` | prod | world | Funnel events webhook |
| `SLACK_WEBHOOK_CLI_MARKET_PRO` | prod | world | Pro activations webhook |
| `SLACK_WEBHOOK_CEO_METRICS` | prod | world | Executive metrics webhook |
| `SLACK_WEBHOOK_PUBLICACIONES` | prod | world | Content publish webhook |
| `SLACK_WEBHOOK_URL` | optional | world | Generic fallback webhook |
| `SLACK_CHANNEL_*` | prod | world | 15+ channel IDs for routing |

### 8. External APIs (`external-apis`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | prod | core | Claude API for Intel Agent |
| `PEPYTECH_API_KEY` | optional | world | PyPI download stats |
| `PEPY_API_KEY` | optional | world | Alternative PyPI stats key |
| `MINIMAX_API_KEY` | optional | core | Minimax connector |
| `MINIMAX_GROUP_ID` | optional | core | Minimax group |
| `TELEGRAM_BOT_TOKEN` | optional | world | Telegram notifications |

### 9. Email / SMTP (`email`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `SMTP_HOST` | prod | core | SMTP server |
| `SMTP_PORT` | prod | core | SMTP port |
| `SMTP_USER` | prod | core | SMTP username |
| `SMTP_PASSWORD` | prod | core | SMTP password |
| `SMTP_USE_TLS` | optional | core | Default true |
| `GMAIL_IMAP_USER` | optional | core | For draft monitoring |
| `GMAIL_IMAP_PASSWORD` | optional | core | IMAP password |
| `BILLING_FROM_EMAIL` | optional | core | Billing email sender |
| `BILLING_NOTIFY_EMAIL` | optional | core | Billing notification recipient |
| `MARKET_OPS_EMAIL` | optional | core | Ops notification email |

### 10. GitHub (`github`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `GITHUB_TOKEN` | build | world | For pip install cli-market-index |
| `GH_PAT` | build | world | Alternative PAT name |
| `GH_TOKEN` | build | world | Alternative PAT name |

### 11. Pricing Config (`pricing`)
| Variable | Required | Where | Notes |
|---|---|---|---|
| `STARTER_PRICE_USD` | optional | core | Override default $24 |
| `PRO_PRICE_USD` | optional | core | Override default $39 |
| `PRO_FOUNDING_PRICE_USD` | optional | core | Override default $29 |
| `PRO_ANNUAL_PRICE_USD` | optional | core | Override default $390 |
| `PRO_PEN_PER_USD` | optional | world | PEN/USD rate for local pricing |

## Deprecated (remove from env)

| Variable | Reason |
|---|---|
| `PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS` | Security fix: now always blocked in prod (PR #297) |

## Total: ~120 unique variables

### Recommended Railway Variable Groups
```
database          → DATABASE_URL, INDEX_DATABASE_URL, PG_SSL_MODE
payments-paypal   → PAYPAL_* (8 vars)
payments-mp       → MERCADOPAGO_*, MP_* (10 vars)
payments-other    → LEMON_*, WISE_*, CHECKOUT_WEBHOOK_SECRET
auth              → MARKET_API_TOKEN, MARKET_ADMIN_PASSWORD
slack             → SLACK_* (25+ vars)
external-apis     → ANTHROPIC_API_KEY, PEPY_*, MINIMAX_*, TELEGRAM_*
email             → SMTP_*, GMAIL_*, BILLING_*
pricing           → *_PRICE_USD, PRO_PEN_PER_USD
```
