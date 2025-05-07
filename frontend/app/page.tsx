import AuthedLayout from "@/components/components/commons/AuthedLayout";
import ClerkLoginPage from "@/components/pages/ClerkLoginPage";
import DashboardPage from "@/components/pages/DashboardPage";
import EmailPasswordLoginPage from "@/components/pages/EmailPasswordLoginPage";
import { SignedIn, SignedOut } from "@clerk/nextjs";


export default async function RootPage() {
  const auth_system = process.env.NEXT_PUBLIC_AUTH_SYSTEM;

  return (
    <>
      <SignedOut>
        {auth_system === "email_password" && <EmailPasswordLoginPage />}
        {auth_system === "clerk" && <ClerkLoginPage />}
      </SignedOut>
      <SignedIn>
        <AuthedLayout>
          <DashboardPage />
        </AuthedLayout>
      </SignedIn>
    </>
  );
}
