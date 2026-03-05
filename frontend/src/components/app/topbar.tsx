"use client";

import { Button } from "@/components/ui/button";
import { useMe } from "@/lib/api/useMe";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export function Topbar() {
  const router = useRouter();
  const { data: me, isLoading } = useMe();

  async function onLogout() {
    await fetch("/api/auth/logout", { method: "POST" });
    toast.success("Sesión cerrada");
    router.replace("/login");
    router.refresh();
  }

  return (
    <div className="border-b px-4 py-3 flex items-center justify-between">
      <div className="font-semibold">Retail App</div>

      <div className="flex items-center gap-3">
        <div className="text-sm text-muted-foreground">
          {isLoading ? "..." : me?.email}
        </div>
        <Button variant="outline" onClick={onLogout}>
          Salir
        </Button>
      </div>
    </div>
  );
}