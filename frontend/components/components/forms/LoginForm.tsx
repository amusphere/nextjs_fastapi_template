"use client";

import { useForm } from "react-hook-form";
import { toast } from "sonner";
import Link from "next/link";
import { Button } from "../ui/button";
import { Form, FormField } from "../ui/form";
import { Input } from "../ui/input";

interface LoginFormValues {
  email: string;
  password: string;
}

export default function LoginForm() {
  const form = useForm<LoginFormValues>({
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormValues) => {
    try {
      const res = await fetch("/api/auth/signin", {
        method: "POST",
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        toast.error("ログインに失敗しました。");
        return;
      }

      const responseData = await res.json();
      if (responseData.success) {
        window.location.href = "/dashboard";
      } else {
        toast.error("ログインに失敗しました。");
      }
    } catch (error) {
      console.error("Login error:", error);
      toast.error("ログインに失敗しました。");
    }
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-4 w-full"
      >
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <Input
              {...field}
              type="email"
              placeholder="Email"
              required
            />
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <Input
              {...field}
              type="password"
              placeholder="Password"
              required
            />
          )}
        />
        <div className="flex flex-col space-y-4">
          <Button type="submit" className="w-full">
            Login
          </Button>
          <div className="text-center space-y-2">
            <div>
              <Link href="/auth/forgot-password" className="text-sm text-primary hover:underline">
                Forgot Password?
              </Link>
            </div>
            <div>
              <Link href="/auth/signup" className="text-sm text-primary hover:underline">
                Create New Account
              </Link>
            </div>
          </div>
        </div>
      </form>
    </Form>
  );
}
