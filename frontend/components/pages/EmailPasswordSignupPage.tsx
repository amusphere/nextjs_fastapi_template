import SignupForm from "../components/forms/SignupForm";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

export default function EmailPasswordSignupPage() {
  return (
    <>
      <div className="flex flex-col items-center justify-center min-h-screen p-2">
        <Card className="w-full max-w-md text-center">
          <CardHeader>
            <CardTitle className="text-2xl my-2">
              Create Account
            </CardTitle>
            <CardDescription>
              Create a new account to get started
            </CardDescription>
          </CardHeader>
          <CardContent>
            <SignupForm />
          </CardContent>
        </Card>
      </div>
    </>
  );
}
