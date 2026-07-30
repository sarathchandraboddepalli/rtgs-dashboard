import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid
from app.database import Base

class NlQuery(Base):
    __tablename__ = "nl_queries"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_query: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_intent: Mapped[str | None] = mapped_column(String(50))  # scheme_status, department_kpi, anomaly_check, summary
    parsed_filters: Mapped[str | None] = mapped_column(Text)  # JSON filters extracted
    result_summary: Mapped[str | None] = mapped_column(Text)  # human-readable answer
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
