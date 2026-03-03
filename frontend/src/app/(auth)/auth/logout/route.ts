import { NextResponse } from "next/server";

export async function POST() {
  const cookieName = process.env.AUTH_COOKIE_NAME || "retail_session";

  const res = NextResponse.json({ ok: true });
  res.cookies.set(cookieName, "", {
    httpOnly: true,
    expires: new Date(0),
    path: "/",
  });
  return res;
}