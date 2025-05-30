import { User } from "@/types/User";
import { apiGet } from "@/utils/api";
import { redirect } from "next/navigation";
import { ReactNode } from "react";
import { SidebarProvider, SidebarTrigger } from "../ui/sidebar";
import AppSidebar from "./AppSidebar";

export default async function AuthedLayout({ children }: { children: ReactNode }) {
  const { data, error } = await apiGet<User>("/users/me");
  if (error && error.status === 401) {
    return redirect("/");
  }

  return (
    <SidebarProvider>
      <AppSidebar user={data} />
      <main className="flex-1 w-full">
        <div className="flex flex-col min-h-screen">
          <div className="md:p-2">
            <SidebarTrigger />
          </div>
          <div className="flex-1 overflow-y-auto p-2">{children}</div>
        </div>
      </main>
    </SidebarProvider>
  );
}
