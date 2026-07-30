from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DepartmentOut(BaseModel):
    id: UUID
    name: str
    code: str
    category: str
    budget_crores: float
    spent_crores: float
    pending_files: int
    avg_file_clearance_days: float
    has_anomaly: bool
    anomaly_reason: str | None
    model_config = {"from_attributes": True}
