"use client";

import { useUsers } from "@/lib/api/useUsers";
import { Card } from "@/components/ui/card";

export default function UsersPage() {
  const { data, isLoading } = useUsers();

  if (isLoading) return <div>Cargando usuarios...</div>;

  return (
    <Card className="p-6">
      <h1 className="text-xl font-semibold mb-4">Usuarios</h1>

      <table className="w-full text-sm">
        <thead>
          <tr className="border-b">
            <th className="text-left p-2">Email</th>
            <th className="text-left p-2">Role</th>
            <th className="text-left p-2">Status</th>
          </tr>
        </thead>

        <tbody>
          {data?.map((user: any) => (
            <tr key={user.id} className="border-b">
              <td className="p-2">{user.email}</td>
              <td className="p-2">{user.role}</td>
              <td className="p-2">{user.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}