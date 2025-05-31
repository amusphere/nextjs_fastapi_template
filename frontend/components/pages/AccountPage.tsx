"use client";

import { Button } from "@/components/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle
} from "@/components/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/components/ui/form";
import { Input } from "@/components/components/ui/input";
import { User } from "@/types/User";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

interface UpdateFormValues {
  name: string;
}

interface Props {
  user: User;
}

export default function AccountPage({ user }: Props) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<UpdateFormValues>({
    defaultValues: {
      name: user.name || "",
    },
  });

  const onSubmit = async (data: UpdateFormValues) => {
    setIsSubmitting(true);
    try {
      const res = await fetch("/api/users/me", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const responseData = await res.json();

      if (res.ok && responseData.success) {
        toast.success("Save successfully");
        form.setValue("name", data.name);
      } else {
        toast.error(responseData.error || "Failed to save.");
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("An unexpected error occurred while saving.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">Account Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit(onSubmit)}
              className="space-y-4 w-full"
            >
              <FormField
                control={form.control}
                name="name"
                rules={{
                  required: "Username is required",
                  minLength: {
                    value: 2,
                    message: "Username must be at least 2 characters",
                  },
                  maxLength: {
                    value: 50,
                    message: "Username must be less than 50 characters",
                  },
                }}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Username</FormLabel>
                    <FormControl>
                      <Input
                        {...field}
                        type="text"
                        placeholder="Enter your username"
                        disabled={isSubmitting}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex flex-col space-y-2">
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Saving..." : "Save"}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
