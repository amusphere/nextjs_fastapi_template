import { apiPostUrlEncoded } from "@/utils/api";
import { NextRequest, NextResponse } from "next/server";


export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  const params = new URLSearchParams();
  params.append("username", email);
  params.append("email", email);
  params.append("password", password);

  const res = await apiPostUrlEncoded("/auth/signin", params);

  return NextResponse.json(res);
}
