# AP RTGS Dashboard

Real-Time Governance Dashboard Modules for Andhra Pradesh — AI-powered analytics that plug into the AWARE 2.0 data lake. Built for the CM/Secretary level to monitor scheme delivery, department performance, and anomalies across 13 AP districts.

## Features

- **Natural Language Query**: Ask governance questions in plain English — powered by Claude (`claude-haiku-4-5-20251001`) with a rule-based fallback
- **Executive Dashboard**: Budget utilization, active beneficiaries, pending applications, delayed schemes — at a glance
- **Scheme Status**: Filter by district, type (pension/housing/agriculture/health), delay status
- **Anomaly Detection**: Auto-flag departments with unusual spending or stalled file movements
- **AWARE 2.0 Mock Data**: 8 AP departments, 10 schemes across 8 districts seeded with realistic figures

## Quickstart — Docker

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env — set ANTHROPIC_API_KEY to a real key to enable Claude NL parsing
# Without a key, the rule-based fallback handles all queries

# 2. Launch
docker compose up --build

# Frontend:  http://localhost:3007
# API docs:  http://localhost:8007/docs
# DB:        localhost:5439 (user: rtgs, pass: changeme, db: rtgs_dashboard)
```

The first request to `/api/v1/analytics/executive-summary` auto-seeds the database.

## Quickstart — Local (no Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt

# SQLite for local dev (no Postgres needed)
export DATABASE_URL=sqlite+aiosqlite:///./rtgs_dev.db
export ANTHROPIC_API_KEY=sk-ant-your-key-here   # optional

uvicorn app.main:app --reload --port 8000
```

Then seed: `curl -X POST http://localhost:8000/api/v1/analytics/seed`

### Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
# Open http://localhost:3000
```

## Running Tests

Tests use SQLite in-memory — no Postgres or Claude API key required.

```bash
cd backend
python -m pytest tests/ -v
# 14 tests, all passing
```

## API Reference

### Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/analytics/executive-summary` | KPI summary for CM/Secretary view |
| GET | `/api/v1/analytics/district-stats` | Per-district scheme load and pending count |
| POST | `/api/v1/analytics/seed` | Seed database with AP mock data (idempotent) |

### Departments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/departments/` | List departments (filter: `category`, `has_anomaly`) |
| POST | `/api/v1/departments/run-anomaly-detection` | Run anomaly scan and update flags |
| GET | `/api/v1/departments/anomalies` | Current anomaly summary |

### Schemes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/schemes/` | List schemes (filter: `district`, `scheme_type`, `is_delayed`, `min_pending_days`) |

### Natural Language Query

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/query/` | Submit NL query, returns parsed intent + result summary |
| GET | `/api/v1/query/history` | Last 20 queries with results |

**Request body:**
```json
{ "query": "Show pending housing applications in Krishna district above 90 days" }
```

**Response:**
```json
{
  "id": "uuid",
  "raw_query": "Show pending housing applications in Krishna district above 90 days",
  "parsed_intent": "scheme_status",
  "parsed_filters": "{\"district\": \"Krishna\", \"scheme_type\": \"housing\", \"min_pending_days\": 90}",
  "result_summary": "Found 1 scheme(s) matching your query. Total pending applications: 3,200. ..."
}
```

## NL Query Examples

| Query | Intent | Filters |
|-------|--------|---------|
| Show pending housing applications in Krishna district above 90 days | scheme_status | district=Krishna, scheme_type=housing, min_pending_days=90 |
| Which departments have anomalies? | anomaly_check | — |
| Show all delayed pension schemes in Guntur | scheme_status | district=Guntur, scheme_type=pension, is_delayed=true |
| Give me an executive summary of all schemes | summary | — |
| Show infrastructure department spending | department_kpi | department_category=infrastructure |
| Show health schemes with more than 30 days pending | scheme_status | scheme_type=health, min_pending_days=30 |

## Configuring Claude API

1. Get a key at https://console.anthropic.com
2. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`
3. Model is set to `claude-haiku-4-5-20251001` (fast, low cost) — change via `CLAUDE_MODEL` env var

Without a valid key, `parse_query_with_claude()` catches the `APIError` and falls back to `rule_based_parse()` automatically — all queries still work.

## Anomaly Detection Thresholds

| Condition | Threshold | Reason Text |
|-----------|-----------|-------------|
| Budget spent | > 95% | Budget nearly exhausted |
| Budget spent | < 5% | Severely under-utilized budget |
| Avg file clearance | > 45 days | High file clearance time |
| Pending files | > 500 | High pending file count |

Run detection: `POST /api/v1/departments/run-anomaly-detection`

## Architecture

```
frontend (Next.js 14)  →  backend (FastAPI async)  →  PostgreSQL 16
                               ↓
                        Anthropic Claude API
                        (NL query parsing)
```

- Models: `Department`, `Scheme`, `KpiMetric`, `NlQuery`
- Async SQLAlchemy 2.0 with asyncpg driver (production) / aiosqlite (tests)
- Alembic migrations in `backend/alembic/versions/001_initial.py`
