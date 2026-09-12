import { cn } from "../../lib/utils.ts";

const EXAMPLES = [
  { label: "Billing issue", message: "I was charged twice for my subscription this month." },
  { label: "Password issue", message: "I can't reset my password and I'm locked out of my account." },
  { label: "Device issue", message: "My iPhone screen is cracked and I need a repair." },
  { label: "Delivery issue", message: "My order hasn't arrived yet. Can you check the status?" },
];

export default function ExamplePrompts({ onSelect, disabled }: { onSelect: (msg: string) => void, disabled: boolean }) {
  return (
    <div className="mt-4 flex flex-wrap gap-2 items-center">
      <span className="text-xs font-medium text-gray-500 mr-1">Try an example:</span>
      {EXAMPLES.map((ex) => (
        <button
          key={ex.label}
          disabled={disabled}
          onClick={() => onSelect(ex.message)}
          className={cn(
            "rounded border border-gray-200 bg-white px-2.5 py-1 text-xs font-medium text-gray-600 shadow-sm transition-colors",
            disabled ? "opacity-50 cursor-not-allowed" : "hover:bg-gray-50 hover:text-gray-900"
          )}
        >
          {ex.label}
        </button>
      ))}
    </div>
  );
}
