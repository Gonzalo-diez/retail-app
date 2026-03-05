import { useQuery } from "@tanstack/react-query";

export function useUsers() {
  return useQuery({
    queryKey: ["users"],
    queryFn: async () => {
      const r = await fetch("/api/users");
      if (!r.ok) throw new Error("Error loading users");
      return r.json();
    },
  });
}