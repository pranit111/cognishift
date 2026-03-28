import { useDecisions, useUsers } from "@/hooks/use-api";
import { StatusDot } from "@/components/StatusDot";
import { formatTimestamp } from "@/lib/format";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { Decision, InferredMode } from "@/types/api";

export function DashboardView() {
  const { data: decisions, isLoading: loadingD, error: errorD } = useDecisions(15000);
  const { data: users, isLoading: loadingU } = useUsers(true, 15000);

  const today = new Date().toISOString().slice(0, 10);
  const todayDecisions = decisions?.filter((d) => d.created_at.startsWith(today)) ?? [];

  const counts: Record<Decision, number> = { send: 0, delay: 0, block: 0 };
  todayDecisions.forEach((d) => counts[d.decision]++);

  const modeDistribution: Record<string, number> = {};
  if (decisions) {
    decisions.forEach((d) => {
      modeDistribution[d.inferred_mode] = (modeDistribution[d.inferred_mode] || 0) + 1;
    });
  }

  const recent = decisions?.slice(0, 10) ?? [];

  return (
    <div className="space-y-0">
      {/* Stats Row */}
      <div className="grid grid-cols-5 border-b border-border">
        <StatCell label="Total Decisions Today" value={todayDecisions.length} loading={loadingD} />
        <StatCell label="Sent" value={counts.send} loading={loadingD} dotColor="text-status-send" />
        <StatCell label="Delayed" value={counts.delay} loading={loadingD} dotColor="text-status-delay" />
        <StatCell label="Blocked" value={counts.block} loading={loadingD} dotColor="text-status-block" />
        <StatCell label="Active Users" value={users?.length ?? 0} loading={loadingU} />
      </div>

      <div className="grid grid-cols-3">
        {/* Recent Decisions */}
        <div className="col-span-2 border-r border-border">
          <div className="px-3 py-2 border-b border-border">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Recent Decisions</span>
          </div>
          {errorD ? (
            <div className="p-3 text-xs text-status-block">Error: {(errorD as Error).message}</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="text-xs">
                  <TableHead className="h-8 px-3 text-xs">Time</TableHead>
                  <TableHead className="h-8 px-3 text-xs">User</TableHead>
                  <TableHead className="h-8 px-3 text-xs">Source</TableHead>
                  <TableHead className="h-8 px-3 text-xs">Message</TableHead>
                  <TableHead className="h-8 px-3 text-xs">Decision</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loadingD ? (
                  <TableRow><TableCell colSpan={5} className="text-xs text-muted-foreground">Loading…</TableCell></TableRow>
                ) : recent.length === 0 ? (
                  <TableRow><TableCell colSpan={5} className="text-xs text-muted-foreground">No decisions yet</TableCell></TableRow>
                ) : (
                  recent.map((d) => (
                    <TableRow key={d.id} className="text-xs">
                      <TableCell className="px-3 py-1.5 font-mono text-xs text-muted-foreground">{formatTimestamp(d.created_at)}</TableCell>
                      <TableCell className="px-3 py-1.5">{d.user_name}</TableCell>
                      <TableCell className="px-3 py-1.5 font-mono text-xs">{d.notification_source}</TableCell>
                      <TableCell className="px-3 py-1.5 max-w-[200px] truncate">{d.notification_message}</TableCell>
                      <TableCell className="px-3 py-1.5"><StatusDot decision={d.decision} /></TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </div>

        {/* Mode Distribution */}
        <div>
          <div className="px-3 py-2 border-b border-border">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Mode Distribution</span>
          </div>
          <div className="p-3 space-y-2">
            {(["focus", "work", "meeting", "relax", "sleep"] as InferredMode[]).map((mode) => {
              const count = modeDistribution[mode] || 0;
              const total = decisions?.length || 1;
              const pct = Math.round((count / total) * 100);
              return (
                <div key={mode} className="flex items-center gap-2 text-xs">
                  <span className="w-14 font-mono text-muted-foreground">{mode}</span>
                  <div className="flex-1 h-3 bg-secondary rounded-sm overflow-hidden">
                    <div className="h-full bg-primary/40 rounded-sm" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="w-8 text-right font-mono text-muted-foreground">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCell({ label, value, loading, dotColor }: { label: string; value: number; loading: boolean; dotColor?: string }) {
  return (
    <div className="px-4 py-3 border-r border-border last:border-r-0">
      <div className="text-xs text-muted-foreground mb-0.5 flex items-center gap-1.5">
        {dotColor && <span className={`${dotColor} text-[10px] leading-none`}>●</span>}
        {label}
      </div>
      <div className="text-lg font-semibold tabular-nums">{loading ? "—" : value}</div>
    </div>
  );
}
