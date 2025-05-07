import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function GET() {
  const authSystem = process.env.NEXT_PUBLIC_AUTH_SYSTEM;

  if (authSystem === "email_password") {
    const store = await cookies();
    store.delete({ name: "access_token", path: "/" });
    store.delete({ name: "refresh_token", path: "/" });
  }

  const domain = process.env.FRONTEND_URL || "http://localhost:3000";
  const redirectUrl = new URL("/", domain);

  return NextResponse.redirect(redirectUrl.toString(), 302);
}
