"use client";

import { Topbar } from "@/components/app/topbar";
import { Sidebar } from "@/components/app/sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex">
      <Sidebar />
      <div className="flex-1">
        <Topbar />
        <main className="mx-auto max-w-6xl p-6">{children}</main>
      </div>
    </div>
  );
}