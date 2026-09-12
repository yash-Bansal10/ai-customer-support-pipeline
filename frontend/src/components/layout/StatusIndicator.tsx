import { useEffect, useState } from "react";
import { checkApiHealth } from "../../lib/api.ts";

export default function StatusIndicator() {
  const [isOnline, setIsOnline] = useState<boolean | null>(null);

  useEffect(() => {
    checkApiHealth().then(setIsOnline);
  }, []);

  return (
    <div className="flex items-center gap-2 text-xs font-medium">
      {isOnline === null ? (
        <span className="text-gray-400">Checking API...</span>
      ) : (
        <>
          <span className="text-gray-600">{isOnline ? "API Online" : "API Offline"}</span>
          <span className={`relative flex h-2 w-2 ${isOnline ? "text-emerald-500" : "text-rose-500"}`}>
            {isOnline && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-75"></span>}
            <span className="relative inline-flex h-2 w-2 rounded-full bg-current"></span>
          </span>
        </>
      )}
    </div>
  );
}
