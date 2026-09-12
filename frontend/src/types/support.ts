export type SupportRequest = {
  message: string;
};

export type Evidence = {
  conversation_id: string;
  customer_message: string;
  brand_response?: string;
  similarity_score: number;
};

export type SupportResponse = {
  intent: string;
  intent_confidence: number;
  decision: "AUTO" | "ESCALATE" | string;
  reason: string;
  reply: string;
  evidence: Evidence[];
};
