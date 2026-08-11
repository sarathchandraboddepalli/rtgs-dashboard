import json
import time
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.nl_query import NlQuery
from app.schemas.nl_query import NlQueryRequest, NlQueryResponse
from app.services.nl_query_service import parse_query_with_claude, execute_query

# NOTE: This endpoint needs proper rate limiting via slowapi or a reverse proxy.
# A lightweight in-process fallback is implemented below (10 requests/minute per IP).
# For production, install slowapi and replace this with @limiter.limit("10/minute").
_rate_limit_store: dict = defaultdict(list)
_RATE_LIMIT_REQUESTS = 10
_RATE_LIMIT_WINDOW = 60  # seconds

router = APIRouter()

@router.post("/", response_model=NlQueryResponse)
async def natural_language_query(request: Request, body: NlQueryRequest, db: AsyncSession = Depends(get_db)):
    # Basic per-IP rate limiting (10 requests/minute)
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window_start = now - _RATE_LIMIT_WINDOW
    _rate_limit_store[client_ip] = [t for t in _rate_limit_store[client_ip] if t > window_start]
    if len(_rate_limit_store[client_ip]) >= _RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded: 10 requests per minute allowed.")
    _rate_limit_store[client_ip].append(now)
    request = body
    parsed = await parse_query_with_claude(request.query)
    intent = parsed.get("intent", "summary")
    filters = parsed.get("filters", {})
    result_summary = await execute_query(filters, intent, db)
    nl_query = NlQuery(
        raw_query=request.query,
        parsed_intent=intent,
        parsed_filters=json.dumps(filters),
        result_summary=result_summary,
    )
    db.add(nl_query)
    await db.commit()
    await db.refresh(nl_query)
    return nl_query

@router.get("/history")
async def query_history(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(NlQuery).order_by(NlQuery.created_at.desc()).limit(20))
    queries = result.scalars().all()
    return [{"id": str(q.id), "query": q.raw_query, "intent": q.parsed_intent, "result": q.result_summary, "created_at": str(q.created_at)} for q in queries]
