import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function useUsers(enabled = true, refetchInterval?: number) {
  return useQuery({
    queryKey: ["users"],
    queryFn: api.getUsers,
    enabled,
    refetchInterval: refetchInterval || false,
  });
}

export function useDecisions(refetchInterval?: number) {
  return useQuery({
    queryKey: ["decisions"],
    queryFn: api.getDecisions,
    refetchInterval: refetchInterval || false,
  });
}

export function useSimulation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: api.runSimulation,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] });
      qc.invalidateQueries({ queryKey: ["decisions"] });
    },
  });
}

export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: api.checkHealth,
    refetchInterval: 10000,
  });
}
