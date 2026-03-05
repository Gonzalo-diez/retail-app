import { useQuery } from "@tanstack/react-query";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const r = await fetch("/api/me");
      const data = await r.json();
      if (!r.ok || !data.ok) throw new Error("Not authenticated");
      return data.user;
    },
    retry: false,
  });
}