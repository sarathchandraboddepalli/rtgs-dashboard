from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.department import Department
from app.schemas.department import DepartmentOut
from app.services.anomaly_service import run_anomaly_detection, get_anomaly_summary

router = APIRouter()

@router.get("/", response_model=list[DepartmentOut])
async def list_departments(category: str | None = None, has_anomaly: bool | None = None, db: AsyncSession = Depends(get_db)):
    q = select(Department).order_by(Department.name)
    if category:
        q = q.where(Department.category == category)
    if has_anomaly is not None:
        q = q.where(Department.has_anomaly == has_anomaly)
    result = await db.execute(q)
    return list(result.scalars().all())

@router.post("/run-anomaly-detection")
async def detect_anomalies(db: AsyncSession = Depends(get_db)):
    anomalies = await run_anomaly_detection(db)
    return {"anomalies_found": len(anomalies), "details": anomalies}

@router.get("/anomalies")
async def anomaly_summary(db: AsyncSession = Depends(get_db)):
    return await get_anomaly_summary(db)
