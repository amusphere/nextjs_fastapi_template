import AuthedLayout from "@/components/components/commons/AuthedLayout";
import DashboardPage from "@/components/pages/DashboardPage";
import LoginPage from "@/components/pages/LoginPage";
import { SignedIn, SignedOut } from "@clerk/nextjs";


export default async function RootPage() {
  return (
    <>
      <SignedOut>
        <LoginPage />
      </SignedOut>
      <SignedIn>
        <AuthedLayout>
          <DashboardPage />
        </AuthedLayout>
      </SignedIn>
    </>
  );
}
