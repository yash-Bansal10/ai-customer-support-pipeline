import { useState } from "react";
import { Check, Copy, MessageSquareText } from "lucide-react";
import { cn } from "../../lib/utils.ts";

export default function GeneratedReply({ reply }: { reply: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!reply) return;
    navigator.clipboard.writeText(reply);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!reply) return null;

  return (
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm overflow-hidden mt-6">
      <div className="border-b border-gray-100 bg-gray-50/50 px-5 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
          <MessageSquareText className="h-4 w-4 text-gray-500" />
          AI-generated response
        </div>
        <button
          onClick={handleCopy}
          className={cn(
            "flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
            copied ? "bg-emerald-100 text-emerald-700 border-emerald-200" : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
          )}
        >
          {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <div className="p-5">
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-gray-800">{reply}</p>
      </div>
    </div>
  );
}
