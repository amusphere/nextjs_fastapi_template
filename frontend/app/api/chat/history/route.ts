import { apiDelete, apiGet } from "@/utils/api";
import { NextRequest, NextResponse } from "next/server";

// GET /api/chat/history -> バックエンドの /api/chat/history を転送
export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const limit = searchParams.get("limit") ?? undefined;
  const query = limit ? `?limit=${encodeURIComponent(limit)}` : "";

  const { data, error } = await apiGet(`/chat/history${query}`);
  if (error) {
    return NextResponse.json(
      { message: error.message },
      { status: error.status || 500 }
    );
  }
  return NextResponse.json(data);
}

// DELETE /api/chat/history -> バックエンドの /api/chat/history を転送
export async function DELETE() {
  const { error } = await apiDelete("/chat/history");
  if (error) {
    return NextResponse.json(
      { message: error.message },
      { status: error.status || 500 }
    );
  }
  return new NextResponse(null, { status: 204 });
}

