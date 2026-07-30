import json
import re
from anthropic import Anthropic, APIError
from app.config import settings

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

INTENT_KEYWORDS = {
    "anomaly_check": ["anomal", "unusual", "spike", "outlier", "flag", "suspicious"],
    "scheme_status": ["scheme", "application", "beneficiar", "pending", "housing", "pension", "aarogyasri", "rythu"],
    "department_kpi": ["department", "ministry", "spending", "budget", "files", "clearance"],
    "summary": ["summary", "overview", "dashboard", "top", "worst", "best"],
}

AP_DISTRICTS = [
    "Srikakulam", "Vizianagaram", "Visakhapatnam", "East Godavari", "West Godavari",
    "Krishna", "Guntur", "Prakasam", "Nellore", "Kurnool", "Kadapa", "Anantapur", "Chittoor",
]

def rule_based_parse(query: str) -> dict:
    """Fallback parser using regex/keywords when Claude is unavailable."""
    q = query.lower()

    # Detect intent
    intent = "summary"
    for candidate_intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            intent = candidate_intent
            break

    filters = {}

    # Extract district
    for district in AP_DISTRICTS:
        if district.lower() in q:
            filters["district"] = district
            break

    # Extract scheme type
    scheme_types = {"housing": "housing", "pension": "pension", "agriculture": "agriculture", "health": "health"}
    for kw, stype in scheme_types.items():
        if kw in q:
            filters["scheme_type"] = stype
            break

    # Extract day threshold (e.g., "above 90 days", "more than 30 days")
    day_match = re.search(r'(?:above|more than|over|>)\s*(\d+)\s*days?', q)
    if day_match:
        filters["min_pending_days"] = int(day_match.group(1))

    # Extract department category
    categories = ["welfare", "infrastructure", "finance", "health", "education"]
    for cat in categories:
        if cat in q:
            filters["department_category"] = cat
            break

    return {"intent": intent, "filters": filters}

async def parse_query_with_claude(query: str) -> dict:
    """Use Claude to parse natural language into structured filters."""
    system_prompt = """You are an AI assistant for AP government's RTGS dashboard.
Parse the user's natural language query into a JSON with:
- "intent": one of ["scheme_status", "department_kpi", "anomaly_check", "summary"]
- "filters": dict with optional keys:
  - "district": AP district name
  - "scheme_type": one of ["housing", "pension", "agriculture", "health", "education"]
  - "department_category": one of ["welfare", "infrastructure", "finance", "revenue", "health", "education"]
  - "min_pending_days": integer (for "above N days" queries)
  - "is_delayed": boolean
  - "has_anomaly": boolean

Respond ONLY with valid JSON. No explanation."""

    try:
        response = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=256,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
        )
        text = response.content[0].text.strip()
        # Strip markdown code blocks if present
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)
        return json.loads(text)
    except (APIError, json.JSONDecodeError, Exception):
        return rule_based_parse(query)

async def execute_query(filters: dict, intent: str, db) -> str:
    """Execute parsed filters against DB and return a human-readable summary."""
    from sqlalchemy import select
    from app.models.scheme import Scheme
    from app.models.department import Department

    if intent == "scheme_status":
        q = select(Scheme)
        if district := filters.get("district"):
            q = q.where(Scheme.district == district)
        if scheme_type := filters.get("scheme_type"):
            q = q.where(Scheme.scheme_type == scheme_type)
        if min_days := filters.get("min_pending_days"):
            q = q.where(Scheme.avg_pending_days >= min_days)
        if filters.get("is_delayed"):
            q = q.where(Scheme.is_delayed == True)
        result = await db.execute(q.limit(20))
        schemes = list(result.scalars().all())
        if not schemes:
            return f"No schemes found matching your criteria: {filters}"
        total_pending = sum(s.pending_applications for s in schemes)
        return f"Found {len(schemes)} scheme(s) matching your query. Total pending applications: {total_pending:,}. Districts: {', '.join(set(s.district for s in schemes))}. Most delayed: {max(schemes, key=lambda s: s.avg_pending_days).name} ({max(s.avg_pending_days for s in schemes):.0f} days avg)."

    elif intent == "department_kpi":
        q = select(Department)
        if cat := filters.get("department_category"):
            q = q.where(Department.category == cat)
        if filters.get("has_anomaly"):
            q = q.where(Department.has_anomaly == True)
        result = await db.execute(q.limit(20))
        depts = list(result.scalars().all())
        if not depts:
            return "No departments found matching your criteria."
        total_budget = sum(d.budget_crores for d in depts)
        total_spent = sum(d.spent_crores for d in depts)
        return f"Found {len(depts)} department(s). Total budget: ₹{total_budget:.0f} Cr. Total spent: ₹{total_spent:.0f} Cr ({total_spent/total_budget*100:.1f}%). Departments with anomalies: {sum(1 for d in depts if d.has_anomaly)}."

    elif intent == "anomaly_check":
        q = select(Department).where(Department.has_anomaly == True)
        result = await db.execute(q)
        anomalous = list(result.scalars().all())
        if not anomalous:
            return "No anomalous departments detected currently."
        return f"⚠️ {len(anomalous)} department(s) with anomalies: {', '.join(d.name for d in anomalous)}. Issues: {'; '.join(d.anomaly_reason or 'Unknown' for d in anomalous[:3])}."

    else:  # summary
        dept_result = await db.execute(select(Department))
        depts = list(dept_result.scalars().all())
        scheme_result = await db.execute(select(Scheme))
        schemes = list(scheme_result.scalars().all())
        total_pending = sum(s.pending_applications for s in schemes)
        delayed = sum(1 for s in schemes if s.is_delayed)
        anomalous = sum(1 for d in depts if d.has_anomaly)
        return f"AP Governance Summary: {len(depts)} departments, {len(schemes)} schemes across {len(set(s.district for s in schemes))} districts. Total pending applications: {total_pending:,}. Delayed schemes: {delayed}. Departments with anomalies: {anomalous}."
