import LoginForm from "../components/forms/LoginForm";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

export default function EmailPasswordLoginPage() {
  return (
    <>
      <div className="flex flex-col items-center justify-center min-h-screen">
        <Card className="w-full max-w-md text-center">
          <CardHeader>
            <CardTitle className="text-2xl my-2">
              {process.env.APP_NAME}
            </CardTitle>
            <CardDescription>
              A template for building Next.js applications.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LoginForm />
          </CardContent>
        </Card>
      </div>
    </>
  );
}
