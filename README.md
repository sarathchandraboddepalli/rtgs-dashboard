# RTGS Dashboard — Government Operations Analytics

A real-time analytics platform for monitoring government department performance and scheme delivery. Features a natural language query interface powered by Claude, anomaly detection on budget and file clearance KPIs, and an executive summary view for administrators.

## What It Does

District and department administrators generate hundreds of KPI data points — budget utilisation, pending files, scheme beneficiary counts, application backlogs. This dashboard aggregates that data, surfaces anomalies automatically, and lets non-technical officers ask questions in plain English instead of writing SQL.

**Example queries:**
- "Which departments have overspent their budget this quarter?"
- "Show me schemes with more than 500 pending applications in Kurnool"
- "Which districts have the worst file clearance times?"

## Architecture

```
 Next.js Frontend (port 3007)
         |
         v
  FastAPI REST API (port 8007)
         |
   ------+------
   |            |
   v            v
PostgreSQL   Anthropic Claude Haiku
(KPI data)   (NL query translation)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI 0.115, Python 3.12 |
| LLM | Anthropic Claude Haiku (NL query layer) |
| Database | PostgreSQL 16 + SQLAlchemy (async) + Alembic |
| Frontend | Next.js 14, Tailwind CSS |
| Containerisation | Docker + Docker Compose |

## Features

### Natural Language Query
Officers type questions in plain English. Claude translates intent into structured filters, which run against live KPI data and return formatted results. No SQL, no training required.

### Anomaly Detection
Automatic flagging on configurable thresholds:
- Budget nearly exhausted (>95% spent)
- Severely under-utilised budget (<5% spent by fiscal year-end)
- High average file clearance time (>45 days)
- High pending file count (>500 files)

### Executive Summary
Single-call aggregation: total departments, anomalous departments, total budget vs spent, scheme counts, delayed schemes, pending applications, active beneficiaries.

### District-Level Breakdown
Scheme distribution and pending application counts grouped by district, ordered by backlog severity.

## Quick Start

```bash
git clone https://github.com/sarathchandraboddepalli/rtgs-dashboard
cd rtgs-dashboard
cp .env.example .env    # add your ANTHROPIC_API_KEY
docker-compose up --build
```

Run migrations and seed data:
```bash
docker-compose exec api alembic upgrade head
docker-compose exec api python -c "from app.services.seed_service import seed_all; import asyncio; asyncio.run(seed_all())"
```

- **Frontend:** http://localhost:3007
- **API:** http://localhost:8007
- **Swagger docs:** http://localhost:8007/docs

## API Reference

```
GET  /api/v1/analytics/summary         # Executive summary
GET  /api/v1/analytics/districts       # District-level scheme stats
GET  /api/v1/analytics/anomalies       # Run and return anomaly scan
GET  /api/v1/departments/              # All departments with KPIs
GET  /api/v1/schemes/                  # All schemes
POST /api/v1/query/                    # Natural language query
GET  /api/v1/kpis/                     # Raw KPI metrics
```

## Running Tests

```bash
cd backend
pip install pytest pytest-asyncio anyio httpx aiosqlite fastapi pydantic pydantic-settings "sqlalchemy[asyncio]" anthropic
python -m pytest tests/ -v
```

## Environment Variables

| Variable | Description |
|----------|-------------|
|  | PostgreSQL connection string |
|  | Anthropic API key for NL query |
|  | Claude model ID (default: ) |
