import { useState, useEffect } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import ExamplePrompts from "./ExamplePrompts.tsx";
import { cn } from "../../lib/utils.ts";

export default function MessageInput({ onAnalyze, isLoading, defaultMsg = "" }: { onAnalyze: (msg: string) => void, isLoading: boolean, defaultMsg?: string }) {
  const [message, setMessage] = useState(defaultMsg);
  const [error, setError] = useState("");

  useEffect(() => {
    if (defaultMsg) setMessage(defaultMsg);
  }, [defaultMsg]);

  const handleAnalyze = () => {
    if (!message.trim()) {
      setError("Please enter a customer message.");
      return;
    }
    setError("");
    onAnalyze(message);
  };

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-gray-900">Customer message</h2>
        <p className="text-sm text-gray-500 mt-1">Enter a customer request to analyze its intent, retrieve similar cases, and generate a grounded response.</p>
      </div>
      
      <div className="relative">
        <textarea
          value={message}
          onChange={(e) => { setMessage(e.target.value); setError(""); }}
          placeholder="My iPhone screen is cracked and I need a repair."
          className={cn(
            "w-full min-h-[140px] resize-y rounded-lg border bg-gray-50/50 p-4 text-sm outline-none transition-all focus:border-gray-400 focus:bg-white focus:ring-4 focus:ring-gray-100",
            error ? "border-rose-300 focus:border-rose-400 focus:ring-rose-50" : "border-gray-200"
          )}
          maxLength={1000}
        />
        <div className="absolute bottom-4 right-4 text-xs font-medium text-gray-400">
          {message.length} / 1000
        </div>
      </div>
      
      {error && <p className="mt-2 text-xs font-medium text-rose-600">{error}</p>}
      
      <ExamplePrompts onSelect={(m) => { setMessage(m); setError(""); }} disabled={isLoading} />
      
      <div className="mt-6 flex justify-end">
        <button
          onClick={handleAnalyze}
          disabled={isLoading || !message.trim()}
          className="flex items-center gap-2 rounded-lg bg-gray-900 px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:bg-gray-800 focus:ring-4 focus:ring-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              Analyze
            </>
          )}
        </button>
      </div>
    </div>
  );
}
