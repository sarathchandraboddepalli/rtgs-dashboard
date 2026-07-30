from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.scheme import Scheme
from app.schemas.scheme import SchemeOut

router = APIRouter()

@router.get("/", response_model=list[SchemeOut])
async def list_schemes(district: str | None = None, scheme_type: str | None = None, is_delayed: bool | None = None, min_pending_days: float | None = None, db: AsyncSession = Depends(get_db)):
    q = select(Scheme).order_by(Scheme.avg_pending_days.desc())
    if district:
        q = q.where(Scheme.district == district)
    if scheme_type:
        q = q.where(Scheme.scheme_type == scheme_type)
    if is_delayed is not None:
        q = q.where(Scheme.is_delayed == is_delayed)
    if min_pending_days is not None:
        q = q.where(Scheme.avg_pending_days >= min_pending_days)
    result = await db.execute(q)
    return list(result.scalars().all())
