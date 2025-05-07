"use client";

import { useForm } from "react-hook-form";
import { Button } from "../ui/button";
import { Form, FormField } from "../ui/form";
import { Input } from "../ui/input";

interface LoginFormValues {
  email: string;
  password: string;
}

export default function LoginForm() {
  const form = useForm<LoginFormValues>();

  const onSubmit = async (data: LoginFormValues) => {
    const res = await fetch("/api/auth/signin", {
      method: "POST",
      body: JSON.stringify(data),
    });

    const body = await res.json();
    console.log(body);
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
        <Button type="submit" className="w-full">
          Login
        </Button>
      </form>
    </Form>
  );
}
