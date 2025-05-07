import AuthedLayout from "@/components/components/commons/AuthedLayout";
import ClerkLoginPage from "@/components/pages/ClerkLoginPage";
import DashboardPage from "@/components/pages/DashboardPage";
import EmailPasswordLoginPage from "@/components/pages/EmailPasswordLoginPage";
import { User } from "@/types/User";
import { apiGet } from "@/utils/api";
import { SignedIn, SignedOut } from "@clerk/nextjs";
import { redirect } from "next/navigation";


export default async function RootPage() {
  const authSystem = process.env.NEXT_PUBLIC_AUTH_SYSTEM;

  // Check if the user is already logged in
  if (authSystem === "email_password") {
    const { data } = await apiGet<User>("/users/me");
    if (data && data.uuid) {
      redirect("/dashboard");
      return;
    }
  }

  return (
    <>
      <SignedOut>
        {authSystem === "email_password" && <EmailPasswordLoginPage />}
        {authSystem === "clerk" && <ClerkLoginPage />}
      </SignedOut>
      <SignedIn>
        <AuthedLayout>
          <DashboardPage />
        </AuthedLayout>
      </SignedIn>
    </>
  );
}
