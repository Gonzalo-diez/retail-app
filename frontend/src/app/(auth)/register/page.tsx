"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import Link from "next/link";

export default function RegisterPage() {
  const router = useRouter();

  const [tenant_name, setTenantName] = useState("admin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      const r = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tenant_name,
          email,
          password,
        }),
      });

      const data = await r.json();

      if (!r.ok || !data.ok) {
        toast.error("No se pudo registrar");
        return;
      }

      toast.success("Usuario creado");

      // si register ya te dejó logueado (token cookie), te mando directo al home
      // si no, te mando a /login
      router.replace("/");
    } catch {
      toast.error("Error de red");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <Card className="w-full max-w-sm p-6">
        <h1 className="text-xl font-semibold">Crear cuenta</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Registrá un usuario para tu tenant.
        </p>

        <form className="mt-6 space-y-4" onSubmit={onSubmit}>
          <div className="space-y-2">
            <Label>Tenant</Label>
            <Input value={tenant_name} onChange={(e) => setTenantName(e.target.value)} />
          </div>

          <div className="space-y-2">
            <Label>Email</Label>
            <Input value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>

          <div className="space-y-2">
            <Label>Password</Label>
            <Input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <Button className="w-full" disabled={loading}>
            {loading ? "Creando..." : "Crear cuenta"}
          </Button>

          <p className="text-sm text-muted-foreground text-center">
            ¿Ya tenés cuenta?{" "}
            <Link className="underline" href="/login">
              Ingresar
            </Link>
          </p>
        </form>
      </Card>
    </div>
  );
}