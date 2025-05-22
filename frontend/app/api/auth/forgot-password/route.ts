"use server";

import { apiPost } from "@/utils/api";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { email } = await req.json();

    // Call the backend API
    const apiRes = await apiPost(
      "/auth/forgot-password",
      { email }
    );

    if (apiRes.error) {
      return NextResponse.json(
        { success: false, error: apiRes.error.message },
        { status: apiRes.error.status || 500 }
      );
    }

    return NextResponse.json(
      { success: true, message: "Password reset link has been sent" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error in forgot-password route:", error);
    return NextResponse.json(
      { success: false, error: "Internal Server Error" },
      { status: 500 }
    );
  }
}
