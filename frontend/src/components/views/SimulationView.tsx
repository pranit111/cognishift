import { useState, useCallback, useRef, useEffect } from "react";
import { useSimulation } from "@/hooks/use-api";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { StatusDot } from "@/components/StatusDot";
import type { SimulationResponse } from "@/types/api";

interface LogEntry {
  tick: number;
  timestamp: string;
  data: SimulationResponse;
}

export function SimulationView() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [tickCount, setTickCount] = useState(0);
  const [autoTick, setAutoTick] = useState(false);
  const [interval, setInterval_] = useState("5000");
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const simulation = useSimulation();

  const runTick = useCallback(async () => {
    try {
      const data = await simulation.mutateAsync();
      const newTick = tickCount + 1;
      setTickCount(newTick);
      setLogs((prev) => [{
        tick: newTick,
        timestamp: new Date().toISOString(),
        data,
      }, ...prev].slice(0, 100));
    } catch {
      // error handled by mutation state
    }
  }, [simulation, tickCount]);

  useEffect(() => {
    if (autoTick) {
      timerRef.current = setInterval(runTick, parseInt(interval));
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [autoTick, interval, runTick]);

  return (
    <div>
      {/* Controls */}
      <div className="px-3 py-2 border-b border-border flex items-center gap-4">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Simulation Control</span>
        <Button
          variant="outline"
          size="sm"
          className="h-7 text-xs px-3 border-border"
          onClick={runTick}
          disabled={simulation.isPending}
        >
          {simulation.isPending ? "Running…" : "Run Tick"}
        </Button>
        <div className="flex items-center gap-2 text-xs text-muted-foreground ml-2">
          Auto-tick
          <Switch checked={autoTick} onCheckedChange={setAutoTick} className="scale-75" />
        </div>
        {autoTick && (
          <Select value={interval} onValueChange={setInterval_}>
            <SelectTrigger className="h-6 text-xs w-auto min-w-[70px] border-border bg-card">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="3000" className="text-xs">3s</SelectItem>
              <SelectItem value="5000" className="text-xs">5s</SelectItem>
              <SelectItem value="10000" className="text-xs">10s</SelectItem>
              <SelectItem value="30000" className="text-xs">30s</SelectItem>
            </SelectContent>
          </Select>
        )}
        <span className="ml-auto text-xs font-mono text-muted-foreground">Ticks: {tickCount}</span>
      </div>

      {simulation.error && (
        <div className="px-3 py-2 text-xs text-status-block border-b border-border">
          Error: {(simulation.error as Error).message}
        </div>
      )}

      {/* Console Log */}
      <div className="h-[calc(100vh-140px)] overflow-y-auto bg-card">
        {logs.length === 0 ? (
          <div className="p-4 text-xs text-muted-foreground font-mono">Waiting for simulation ticks…</div>
        ) : (
          <div className="divide-y divide-border">
            {logs.map((entry, i) => (
              <div key={i} className="px-3 py-2 font-mono text-xs space-y-0.5">
                <div className="text-muted-foreground">
                  [{entry.timestamp.split("T")[1]?.slice(0, 8)}] tick #{entry.tick}
                </div>
                {entry.data.results.map((r, j) => (
                  <div key={j} className="pl-4 flex items-center gap-2">
                    <span className="text-foreground">{r.user}</span>
                    <span className="text-muted-foreground">app_rotated={r.app_rotated ? "yes" : "no"}</span>
                    {r.notification ? (
                      <>
                        <StatusDot decision={r.notification.decision} />
                        <span className="text-muted-foreground">{r.notification.inferred_mode}</span>
                        <span className="text-muted-foreground">{r.notification.ai_priority}/{r.notification.ai_category}</span>
                      </>
                    ) : (
                      <span className="text-muted-foreground">no notification</span>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
