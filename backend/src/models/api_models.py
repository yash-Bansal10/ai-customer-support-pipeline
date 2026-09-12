from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class SupportRequest(BaseModel):
    message: str = Field(..., max_length=1000, description="The incoming customer message")

class HistoricalEvidence(BaseModel):
    conversation_id: str
    customer_message: str
    brand_response: str
    similarity_score: float

class SupportResponse(BaseModel):
    intent: Literal["DEVICE_ISSUE", "ACCOUNT_ISSUE", "BILLING_ISSUE", "HOW_TO_QUERY", "OTHER"]
    intent_confidence: float
    reply: Optional[str] = None
    decision: Literal["AUTO", "ESCALATE"]
    reason: str
    evidence: List[HistoricalEvidence] = Field(default_factory=list)

class IntentClassificationResult(BaseModel):
    intent: Literal["DEVICE_ISSUE", "ACCOUNT_ISSUE", "BILLING_ISSUE", "HOW_TO_QUERY", "OTHER"]
    confidence: float = Field(ge=0.0, le=1.0)

class GenerationResult(BaseModel):
    needs_human: bool
    reason_for_decision: str
    reply: str
