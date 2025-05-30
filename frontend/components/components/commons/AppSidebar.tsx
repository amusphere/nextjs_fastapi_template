"use client"

import { User } from "@/types/User";
import { Home, LayoutDashboard, MessageCircle } from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/components/ui/sidebar";
import AppSidebarFooterContent from "./AppSidebarFooterContent";

type Props = {
  user: User;
};

const items = [
  {
    title: "Home",
    url: "/",
    icon: Home,
  },
  {
    title: "dashboard",
    url: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "chat",
    url: "/chat",
    icon: MessageCircle,
  },
]

export default function AppSidebar({ user }: Props) {
  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>
            Side Menu
          </SidebarGroupLabel>
          <SidebarGroupContent className="mt-2">
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon />
                      <span>{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <AppSidebarFooterContent user={user} />
      </SidebarFooter>
    </Sidebar>
  )
}
