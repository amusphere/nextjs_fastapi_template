"use client";

import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
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

interface ResetPasswordFormValues {
  new_password: string;
  confirm_password: string;
}

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const [token, setToken] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isError, setIsError] = useState(false);

  const form = useForm<ResetPasswordFormValues>({
    defaultValues: {
      new_password: "",
      confirm_password: "",
    },
  });

  useEffect(() => {
    const tokenParam = searchParams.get("token");
    if (tokenParam) {
      setToken(tokenParam);
    } else {
      setIsError(true);
      toast.error("無効なリンクです。パスワードリセットを再度リクエストしてください。");
    }
  }, [searchParams]);

  const onSubmit = async (data: ResetPasswordFormValues) => {
    if (data.new_password !== data.confirm_password) {
      form.setError("confirm_password", {
        type: "manual",
        message: "パスワードが一致しません",
      });
      return;
    }

    if (!token) {
      toast.error("トークンが見つかりません。パスワードリセットを再度リクエストしてください。");
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token,
          new_password: data.new_password,
        }),
      });

      const responseData = await res.json();

      if (res.ok && responseData.success) {
        setIsSuccess(true);
        toast.success("パスワードが正常に更新されました。");
      } else {
        let errorMessage = "パスワードのリセット中にエラーが発生しました。";
        if (responseData.error) {
          errorMessage = typeof responseData.error === 'object' && responseData.error.detail
            ? responseData.error.detail
            : String(responseData.error);
        }
        toast.error(errorMessage);
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("リクエストの送信中にエラーが発生しました。");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <Card className="w-1/4 text-center">
          <CardHeader>
            <CardTitle className="text-2xl my-2">エラー</CardTitle>
            <CardDescription>
              無効なパスワードリセットリンクです。
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                リンクが無効であるか、期限が切れています。
                新しいパスワードリセットリンクをリクエストしてください。
              </p>
              <Button
                className="w-full"
                onClick={() => window.location.href = "/auth/forgot-password"}
              >
                パスワードをリセットする
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <Card className="w-1/4 text-center">
        <CardHeader>
          <CardTitle className="text-2xl my-2">新しいパスワードを設定</CardTitle>
          <CardDescription>
            アカウントの新しいパスワードを入力してください。
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSuccess ? (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                パスワードが正常に更新されました。新しいパスワードでログインできます。
              </p>
              <Button
                className="w-full"
                onClick={() => window.location.href = "/"}
              >
                ログインする
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
                  name="new_password"
                  rules={{
                    required: "パスワードは必須です",
                    minLength: {
                      value: 8,
                      message: "パスワードは8文字以上である必要があります",
                    },
                  }}
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          type="password"
                          placeholder="新しいパスワード"
                          disabled={isSubmitting}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="confirm_password"
                  rules={{
                    required: "パスワード確認は必須です",
                  }}
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          {...field}
                          type="password"
                          placeholder="パスワードを確認"
                          disabled={isSubmitting}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "処理中..." : "パスワードを更新"}
                </Button>
              </form>
            </Form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
