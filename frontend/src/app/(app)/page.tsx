"use client";

import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <Card className="p-6 flex items-center justify-between">
      <div>
        <h1 className="text-xl font-semibold">Retail App</h1>
        <p className="text-sm text-muted-foreground">
          Dashboard inicial. Elegí una sección para continuar.
        </p>
      </div>

      <div className="flex gap-2">
        <Button asChild variant="outline">
          <Link href="/runs">Runs</Link>
        </Button>
        <Button asChild>
          <Link href="/uploads">Uploads</Link>
        </Button>
      </div>
    </Card>
  );
}