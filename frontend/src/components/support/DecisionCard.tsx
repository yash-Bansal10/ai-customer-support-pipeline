import { ShieldCheck, AlertOctagon } from "lucide-react";
import { cn } from "../../lib/utils.ts";

export default function DecisionCard({ decision }: { decision: string }) {
  const isAuto = decision === "AUTO" || decision === "AUTO-HANDLE";
  
  return (
    <div className={cn(
      "flex flex-col gap-1 rounded-xl border p-5 shadow-sm",
      isAuto ? "border-emerald-200 bg-emerald-50/30" : "border-amber-200 bg-amber-50/30"
    )}>
      <div className={cn(
        "flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider",
        isAuto ? "text-emerald-700" : "text-amber-700"
      )}>
        {isAuto ? <ShieldCheck className="h-4 w-4" /> : <AlertOctagon className="h-4 w-4" />}
        Automation decision
      </div>
      <div className={cn(
        "mt-2 text-lg font-black tracking-tight",
        isAuto ? "text-emerald-900" : "text-amber-900"
      )}>
        {decision || "ESCALATE"}
      </div>
      <div className={cn(
        "text-xs font-semibold mt-1",
        isAuto ? "text-emerald-600" : "text-amber-600"
      )}>
        {isAuto ? "Safe to automate" : "Human review required"}
      </div>
    </div>
  );
}
