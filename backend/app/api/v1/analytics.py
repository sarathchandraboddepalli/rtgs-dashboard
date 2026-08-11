from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.analytics_service import get_executive_summary, get_district_scheme_stats
from app.services.seed_service import seed_data

router = APIRouter()

@router.get("/executive-summary")
async def executive_summary(db: AsyncSession = Depends(get_db)):
    return await get_executive_summary(db)

@router.get("/district-stats")
async def district_stats(db: AsyncSession = Depends(get_db)):
    return await get_district_scheme_stats(db)

@router.post("/seed")
async def seed(db: AsyncSession = Depends(get_db)):
    await seed_data(db)
    return {"seeded": True}
