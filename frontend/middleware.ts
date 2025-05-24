import { NextFetchEvent, NextRequest, NextResponse } from 'next/server';

const authSystem = process.env.NEXT_PUBLIC_AUTH_SYSTEM;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let clerkMiddleware: any = null;
try {
  if (authSystem === 'clerk') {
    // Import Clerk only when needed, but always at the top level for detection
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { clerkMiddleware: clerk } = require('@clerk/nextjs/server');
    clerkMiddleware = clerk;
  }
} catch {
  // Clerk not available, ignore
}

export default async function middleware(request: NextRequest, event: NextFetchEvent) {
  if (authSystem === 'clerk' && clerkMiddleware) {
    return clerkMiddleware(() => {
      // Basic middleware - no custom logic needed
    })(request, event);
  }

  // For other auth systems or no auth, just continue
  return NextResponse.next();
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}