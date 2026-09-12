import type { Evidence } from "../../types/support.ts";
import EvidenceCard from "./EvidenceCard.tsx";
import { Database } from "lucide-react";

export default function EvidenceSection({ evidenceList }: { evidenceList: Evidence[] }) {
  return (
    <div className="mt-10">
      <div className="mb-5">
        <h3 className="flex items-center gap-2 text-lg font-semibold text-gray-900">
          <Database className="h-4 w-4 text-gray-400" />
          Retrieved evidence
        </h3>
        <p className="text-sm text-gray-500 mt-1">Historical support cases used to ground the generated response.</p>
      </div>
      
      {!evidenceList || evidenceList.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-8 text-center text-sm font-medium text-gray-500">
          No relevant historical evidence was found.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {evidenceList.map((evidence, idx) => (
            <EvidenceCard key={evidence.conversation_id || idx} evidence={evidence} />
          ))}
        </div>
      )}
    </div>
  );
}
