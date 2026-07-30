from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class SchemeOut(BaseModel):
    id: UUID
    name: str
    department_id: UUID
    scheme_type: str
    district: str
    total_beneficiaries: int
    active_beneficiaries: int
    pending_applications: int
    avg_pending_days: float
    sla_days: int
    disbursed_crores: float
    target_crores: float
    completion_pct: float
    is_delayed: bool
    delay_reason: str | None
    model_config = {"from_attributes": True}
