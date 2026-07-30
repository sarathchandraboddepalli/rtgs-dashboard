from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.department import Department
from app.models.scheme import Scheme
from app.models.kpi_metric import KpiMetric

async def get_executive_summary(db: AsyncSession) -> dict:
    total_depts = (await db.execute(select(func.count(Department.id)))).scalar() or 0
    anomalous_depts = (await db.execute(select(func.count(Department.id)).where(Department.has_anomaly == True))).scalar() or 0
    total_budget = (await db.execute(select(func.sum(Department.budget_crores)))).scalar() or 0
    total_spent = (await db.execute(select(func.sum(Department.spent_crores)))).scalar() or 0
    total_schemes = (await db.execute(select(func.count(Scheme.id)))).scalar() or 0
    delayed_schemes = (await db.execute(select(func.count(Scheme.id)).where(Scheme.is_delayed == True))).scalar() or 0
    total_pending = (await db.execute(select(func.sum(Scheme.pending_applications)))).scalar() or 0
    total_beneficiaries = (await db.execute(select(func.sum(Scheme.active_beneficiaries)))).scalar() or 0
    return {
        "departments": {"total": total_depts, "anomalous": anomalous_depts},
        "budget": {"total_crores": float(total_budget or 0), "spent_crores": float(total_spent or 0), "utilization_pct": float(total_spent / total_budget * 100) if total_budget else 0},
        "schemes": {"total": total_schemes, "delayed": delayed_schemes, "pending_applications": int(total_pending or 0), "active_beneficiaries": int(total_beneficiaries or 0)},
    }

async def get_district_scheme_stats(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Scheme.district, func.count(Scheme.id).label("scheme_count"), func.sum(Scheme.pending_applications).label("total_pending"))
        .group_by(Scheme.district)
        .order_by(func.sum(Scheme.pending_applications).desc())
    )
    return [{"district": r.district, "scheme_count": r.scheme_count, "total_pending": int(r.total_pending or 0)} for r in result.all()]
