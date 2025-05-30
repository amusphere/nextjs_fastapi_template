"use server";

import { apiPost } from "@/utils/api";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

interface Token {
  access_token: string;
  expires_in: number;
  refresh_token?: string;
}

export async function POST(request: NextRequest) {
  try {
    const { username, email, password } = await request.json();

    if (!username || !email || !password) {
      return NextResponse.json(
        { success: false, error: "All fields are required" },
        { status: 400 }
      );
    }

    // Call the backend API
    const { data, error } = await apiPost("/auth/signup", {
      username,
      email,
      password,
    });    if (error) {
      let errorMessage = "Failed to create account";

      if (error.status === 400) {
        if (error.details && error.details.includes("already exists")) {
          errorMessage = "This email address is already in use";
        } else {
          errorMessage = error.details || error.message || errorMessage;
        }
      }

      return NextResponse.json(
        { success: false, error: errorMessage },
        { status: error.status || 500 }
      );
    }

    const { access_token, expires_in, refresh_token } = data as Token;

    // Set cookies for authentication
    const store = await cookies();
    store.set("access_token", access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: expires_in,
      path: "/",
    });
    store.set("refresh_token", refresh_token || "", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: expires_in,
      path: "/",
    });

    return NextResponse.json({ success: true }, { status: 201 });
  } catch (error) {
    console.error("Error in signup route:", error);
    return NextResponse.json(
      { success: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
