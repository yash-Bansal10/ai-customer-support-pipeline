import { FileText } from "lucide-react";
import type { Evidence } from "../../types/support.ts";

export default function EvidenceCard({ evidence }: { evidence: Evidence }) {
  const percentage = Math.round((evidence.similarity_score || 0) * 100);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition-all hover:shadow-md flex flex-col h-full">
      <div className="flex items-center justify-between mb-4 border-b border-gray-100 pb-3">
        <div className="flex items-center gap-2 text-xs font-medium text-gray-600 uppercase tracking-wide">
          <FileText className="h-4 w-4 text-indigo-500" />
          Case #{evidence.conversation_id || "Unknown"}
        </div>
        <div className="rounded-full bg-indigo-50 border border-indigo-100 px-2.5 py-0.5 text-[11px] font-semibold text-indigo-700">
          Similarity {percentage}%
        </div>
      </div>
      
      <div className="space-y-4 flex-1">
        <div>
          <h4 className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Customer</h4>
          <p className="text-sm text-gray-800 bg-gray-50/80 p-3 rounded-md border border-gray-100/80 leading-relaxed">{evidence.customer_message || "No message."}</p>
        </div>
        
        {evidence.brand_response && (
          <div>
            <h4 className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Resolution</h4>
            <p className="text-sm text-gray-800 bg-indigo-50/30 p-3 rounded-md border border-indigo-100/50 leading-relaxed">{evidence.brand_response}</p>
          </div>
        )}
      </div>
    </div>
  );
}
