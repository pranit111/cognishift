import type { User, DecisionEntry, SimulationResponse } from "@/types/api";

let baseUrl = "http://127.0.0.1:8000/api";

export const getApiBaseUrl = () => baseUrl;
export const setApiBaseUrl = (url: string) => { baseUrl = url; };

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${baseUrl}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `API ${res.status}`);
  }
  return res.json();
}

export const api = {
  getUsers: () => fetchJson<User[]>("/users/"),
  getDecisions: () => fetchJson<DecisionEntry[]>("/decisions/"),
  runSimulation: () => fetchJson<SimulationResponse>("/simulate/run/"),
  checkHealth: async (): Promise<boolean> => {
    try {
      await fetch(`${baseUrl}/users/`, { method: "GET", signal: AbortSignal.timeout(3000) });
      return true;
    } catch {
      return false;
    }
  },
};
