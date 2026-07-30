from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.department import Department
from app.models.kpi_metric import KpiMetric

SPENDING_ANOMALY_THRESHOLD = 0.95  # >95% budget spent = anomaly
SPENDING_LOW_THRESHOLD = 0.05       # <5% budget spent by year-end = anomaly
FILE_CLEARANCE_THRESHOLD = 45       # >45 days avg = anomaly

async def run_anomaly_detection(db: AsyncSession) -> list[dict]:
    """Detect anomalous departments based on KPI thresholds."""
    result = await db.execute(select(Department))
    departments = list(result.scalars().all())
    anomalies = []

    for dept in departments:
        reasons = []

        if dept.budget_crores > 0:
            spend_pct = dept.spent_crores / dept.budget_crores
            if spend_pct > SPENDING_ANOMALY_THRESHOLD:
                reasons.append(f"Budget nearly exhausted ({spend_pct*100:.1f}% spent)")
            elif spend_pct < SPENDING_LOW_THRESHOLD:
                reasons.append(f"Severely under-utilized budget ({spend_pct*100:.1f}% spent)")

        if dept.avg_file_clearance_days > FILE_CLEARANCE_THRESHOLD:
            reasons.append(f"High file clearance time ({dept.avg_file_clearance_days:.0f} days avg)")

        if dept.pending_files > 500:
            reasons.append(f"High pending file count ({dept.pending_files})")

        if reasons:
            dept.has_anomaly = True
            dept.anomaly_reason = "; ".join(reasons)
            anomalies.append({"department": dept.name, "reasons": reasons})
        else:
            dept.has_anomaly = False
            dept.anomaly_reason = None

    await db.commit()
    return anomalies

async def get_anomaly_summary(db: AsyncSession) -> dict:
    result = await db.execute(select(Department).where(Department.has_anomaly == True))
    anomalous = list(result.scalars().all())
    return {
        "total_anomalous": len(anomalous),
        "departments": [{"name": d.name, "reason": d.anomaly_reason, "category": d.category} for d in anomalous],
    }
