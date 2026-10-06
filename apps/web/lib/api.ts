export const apiBase = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBase}/api${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${response.status} ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function apiSend<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${apiBase}/api${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}
