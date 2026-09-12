import IntentCard from "./IntentCard.tsx";
import ConfidenceCard from "./ConfidenceCard.tsx";
import DecisionCard from "./DecisionCard.tsx";

export default function AnalysisSummary({ intent, confidence, decision }: { intent: string, confidence: number, decision: string }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <IntentCard intent={intent} />
      <ConfidenceCard confidence={confidence} />
      <DecisionCard decision={decision} />
    </div>
  );
}
