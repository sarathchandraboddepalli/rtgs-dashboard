# CHANGES

## v1.0.0 — Initial MVP (2026-07-31)

### What Was Built

A production-ready Real-Time Governance Dashboard for Andhra Pradesh (AP RTGS) that plugs into the AWARE 2.0 data lake concept, built with:

- **FastAPI** async backend (Python 3.12) with SQLAlchemy 2.0 async ORM
- **Next.js 14** frontend with Tailwind CSS
- **PostgreSQL 16** as the primary database (SQLite in-memory for tests)
- **Docker Compose** orchestration (ports: API 8007, Frontend 3007, DB 5439)

### Features Implemented

**Natural Language Query Interface**
- POST `/api/v1/query/` accepts plain English questions
- Primary parser: Claude API (`claude-haiku-4-5-20251001`) via Anthropic SDK
- Fallback: `rule_based_parse()` using regex + keyword matching (no API key required)
- Extracted fields: `intent`, `district`, `scheme_type`, `min_pending_days`, `department_category`, `is_delayed`, `has_anomaly`
- Query history stored in `nl_queries` table and surfaced via GET `/api/v1/query/history`

**NL Query Flow**
1. User submits plain-English query (e.g. "Show pending housing applications in Krishna district above 90 days")
2. `parse_query_with_claude()` calls Claude API with a structured system prompt requesting JSON output
3. On API failure / JSON parse error, falls back to `rule_based_parse()` which uses:
   - Keyword dict ordered: `anomaly_check` → `scheme_status` → `department_kpi` → `summary` (priority matters — anomaly beats department)
   - Regex `r'(?:above|more than|over|>)\s*(\d+)\s*days?'` for day threshold extraction
   - District substring matching against 13 AP district names
4. `execute_query()` builds SQLAlchemy queries from parsed filters and returns a human-readable summary
5. Result + metadata saved to `nl_queries` table

**Predictive Analytics / Executive Dashboard**
- GET `/api/v1/analytics/executive-summary` — department counts, budget utilization %, active beneficiaries, pending applications, delayed scheme count
- GET `/api/v1/analytics/district-stats` — per-district scheme count and total pending applications, ordered by load

**Anomaly Detection**
- POST `/api/v1/departments/run-anomaly-detection` — scans all departments against thresholds:
  - Spending > 95% of budget → "Budget nearly exhausted"
  - Spending < 5% of budget → "Severely under-utilized budget"
  - Avg file clearance > 45 days → "High file clearance time"
  - Pending files > 500 → "High pending file count"
- Updates `has_anomaly` and `anomaly_reason` fields in-place
- GET `/api/v1/departments/anomalies` — returns current anomaly summary

**AWARE 2.0 Mock Seed Data**
- 8 AP government departments: Social Welfare, Roads & Buildings, Finance, Health, Agriculture, Education, Revenue, MAUD
- 10 schemes across 8 AP districts: YSR Pension Kanuka, PMAY-G Housing, YSR Rythu Bharosa, YSR Aarogyasri
- Realistic delay reasons, beneficiary counts, disbursement figures seeded at first request
- Seed is idempotent (checks `count(Department.id) > 0` before inserting)

### Bug Fixes Applied During Build

1. **Regex bug**: `r'(?:above|more than|over|>\s*)(\d+)'` did not capture digits after "above 90" or "more than 45" because `\s*` was inside the alternation for `>` only. Fixed to `r'(?:above|more than|over|>)\s*(\d+)'`.
2. **Intent priority bug**: INTENT_KEYWORDS dict iterated `department_kpi` before `anomaly_check`. Query "Which departments have anomalies?" matched "department" first, returning wrong intent. Fixed by reordering: `anomaly_check` is checked first.

### Run Instructions

**Docker (full stack)**
```bash
cp .env.example .env
# Edit .env to set your ANTHROPIC_API_KEY
docker compose up --build
# Frontend: http://localhost:3007
# API docs: http://localhost:8007/docs
```

**Local backend (with SQLite for dev)**
```bash
cd backend
pip install -r requirements.txt
# Override DB to SQLite for local dev:
DATABASE_URL=sqlite+aiosqlite:///./rtgs_dev.db uvicorn app.main:app --reload --port 8000
# Seed data: POST http://localhost:8000/api/v1/analytics/seed
```

**Run tests (no API key required)**
```bash
cd backend
python -m pytest tests/ -v
```

### What to Tackle Next

1. **Real AWARE 2.0 integration**: Replace mock seed data with live API connectors to AWARE 2.0 endpoints for departments, schemes, and KPIs.
2. **Predictive ML models**: Add scikit-learn or statsmodels-based regression models to predict pension delivery delays and scheme eligibility backlogs from historical trend data.
3. **Time-series KPI tracking**: KpiMetric table is seeded but not yet populated — wire it to periodic snapshots and build trend charts on the frontend.
4. **Authentication**: Add JWT-based auth for the CM/Secretary-level executive views; role-based access for department-level drill-downs.
5. **Alembic migrations**: The alembic setup is configured but migrations have not been run in production — run `alembic upgrade head` in the container entrypoint.
6. **Frontend charts**: Replace the load-bar table with Recharts or Chart.js for district heat maps and spending trend lines.
7. **Alert webhooks**: Trigger SMS/email alerts when anomaly detection finds new issues.
8. **CI/CD**: Add GitHub Actions workflow to run `pytest` on push and build Docker images.
