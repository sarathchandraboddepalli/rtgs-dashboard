from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class NlQueryRequest(BaseModel):
    query: str

class NlQueryResponse(BaseModel):
    id: UUID
    raw_query: str
    parsed_intent: str | None
    parsed_filters: str | None
    result_summary: str | None
    model_config = {"from_attributes": True}
