"use client";

import { Button } from "@/components/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/components/ui/form";
import { Input } from "@/components/components/ui/input";
import Link from "next/link";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

interface ForgotPasswordFormValues {
  email: string;
}

export default function ForgotPasswordPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const form = useForm<ForgotPasswordFormValues>();

  const onSubmit = async (data: ForgotPasswordFormValues) => {
    setIsSubmitting(true);
    try {
      const res = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const responseData = await res.json();

      if (res.ok && responseData.success) {
        setIsSuccess(true);
        toast.success("パスワードリセットリンクが送信されました。");
      } else {
        toast.error(responseData.error || "リクエストの処理中にエラーが発生しました。");
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("リクエストの送信中にエラーが発生しました。");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <Card className="w-1/4 text-center">
        <CardHeader>
          <CardTitle className="text-2xl my-2">パスワードをリセット</CardTitle>
          <CardDescription>
            アカウントに関連付けられたメールアドレスを入力してください。
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSuccess ? (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                パスワードリセットリンクを記載したメールを送信しました。
                メールをご確認ください。
              </p>
              <Button
                className="w-full"
                variant="outline"
                onClick={() => window.location.href = "/"}
              >
                ログイン画面に戻る
              </Button>
            </div>
          ) : (
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-4 w-full"
              >
                <FormField
                  control={form.control}
                  name="email"
                  rules={{
                    required: "メールアドレスは必須です",
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: "有効なメールアドレスを入力してください",
                    },
                  }}
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          type="email"
                          placeholder="メールアドレス"
                          disabled={isSubmitting}
                          required
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <div className="flex flex-col space-y-4">
                  <Button
                    type="submit"
                    className="w-full"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? "送信中..." : "リセットリンクを送信"}
                  </Button>
                  <Link href="/" className="text-sm text-primary hover:underline">
                    Back to Login
                  </Link>
                </div>
              </form>
            </Form>
          )}
        </CardContent>
      </Card>
    </div >
  );
}
