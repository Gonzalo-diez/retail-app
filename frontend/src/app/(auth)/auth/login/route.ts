import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json();

  const apiBase = process.env.API_BASE_URL!;
  const cookieName = process.env.AUTH_COOKIE_NAME || "retail_session";

  const r = await fetch(`${apiBase}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!r.ok) {
    const err = await safeJson(r);
    return NextResponse.json(
      { ok: false, error: err ?? "Login failed" },
      { status: r.status }
    );
  }

  const data = await r.json();

  const token = data.access_token || data.token;
  if (!token) {
    return NextResponse.json(
      { ok: false, error: "Token not found in backend response" },
      { status: 500 }
    );
  }

  const res = NextResponse.json({ ok: true, user: data.user ?? null });

  res.cookies.set(cookieName, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24,
  });

  return res;
}

async function safeJson(r: Response) {
  try {
    return await r.json();
  } catch {
    return null;
  }
}