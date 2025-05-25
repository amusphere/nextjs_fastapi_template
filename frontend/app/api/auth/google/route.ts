"use server";

import { apiGet } from "@/utils/api";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    // バックエンドからGoogle OAuth認証URLを取得
    const { data, error } = await apiGet("/google/auth-url");

    if (error) {
      console.error("Failed to get Google auth URL:", error);
      return NextResponse.json(
        { success: false, error: error.message },
        { status: error.status || 500 }
      );
    }

    // 認証URLにリダイレクト
    return NextResponse.redirect((data as { auth_url: string }).auth_url, 302);

  } catch (error) {
    console.error("Error in Google auth initiation:", error);
    return NextResponse.json(
      { success: false, error: "Internal Server Error" },
      { status: 500 }
    );
  }
}
