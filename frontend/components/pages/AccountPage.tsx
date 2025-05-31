"use client";

import { User } from "@/types/User";
import AccountSettingCard from "./accounts/AccountSettingCard";
import PasswordChangeCard from "./accounts/PasswordChangeCard";


interface Props {
  user: User;
}

export default function AccountPage({ user }: Props) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 space-y-6">
      <AccountSettingCard user={user} />
      <PasswordChangeCard />
    </div>
  );
}
