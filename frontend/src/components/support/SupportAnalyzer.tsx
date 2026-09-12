import { useState } from "react";
import MessageInput from "./MessageInput.tsx";
import AnalysisSummary from "./AnalysisSummary.tsx";
import GeneratedReply from "./GeneratedReply.tsx";
import DecisionReason from "./DecisionReason.tsx";
import EvidenceSection from "./EvidenceSection.tsx";
import { analyzeMessage } from "../../lib/api.ts";
import type { SupportResponse } from "../../types/support.ts";

export default function SupportAnalyzer() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<SupportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async (message: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await analyzeMessage(message);
      setResult(response);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <MessageInput onAnalyze={handleAnalyze} isLoading={isLoading} />
      
      {error && (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5 text-sm font-medium text-red-800 shadow-sm">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-10 space-y-6">
          <AnalysisSummary 
            intent={result.intent} 
            confidence={result.intent_confidence} 
            decision={result.decision} 
          />
          
          <div className="grid gap-6 md:grid-cols-2 items-start">
            <GeneratedReply reply={result.reply} />
            <div className="mt-6">
              <DecisionReason reason={result.reason} />
            </div>
          </div>
          
          <EvidenceSection evidenceList={result.evidence} />
        </div>
      )}
    </div>
  );
}
