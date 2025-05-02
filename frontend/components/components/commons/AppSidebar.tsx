"use client"

import { Home, LayoutDashboard } from "lucide-react"

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
} from "@/components/components/ui/sidebar"
import { UserButton } from "@clerk/nextjs"

const items = [
  {
    title: "Home",
    url: "/",
    icon: Home,
  },
  {
    title: "dashboard",
    url: "/",
    icon: LayoutDashboard,
  },
]

export default function AppSidebar() {
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
        <div className="flex items-center gap-4 p-2">
          <UserButton appearance={{
            elements: {
              userButtonBox: {
                flexDirection: "row-reverse",
              },
            },
          }} showName={true} />
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
