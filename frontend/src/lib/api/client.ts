const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

type ApiError = { status: number; message: string; details?: unknown };

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  if (!BASE_URL) throw new Error("NEXT_PUBLIC_API_BASE_URL is not set");

  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    // si vas con cookies httpOnly:
    credentials: "include",
  });

  if (!res.ok) {
    let details: unknown = undefined;
    try { details = await res.json(); } catch {}
    const err: ApiError = {
      status: res.status,
      message: `API error ${res.status} on ${path}`,
      details,
    };
    throw err;
  }

  return res.json() as Promise<T>;
}