import { useState, useMemo } from "react";
import { useDecisions } from "@/hooks/use-api";
import { StatusDot } from "@/components/StatusDot";
import { formatDateTime } from "@/lib/format";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Decision } from "@/types/api";

export function DecisionLogView() {
  const { data: decisions, isLoading, error } = useDecisions(10000);
  const [filterDecision, setFilterDecision] = useState<string>("all");
  const [filterSource, setFilterSource] = useState<string>("all");
  const [filterUser, setFilterUser] = useState<string>("all");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const sources = useMemo(() => {
    if (!decisions) return [];
    return [...new Set(decisions.map((d) => d.notification_source))];
  }, [decisions]);

  const users = useMemo(() => {
    if (!decisions) return [];
    return [...new Set(decisions.map((d) => d.user_name))];
  }, [decisions]);

  const filtered = useMemo(() => {
    if (!decisions) return [];
    return decisions.filter((d) => {
      if (filterDecision !== "all" && d.decision !== filterDecision) return false;
      if (filterSource !== "all" && d.notification_source !== filterSource) return false;
      if (filterUser !== "all" && d.user_name !== filterUser) return false;
      return true;
    });
  }, [decisions, filterDecision, filterSource, filterUser]);

  return (
    <div>
      {/* Filters */}
      <div className="px-3 py-2 border-b border-border flex items-center gap-4">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide mr-auto">Decision Log</span>
        <FilterSelect label="Decision" value={filterDecision} onValueChange={setFilterDecision} options={[{ value: "all", label: "All" }, { value: "send", label: "Send" }, { value: "delay", label: "Delay" }, { value: "block", label: "Block" }]} />
        <FilterSelect label="Source" value={filterSource} onValueChange={setFilterSource} options={[{ value: "all", label: "All" }, ...sources.map((s) => ({ value: s, label: s }))]} />
        <FilterSelect label="User" value={filterUser} onValueChange={setFilterUser} options={[{ value: "all", label: "All" }, ...users.map((u) => ({ value: u, label: u }))]} />
      </div>

      {error ? (
        <div className="p-3 text-xs text-status-block">Error: {(error as Error).message}</div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow className="text-xs">
              <TableHead className="h-8 px-3 text-xs w-6"></TableHead>
              <TableHead className="h-8 px-3 text-xs">Timestamp</TableHead>
              <TableHead className="h-8 px-3 text-xs">User</TableHead>
              <TableHead className="h-8 px-3 text-xs">Source</TableHead>
              <TableHead className="h-8 px-3 text-xs">Message</TableHead>
              <TableHead className="h-8 px-3 text-xs">App</TableHead>
              <TableHead className="h-8 px-3 text-xs">Block</TableHead>
              <TableHead className="h-8 px-3 text-xs">Mode</TableHead>
              <TableHead className="h-8 px-3 text-xs">Decision</TableHead>
              <TableHead className="h-8 px-3 text-xs">AI Reason</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow><TableCell colSpan={10} className="text-xs text-muted-foreground">Loading…</TableCell></TableRow>
            ) : filtered.length === 0 ? (
              <TableRow><TableCell colSpan={10} className="text-xs text-muted-foreground">No decisions match filters</TableCell></TableRow>
            ) : (
              filtered.map((d) => (
                <>
                  <TableRow
                    key={d.id}
                    className="text-xs cursor-pointer"
                    onClick={() => setExpandedId(expandedId === d.id ? null : d.id)}
                  >
                    <TableCell className="px-3 py-1.5 text-muted-foreground">{expandedId === d.id ? "▾" : "▸"}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono text-muted-foreground whitespace-nowrap">{formatDateTime(d.created_at)}</TableCell>
                    <TableCell className="px-3 py-1.5">{d.user_name}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{d.notification_source}</TableCell>
                    <TableCell className="px-3 py-1.5 max-w-[180px] truncate">{d.notification_message}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{d.active_app_snapshot ?? "—"}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{d.schedule_block_snapshot ?? "—"}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{d.inferred_mode}</TableCell>
                    <TableCell className="px-3 py-1.5"><StatusDot decision={d.decision} /></TableCell>
                    <TableCell className="px-3 py-1.5 max-w-[200px] truncate text-muted-foreground">{d.ai_reason}</TableCell>
                  </TableRow>
                  {expandedId === d.id && (
                    <TableRow key={`${d.id}-detail`} className="bg-secondary/30">
                      <TableCell colSpan={10} className="px-6 py-3">
                        <div className="text-xs space-y-1 font-mono">
                          <div><span className="text-muted-foreground">Ignored count: </span>{d.recent_ignored_count}</div>
                          <div><span className="text-muted-foreground">Last interactions: </span>{d.last_interactions_snapshot?.join(", ") || "—"}</div>
                          <div><span className="text-muted-foreground">Time of day: </span>{d.time_of_day_snapshot}</div>
                          <div><span className="text-muted-foreground">App category: </span>{d.active_app_category_snapshot ?? "—"}</div>
                          {d.delay_until && <div><span className="text-muted-foreground">Delay until: </span>{formatDateTime(d.delay_until)}</div>}
                          <div className="mt-2 text-foreground font-sans"><span className="text-muted-foreground font-mono">AI reason: </span>{d.ai_reason}</div>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </>
              ))
            )}
          </TableBody>
        </Table>
      )}
    </div>
  );
}

function FilterSelect({ label, value, onValueChange, options }: { label: string; value: string; onValueChange: (v: string) => void; options: { value: string; label: string }[] }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-xs text-muted-foreground">{label}:</span>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger className="h-6 text-xs w-auto min-w-[80px] border-border bg-card">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((o) => (
            <SelectItem key={o.value} value={o.value} className="text-xs">{o.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
