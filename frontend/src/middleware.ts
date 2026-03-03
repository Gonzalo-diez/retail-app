import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(req: NextRequest) {
  const cookieName = process.env.AUTH_COOKIE_NAME || "retail_session";
  const token = req.cookies.get(cookieName)?.value;

  const { pathname } = req.nextUrl;

  const isAuthRoute = pathname.startsWith("/login") || pathname.startsWith("/api/auth");

  // Si NO está logueado y quiere entrar a app → login
  if (!token && !isAuthRoute) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    url.searchParams.set("next", pathname);
    return NextResponse.redirect(url);
  }

  // Si está logueado y entra a /login → home
  if (token && pathname.startsWith("/login")) {
    const url = req.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

// Protegemos todo menos assets y next internals
export const config = {
  matcher: ["/((?!_next|favicon.ico|assets|public).*)"],
};