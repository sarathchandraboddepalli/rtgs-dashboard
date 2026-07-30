from fastapi import APIRouter
from app.api.v1 import departments, schemes, kpis, query, analytics
api_router = APIRouter()
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(schemes.router, prefix="/schemes", tags=["schemes"])
api_router.include_router(kpis.router, prefix="/kpis", tags=["kpis"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
