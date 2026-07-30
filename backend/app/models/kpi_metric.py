import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from app.database import Base

class KpiMetric(Base):
    __tablename__ = "kpi_metrics"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("departments.id"))
    metric_name: Mapped[str] = mapped_column(String(255))
    metric_category: Mapped[str] = mapped_column(String(50))  # spending, delivery, compliance, satisfaction
    current_value: Mapped[float] = mapped_column(Float)
    target_value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String(20))  # %, days, crores, count
    is_anomalous: Mapped[bool] = mapped_column(Boolean, default=False)
    trend: Mapped[str] = mapped_column(String(10), default="stable")  # improving, declining, stable
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
