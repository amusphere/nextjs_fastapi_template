"use server";

import { apiGet } from "@/utils/api";
import { NextResponse } from "next/server";

export async function GET() {
  try {
    // バックエンドからGoogle連携状況を取得
    const { data, error } = await apiGet("/google/status");

    if (error) {
      return NextResponse.json(
        { connected: false, error: error.message },
        { status: error.status || 500 }
      );
    }

    return NextResponse.json(data, { status: 200 });

  } catch (error) {
    console.error("Error checking Google connection status:", error);
    return NextResponse.json(
      { connected: false, error: "Internal Server Error" },
      { status: 500 }
    );
  }
}
