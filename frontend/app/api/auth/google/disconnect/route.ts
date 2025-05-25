"use server";

import { apiDelete } from "@/utils/api";
import { NextResponse } from "next/server";

export async function DELETE() {
  try {
    // バックエンドでGoogle連携を解除
    const { data, error } = await apiDelete("/google/disconnect");

    if (error) {
      return NextResponse.json(
        { success: false, error: error.message },
        { status: error.status || 500 }
      );
    }

    return NextResponse.json(data, { status: 200 });

  } catch (error) {
    console.error("Error disconnecting Google account:", error);
    return NextResponse.json(
      { success: false, error: "Internal Server Error" },
      { status: 500 }
    );
  }
}
