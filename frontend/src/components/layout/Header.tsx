import { Sparkles } from "lucide-react";
import StatusIndicator from "./StatusIndicator.tsx";

export default function Header() {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded bg-gray-900 text-white shadow-sm">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight text-gray-900 leading-tight">Customer Support Intelligence</h1>
            <p className="text-[11px] font-medium text-gray-500 uppercase tracking-wide">Assessment Prototype</p>
          </div>
        </div>
        <StatusIndicator />
      </div>
    </header>
  );
}
