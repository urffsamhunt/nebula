"use client"

import * as React from "react";

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

type NavMainProps = {
  items: {
    title: string;
    url: string;
    icon: React.ElementType;
  }[];
  activeItem: string;
  onItemClick: (title: string) => void;
};

export function NavMain({ items, activeItem, onItemClick }: NavMainProps) {
  return (
    <SidebarGroup>
      <SidebarGroupContent className="flex flex-col gap-1 p-1">
        <SidebarMenu>
          {items.map((item) => (
            <SidebarMenuItem key={item.title}>
              {/* ✨ 2. Added onClick handler and conditional styling */}
              <SidebarMenuButton
                onClick={() => onItemClick(item.title)}
                tooltip={item.title}
                className={
                  activeItem === item.title
                    ? "bg-primary text-primary-foreground hover:bg-primary/90" // Style for the active item
                    : "hover:bg-accent" // Style for inactive items
                }
              >
                {/* Ensure the icon is rendered correctly */}
                <item.icon className="size-5" />
                <span>{item.title}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}