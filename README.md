# Coretas Campaign Auto-Builder Dashboard

A mini full-stack application demonstrating a dashboard-first campaign auto-builder across Google Ads, Meta, and Amazon Ads.

## Setup

### Backend

```bash
cd backend
pip install -e .
cp .env.example .env   # Optional: add OPENAI_API_KEY for real planning
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Optional. If set, planner uses GPT. Otherwise uses mock. |
| `PLANNER_MODEL` | OpenAI model (default: gpt-4o-mini) |
| `GOOGLE_ADS_*` | Google Ads credentials (sandbox/mock if empty) |
| `META_ACCESS_TOKEN` | Meta API token (mock if empty) |
| `AMAZON_*` | Amazon Ads credentials (mock if empty) |

## Real vs Mocked APIs

- **Planner**: Uses OpenAI when `OPENAI_API_KEY` is set; otherwise returns a deterministic mock plan.
- **Google Ads / Meta / Amazon**: All platform APIs are mocked. When credentials are missing, campaigns are created in-memory with mock IDs. Metrics are simulated.

## Planner & Agent Design

### Flow

1. **Normalize input** – Pydantic validates objective, budget, categories.
2. **Generate plan** – LLM (or mock) produces structured JSON.
3. **Validate** – Schema check, character limits from `platform_policies.md`.
4. **Retry** – Up to 3 attempts with exponential backoff on parse/validation errors.
5. **Fallback** – If all fail, return a safe mock plan.

### Guardrails

- Max 5 planning steps.
- Schema validation via Pydantic.
- Policy file (`platform_policies.md`) injected into the prompt for character limits.
- Graceful degradation when the model fails.

## Optimization Logic

- **Low CTR detection**: Flags campaigns with CTR < 1% and spend > $20.
- **Cross-platform reallocation**: Compares CTR by platform; suggests moving budget from worst to best when ratio > 1.5x.
- Output is structured; human approval required before any action.

## Platform Endpoints (Mocked)

- Google Ads Performance Max: `create_google_campaign` → mock ID
- Meta Shopping: `create_meta_campaign` → mock ID  
- Amazon Sponsored Brands: `create_amazon_campaign` → mock ID

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────►│   FastAPI    │────►│   SQLite    │
│   Frontend  │     │   /api       │     │   DB        │
└─────────────┘     └──────┬──────┘     └─────────────┘
       │                   │
       │                   ├──► Planner Agent ──► OpenAI (or mock)
       │                   │
       │                   ├──► Platform Mappers ──► Google / Meta / Amazon payloads
       │                   │
       │                   └──► Reporting + Optimization ──► Mock metrics + suggestions
       │
       └──► Vite dev server (proxy /api → :8000)
```

See [architecture.svg](architecture.svg) for the diagram. To generate a PNG, open the SVG in a browser and screenshot, or use `convert architecture.svg architecture.png` (ImageMagick).
