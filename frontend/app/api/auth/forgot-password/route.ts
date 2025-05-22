"use server";

import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { email } = await req.json();

    // Call the backend API
    const apiRes = await fetch(
      `${process.env.API_BASE_URL}/api/auth/forgot-password`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      }
    );

    if (!apiRes.ok) {
      const errorText = await apiRes.text();
      return NextResponse.json(
        { success: false, error: errorText },
        { status: apiRes.status }
      );
    }

    return NextResponse.json(
      { success: true, message: "パスワードリセットリンクが送信されました" },
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
