from pydantic import BaseModel, Field
from typing import List, Optional

class SupportRequest(BaseModel):
    message: str = Field(..., description="The incoming customer message")

class HistoricalEvidence(BaseModel):
    conversation_id: str
    customer_message: str
    brand_response: str
    similarity_score: float

class SupportResponse(BaseModel):
    intent: str
    intent_confidence: float
    reply: Optional[str] = None
    decision: str = Field(..., description="'AUTO' or 'ESCALATE'")
    reason: str
    evidence: List[HistoricalEvidence] = []
