import { format } from "date-fns";

export function formatTimestamp(iso: string) {
  try {
    return format(new Date(iso), "HH:mm:ss");
  } catch {
    return iso;
  }
}

export function formatDateTime(iso: string) {
  try {
    return format(new Date(iso), "yyyy-MM-dd HH:mm:ss");
  } catch {
    return iso;
  }
}

export function formatTime(iso: string) {
  try {
    return format(new Date(iso), "HH:mm");
  } catch {
    return iso;
  }
}
