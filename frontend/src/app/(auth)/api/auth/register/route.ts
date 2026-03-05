import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json();

  const apiBase = process.env.API_BASE_URL!;
  const cookieName = process.env.AUTH_COOKIE_NAME || "retail_session";

  const r = await fetch(`${apiBase}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  // si falla, devolvemos el error del backend
  if (!r.ok) {
    let details: unknown = null;
    try { details = await r.json(); } catch {}
    return NextResponse.json({ ok: false, details }, { status: r.status });
  }

  const data = await r.json();

  const token = data.access_token || data.token;

  const res = NextResponse.json({ ok: true, user: data.user ?? data ?? null });

  // Si el backend devuelve token en register
  if (token) {
    res.cookies.set(cookieName, token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
    });
  }

  return res;
}