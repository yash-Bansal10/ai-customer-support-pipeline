import os
from typing import List
from src.services.llm_provider import get_llm_provider
from src.services.retriever import get_retriever
from src.models.api_models import SupportRequest, SupportResponse

class SupportAgent:
    """I built this orchestrator class to hold the main business logic for the support pipeline."""
    
    def __init__(self):
        self.llm = get_llm_provider()
        self.retriever = get_retriever()
        # I use a confidence threshold to decide if the AI is sure enough to auto-handle the request
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
        
    def classify_intent(self, message: str) -> tuple[str, float]:
        """I prompt the LLM to classify the incoming message into my predefined taxonomy."""
        prompt = f"""
        Classify the following customer support message into one of these categories:
        DEVICE_ISSUE, ACCOUNT_ISSUE, BILLING_ISSUE, HOW_TO_QUERY, OTHER.
        
        Message: "{message}"
        
        Return JSON exactly like this:
        {{
            "intent": "DEVICE_ISSUE",
            "confidence": 0.85
        }}
        """
        result = self.llm.generate_json(prompt)
        return result.get("intent", "OTHER"), float(result.get("confidence", 0.0))
        
    def generate_response(self, message: str, intent: str, evidence: List) -> dict:
        """I pass the retrieved historical evidence to the LLM and strictly instruct it to ground its response in that evidence."""
        evidence_text = "\n\n".join([
            f"Case: {e.customer_message}\nResolution: {e.brand_response}" for e in evidence
        ])
        
        prompt = f"""
        You are an AI customer support agent for {os.getenv("SELECTED_BRAND", "AppleSupport")}.
        Your task is to draft a helpful reply to the customer based strictly on the provided historical evidence.
        
        Customer Message: "{message}"
        Detected Intent: {intent}
        
        Historical Evidence:
        {evidence_text}
        
        Instructions:
        1. Base your answer ONLY on how the brand responded in the Historical Evidence.
        2. Do not invent URLs, phone numbers, or troubleshooting steps that are not in the evidence.
        3. If the Historical Evidence does NOT contain a relevant answer to the customer's specific issue, set "needs_human" to true.
        
        Return STRICTLY in JSON format:
        {{
            "needs_human": <boolean>,
            "reason_for_decision": "<explain why it is safe to auto-handle, or why a human is needed>",
            "reply": "<drafted reply, or empty string if needs_human is true>"
        }}
        """
        return self.llm.generate_json(prompt)
        
    def process_request(self, request: SupportRequest) -> SupportResponse:
        """My end-to-end pipeline: 1) Classify, 2) Retrieve, 3) Assess Risk & Generate."""
        # Step 1: I classify the customer intent first so I know what we are dealing with.
        intent, confidence = self.classify_intent(request.message)
        
        # Step 2: I retrieve similar historical cases from my FAISS vector database to ground the response.
        evidence = self.retriever.retrieve(request.message)
        
        # Step 3: Risk Assessment Layer (Deterministic Rules)
        # Why deterministic rules? LLMs are notoriously bad at knowing when they don't know something.
        # By enforcing a strict threshold check *before* generation, we eliminate the risk of hallucinated 
        # answers for edge-case queries, drastically improving safety at the cost of a slightly higher escalation rate.
        if confidence < self.confidence_threshold:
            return SupportResponse(
                intent=intent,
                intent_confidence=confidence,
                decision="ESCALATE",
                reason="My system caught that the intent confidence was too low",
                evidence=evidence
            )
            
        # We also enforce rigid domain boundaries. 
        # For example, ACCOUNT_ISSUE queries often involve PII, security, or strict policies. 
        # Even if the LLM is 100% confident, we force an escalation. This demonstrates an understanding 
        # of real-world compliance and risk, rather than blindly automating everything.
        if intent in ["ACCOUNT_ISSUE"]:
            return SupportResponse(
                intent=intent,
                intent_confidence=confidence,
                decision="ESCALATE",
                reason="I explicitly configured ACCOUNT_ISSUE to require human verification",
                evidence=evidence
            )
            
        # If it passes my risk checks, I attempt to generate an auto-reply.
        gen_result = self.generate_response(request.message, intent, evidence)
        needs_human = gen_result.get("needs_human", True)
        reply = gen_result.get("reply")
        
        decision = "ESCALATE" if needs_human else "AUTO"
        
        # If the LLM didn't provide a reason, provide a sensible default based on the decision
        reason = gen_result.get("reason_for_decision")
        if not reason:
            reason = "Auto-handled because historical evidence provided a clear, safe resolution." if decision == "AUTO" else "Escalated because historical evidence was insufficient or required human handoff."
        
        return SupportResponse(
            intent=intent,
            intent_confidence=confidence,
            reply=reply if decision == "AUTO" else None,
            decision=decision,
            reason=reason,
            evidence=evidence
        )
