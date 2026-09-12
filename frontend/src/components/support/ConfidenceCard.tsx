import { Activity } from "lucide-react";

export default function ConfidenceCard({ confidence }: { confidence: number }) {
  const percentage = Math.round((confidence || 0) * 100);
  
  return (
    <div className="flex flex-col gap-1 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-gray-500">
        <Activity className="h-4 w-4 text-indigo-500" />
        Intent confidence
      </div>
      <div className="mt-2 text-2xl font-black tracking-tight text-gray-900">{percentage}%</div>
    </div>
  );
}
