import { User } from "@/types/User";
import { apiGet } from "@/utils/api";
import { redirect } from "next/navigation";
import { ReactNode } from "react";
import { SidebarProvider, SidebarTrigger } from "../ui/sidebar";
import AppSidebar from "./AppSidebar";

export default async function AuthedLayout({ children }: { children: ReactNode }) {
  const { data, error } = await apiGet<User>("/users/me");
  if (error && error.status === 401) {
    return redirect("/auth/signout");
  }

  return (
    <SidebarProvider>
      <AppSidebar user={data} />
      <main>
        <div className="">
          <SidebarTrigger />
          <div className="p-4">{children}</div>
        </div>
      </main>
    </SidebarProvider>
  );
}
