import uuid
from datetime import datetime, date
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Date, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from app.database import Base

class Scheme(Base):
    __tablename__ = "schemes"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("departments.id"))
    scheme_type: Mapped[str] = mapped_column(String(50))  # pension, housing, agriculture, health, education
    district: Mapped[str] = mapped_column(String(100))
    total_beneficiaries: Mapped[int] = mapped_column(Integer, default=0)
    active_beneficiaries: Mapped[int] = mapped_column(Integer, default=0)
    pending_applications: Mapped[int] = mapped_column(Integer, default=0)
    avg_pending_days: Mapped[float] = mapped_column(Float, default=0.0)
    sla_days: Mapped[int] = mapped_column(Integer, default=30)
    disbursed_crores: Mapped[float] = mapped_column(Float, default=0.0)
    target_crores: Mapped[float] = mapped_column(Float, default=0.0)
    completion_pct: Mapped[float] = mapped_column(Float, default=0.0)
    is_delayed: Mapped[bool] = mapped_column(Boolean, default=False)
    delay_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
