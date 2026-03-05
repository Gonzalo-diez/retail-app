import { NextResponse } from "next/server";
import { cookies } from "next/headers";

export async function GET() {
  const apiBase = process.env.API_BASE_URL!;
  const cookieName = process.env.AUTH_COOKIE_NAME || "retail_session";

  const cookieStore = await cookies();
  const token = cookieStore.get(cookieName)?.value;

  if (!token) {
    return NextResponse.json({ ok: false }, { status: 401 });
  }

  const r = await fetch(`${apiBase}/users/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await r.json();

  return NextResponse.json(data, { status: r.status });
}