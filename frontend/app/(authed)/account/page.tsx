import AccountPage from "@/components/pages/AccountPage";
import { User } from "@/types/User";
import { apiGet } from "@/utils/api";
import { redirect } from "next/navigation";

export default async function UsernamePage() {
  const { data, error } = await apiGet<User>("/users/me");

  if (error && error.status === 401) {
    return redirect("/");
  }

  if (!data) {
    return redirect("/dashboard");
  }

  return <AccountPage user={data} />;
}
