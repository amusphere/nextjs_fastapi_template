import { ChatPromptResponse } from "@/types/Chat";
import { apiPost } from "@/utils/api";
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { data, error } = await apiPost<ChatPromptResponse>('/chats/prompt', await request.json());

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json(data);
}
