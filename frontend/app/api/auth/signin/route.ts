import { apiPostUrlEncoded } from "@/utils/api";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";


interface Token {
  access_token: string;
  expires_in: number;
  refresh_token?: string;
}

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();
  const params = new URLSearchParams();
  params.append("username", email);
  params.append("email", email);
  params.append("password", password);

  const { data } = await apiPostUrlEncoded("/auth/signin", params);

  const { access_token, expires_in, refresh_token } = data as Token;

  const store = await cookies();
  store.set("access_token", access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: expires_in,
    path: "/",
  });
  store.set("refresh_token", refresh_token || "", {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: expires_in,
    path: "/",
  });

  return NextResponse.json({ success: true }, { status: 200 });
}
