"use server";

import { apiPost } from "@/utils/api";
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
    const apiRes = await apiPost(
      "/auth/reset-password",
      { token, new_password }
    );

    if (apiRes.error) {
      return NextResponse.json(
        { success: false, error: apiRes.error.details || apiRes.error.message },
        { status: apiRes.error.status || 500 }
      );
    }

    return NextResponse.json(
      { success: true, message: "Password has been successfully updated" },
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