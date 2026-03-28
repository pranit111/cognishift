import type { Decision } from "@/types/api";

interface StatusDotProps {
  decision: Decision;
  className?: string;
}

const colorMap: Record<Decision, string> = {
  send: "text-status-send",
  delay: "text-status-delay",
  block: "text-status-block",
};

const labelMap: Record<Decision, string> = {
  send: "Sent",
  delay: "Delayed",
  block: "Blocked",
};

export function StatusDot({ decision, className }: StatusDotProps) {
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs ${className ?? ""}`}>
      <span className={`${colorMap[decision]} text-[10px] leading-none`}>●</span>
      <span className={colorMap[decision]}>{labelMap[decision]}</span>
    </span>
  );
}
