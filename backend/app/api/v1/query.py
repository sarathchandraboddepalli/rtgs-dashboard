import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.nl_query import NlQuery
from app.schemas.nl_query import NlQueryRequest, NlQueryResponse
from app.services.nl_query_service import parse_query_with_claude, execute_query

router = APIRouter()

@router.post("/", response_model=NlQueryResponse)
async def natural_language_query(request: NlQueryRequest, db: AsyncSession = Depends(get_db)):
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
