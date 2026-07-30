import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from app.database import Base

class Department(Base):
    __tablename__ = "departments"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    category: Mapped[str] = mapped_column(String(50))  # welfare, infrastructure, finance, revenue, health, education
    budget_crores: Mapped[float] = mapped_column(Float)
    spent_crores: Mapped[float] = mapped_column(Float, default=0.0)
    pending_files: Mapped[int] = mapped_column(Integer, default=0)
    avg_file_clearance_days: Mapped[float] = mapped_column(Float, default=0.0)
    has_anomaly: Mapped[bool] = mapped_column(Boolean, default=False)
    anomaly_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
