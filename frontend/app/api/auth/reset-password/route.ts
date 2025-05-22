"use server";

import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { token, new_password } = await req.json();

    if (!token || !new_password) {
      return NextResponse.json(
        { success: false, error: "Token and new password are required" },
        { status: 400 }
      );
    }

    // Call the backend API
    const apiRes = await fetch(
      `${process.env.API_BASE_URL}/api/auth/reset-password`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token, new_password }),
      }
    );

    if (!apiRes.ok) {
      const errorData = await apiRes.json();
      return NextResponse.json(
        { success: false, error: errorData },
        { status: apiRes.status }
      );
    }

    return NextResponse.json(
      { success: true, message: "パスワードが正常に更新されました" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error in reset-password route:", error);
    return NextResponse.json(
      { success: false, error: "Internal Server Error" },
      { status: 500 }
    );
  }
}