from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.kpi_metric import KpiMetric

router = APIRouter()

@router.get("/")
async def list_kpis(department_id: str | None = None, is_anomalous: bool | None = None, db: AsyncSession = Depends(get_db)):
    q = select(KpiMetric)
    if department_id is not None:
        q = q.where(KpiMetric.department_id == department_id)
    if is_anomalous is not None:
        q = q.where(KpiMetric.is_anomalous == is_anomalous)
    result = await db.execute(q)
    kpis = result.scalars().all()
    return [{"id": str(k.id), "metric_name": k.metric_name, "category": k.metric_category, "current": k.current_value, "target": k.target_value, "unit": k.unit, "trend": k.trend, "is_anomalous": k.is_anomalous} for k in kpis]
