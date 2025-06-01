"use server";

import { apiPost } from "@/utils/api";
import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { current_password, new_password } = await req.json();

    if (!current_password || !new_password) {
      return NextResponse.json(
        { success: false, error: "Current password and new password are required" },
        { status: 400 }
      );
    }

    // Call the backend API
    const apiRes = await apiPost(
      "/auth/change-password",
      { current_password, new_password }
    );

    if (apiRes.error) {
      // Extract error message properly
      let errorMessage = "Failed to change password";

      if (typeof apiRes.error.details === 'string') {
        errorMessage = apiRes.error.details;
      } else if (apiRes.error.details && typeof apiRes.error.details === 'object' && apiRes.error.details.detail) {
        errorMessage = apiRes.error.details.detail;
      } else if (typeof apiRes.error.message === 'string') {
        errorMessage = apiRes.error.message;
      }

      return NextResponse.json(
        { success: false, error: errorMessage },
        { status: apiRes.error.status || 500 }
      );
    }

    return NextResponse.json(
      { success: true, message: "Password has been successfully changed" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Error in change-password route:", error);
    return NextResponse.json(
      { success: false, error: "Internal Server Error" },
      { status: 500 }
    );
  }
}
