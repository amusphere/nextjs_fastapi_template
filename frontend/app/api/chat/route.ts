import { apiPost } from "@/utils/api";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const { prompt } = await req.json();
  const { data, error } = await apiPost<{ response: string }>("/chat", { prompt });

  if (error) {
    return NextResponse.json(
      { message: error.message },
      { status: error.status || 500 }
    );
  }

  return NextResponse.json(data);
}
