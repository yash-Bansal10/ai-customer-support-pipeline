import { Target } from "lucide-react";

export default function IntentCard({ intent }: { intent: string }) {
  return (
    <div className="flex flex-col gap-1 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-gray-500">
        <Target className="h-4 w-4 text-indigo-500" />
        Detected intent
      </div>
      <div className="mt-2 font-mono text-lg font-bold tracking-tight text-gray-900">{intent || "UNKNOWN"}</div>
    </div>
  );
}
