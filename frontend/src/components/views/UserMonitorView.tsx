import { useState } from "react";
import { useUsers } from "@/hooks/use-api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Switch } from "@/components/ui/switch";
import { formatTime } from "@/lib/format";

export function UserMonitorView() {
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const { data: users, isLoading, error } = useUsers(true, autoRefresh ? 5000 : undefined);

  return (
    <div>
      <div className="px-3 py-2 border-b border-border flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">User Monitor</span>
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          Auto-refresh
          <Switch checked={autoRefresh} onCheckedChange={setAutoRefresh} className="scale-75" />
        </label>
      </div>

      {error ? (
        <div className="p-3 text-xs text-status-block">Error: {(error as Error).message}</div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow className="text-xs">
              <TableHead className="h-8 px-3 text-xs w-8"></TableHead>
              <TableHead className="h-8 px-3 text-xs">Name</TableHead>
              <TableHead className="h-8 px-3 text-xs">Role</TableHead>
              <TableHead className="h-8 px-3 text-xs">Notif. Pref</TableHead>
              <TableHead className="h-8 px-3 text-xs">Active App</TableHead>
              <TableHead className="h-8 px-3 text-xs">App Category</TableHead>
              <TableHead className="h-8 px-3 text-xs">Current Block</TableHead>
              <TableHead className="h-8 px-3 text-xs">Block Type</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow><TableCell colSpan={8} className="text-xs text-muted-foreground">Loading…</TableCell></TableRow>
            ) : !users?.length ? (
              <TableRow><TableCell colSpan={8} className="text-xs text-muted-foreground">No users found</TableCell></TableRow>
            ) : (
              users.map((u) => (
                <>
                  <TableRow
                    key={u.id}
                    className="text-xs cursor-pointer"
                    onClick={() => setExpandedId(expandedId === u.id ? null : u.id)}
                  >
                    <TableCell className="px-3 py-1.5 text-muted-foreground">{expandedId === u.id ? "▾" : "▸"}</TableCell>
                    <TableCell className="px-3 py-1.5 font-medium">{u.name}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{u.role}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{u.notification_pref}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{u.active_app?.app_name ?? "—"}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{u.active_app?.app_category ?? "—"}</TableCell>
                    <TableCell className="px-3 py-1.5">{u.current_block?.title ?? "—"}</TableCell>
                    <TableCell className="px-3 py-1.5 font-mono">{u.current_block?.block_type ?? "—"}</TableCell>
                  </TableRow>
                  {expandedId === u.id && (
                    <TableRow key={`${u.id}-detail`} className="bg-secondary/30">
                      <TableCell colSpan={8} className="px-6 py-3">
                        <div className="text-xs space-y-1">
                          <div><span className="text-muted-foreground">Persona: </span>{u.persona_description}</div>
                          {u.current_block && (
                            <div className="font-mono text-muted-foreground">
                              Block: {formatTime(u.current_block.start_time)} – {formatTime(u.current_block.end_time)}
                            </div>
                          )}
                          {u.active_app && (
                            <div className="font-mono text-muted-foreground">
                              App active since: {formatTime(u.active_app.started_at)}
                            </div>
                          )}
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
