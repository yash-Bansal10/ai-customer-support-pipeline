import { Info } from "lucide-react";

export default function DecisionReason({ reason }: { reason: string }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm h-full">
      <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-gray-500 mb-3 border-b border-gray-100 pb-3">
        <Info className="h-4 w-4 text-blue-500" />
        Why this decision?
      </div>
      <p className="text-gray-700 text-sm leading-relaxed">{reason || "No reasoning provided."}</p>
    </div>
  );
}
