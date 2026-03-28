// CogniShift API types — strictly matching API reference

export type SourceApp = "slack" | "gmail" | "github" | "calendar" | "youtube";
export type Priority = "low" | "medium" | "high";
export type Category = "social" | "work" | "urgent";
export type InferredMode = "focus" | "work" | "meeting" | "relax" | "sleep";
export type Decision = "send" | "delay" | "block";
export type AppCategory = "productivity" | "communication" | "leisure";
export type BlockType = "meeting" | "focus" | "break" | "free";
export type Action = "seen" | "ignored" | "dismissed" | "snoozed";
export type Role = "developer" | "manager" | "student" | "designer";
export type NotificationPref = "all" | "priority" | "urgent_only";

export interface ActiveApp {
  id: string;
  app_name: string;
  app_category: AppCategory;
  started_at: string;
  is_active: boolean;
}

export interface ScheduleBlock {
  id: string;
  title: string;
  block_type: BlockType;
  start_time: string;
  end_time: string;
}

export interface User {
  id: string;
  name: string;
  role: Role;
  persona_description: string;
  notification_pref: NotificationPref;
  active_app: ActiveApp | null;
  current_block: ScheduleBlock | null;
}

export interface DecisionEntry {
  id: string;
  user_name: string;
  user_role: Role;
  notification_source: SourceApp;
  notification_message: string;
  active_app_snapshot: string | null;
  active_app_category_snapshot: AppCategory | null;
  schedule_block_snapshot: BlockType | null;
  recent_ignored_count: number;
  last_interactions_snapshot: Action[];
  time_of_day_snapshot: string;
  inferred_mode: InferredMode;
  decision: Decision;
  ai_reason: string;
  delay_until: string | null;
  created_at: string;
}

export interface SimulationNotification {
  notification_id: string;
  decision: Decision;
  inferred_mode: InferredMode;
  ai_priority: Priority;
  ai_category: Category;
  ai_reason: string;
  delay_until: string | null;
}

export interface SimulationResult {
  user: string;
  app_rotated: boolean;
  notification: SimulationNotification | null;
}

export interface SimulationResponse {
  tick: string;
  results: SimulationResult[];
}
