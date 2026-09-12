import type { SupportRequest, SupportResponse } from "../types/support";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function analyzeMessage(message: string): Promise<SupportResponse> {
  const req: SupportRequest = { message: message.trim() };
  
  try {
    const res = await fetch(`${API_BASE_URL}/support`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req),
    });
    
    if (!res.ok) {
      throw new Error(`Server returned ${res.status}`);
    }
    
    const data = await res.json();
    return data as SupportResponse;
  } catch (error) {
    console.error("API Error:", error);
    throw new Error("Unable to analyze this request. Please check that the support API is running and try again.");
  }
}

export async function checkApiHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
