# Cognishift API Reference

**Base URL:** `http://127.0.0.1:8000/api`  
**Content-Type:** `application/json` on all requests

---

## Allowed Values

| Field | Values |
|---|---|
| `source_app` | `slack` `gmail` `github` `calendar` `youtube` |
| `priority` | `low` `medium` `high` |
| `category` | `social` `work` `urgent` |
| `inferred_mode` | `focus` `work` `meeting` `relax` `sleep` |
| `decision` | `send` `delay` `block` |
| `app_category` | `productivity` `communication` `leisure` |
| `block_type` | `meeting` `focus` `break` `free` |
| `action` | `seen` `ignored` `dismissed` `snoozed` |
| `role` | `developer` `manager` `student` `designer` |
| `notification_pref` | `all` `priority` `urgent_only` |

---

## 1. POST `/api/generate-event/`
Runs the full pipeline: classify → infer mode → decide → persist.

**Body**
```json
{
  "user_id": "uuid",
  "source_app": "github",
  "message": "PR #10 approved"
}
```

**Response `201`**
```json
{
  "notification_id": "uuid",
  "decision": "send",
  "inferred_mode": "focus",
  "ai_priority": "high",
  "ai_category": "urgent",
  "ai_reason": "GitHub notification during focus session...",
  "delay_until": null
}
```
> `delay_until` is an ISO datetime string when `decision` is `delay`, otherwise `null`.

**Errors**
```
400 { "error": "user_id, source_app, and message are required." }
404 { "error": "User not found." }
500 { "error": "<exception message>" }
```

---

## 2. POST `/api/classify/`
AI classification only — no decision made, nothing saved.

**Body**
```json
{
  "message": "Build failed on main",
  "context_snapshot": {
    "source_app": "github",
    "role": "developer",
    "app_category": "productivity",
    "block_type": "focus"
  }
}
```
> All fields in `context_snapshot` are optional. Only `message` is required.

**Response `200`**
```json
{
  "priority": "high",
  "category": "urgent"
}
```

**Errors**
```
400 { "error": "message is required." }
500 { "error": "<exception message>" }
```

---

## 3. POST `/api/detect-mode/`
Reads a user's live context and infers their current mode.

**Body**
```json
{
  "user_id": "uuid"
}
```

**Response `200`**
```json
{
  "inferred_mode": "focus",
  "ai_reason": "User is in vscode during a focus block."
}
```

**Errors**
```
400 { "error": "user_id is required." }
404 { "error": "User not found." }
500 { "error": "<exception message>" }
```

---

## 4. POST `/api/decision/`
Pure rule table lookup — no AI, stateless, nothing persisted.

**Body**
```json
{
  "priority": "high",
  "inferred_mode": "focus"
}
```

**Response `200`**
```json
{
  "decision": "send",
  "delay_minutes": 0
}
```

**Errors**
```
400 { "error": "priority and inferred_mode are required." }
```

---

## 5. GET `/api/users/`
Returns all users with their current active app and schedule block.

**No body.**

**Response `200`**
```json
[
  {
    "id": "uuid",
    "name": "Alex Chen",
    "role": "developer",
    "persona_description": "...",
    "notification_pref": "priority",
    "active_app": {
      "id": "uuid",
      "app_name": "vscode",
      "app_category": "productivity",
      "started_at": "2026-03-28T10:00:00Z",
      "is_active": true
    },
    "current_block": {
      "id": "uuid",
      "title": "Deep work — API refactor",
      "block_type": "focus",
      "start_time": "2026-03-28T10:00:00Z",
      "end_time": "2026-03-28T12:00:00Z"
    }
  }
]
```
> `active_app` and `current_block` are `null` when none is active.

---

## 6. GET `/api/decisions/`
Returns the last 50 decision log entries, newest first.

**No body.**

**Response `200`**
```json
[
  {
    "id": "uuid",
    "user_name": "Alex Chen",
    "user_role": "developer",
    "notification_source": "github",
    "notification_message": "PR #10 approved",
    "active_app_snapshot": "vscode",
    "active_app_category_snapshot": "productivity",
    "schedule_block_snapshot": "focus",
    "recent_ignored_count": 0,
    "last_interactions_snapshot": ["seen", "ignored"],
    "time_of_day_snapshot": "morning",
    "inferred_mode": "focus",
    "decision": "send",
    "ai_reason": "High priority GitHub notification during focus...",
    "delay_until": null,
    "created_at": "2026-03-28T10:05:00Z"
  }
]
```

---

## 7. GET `/api/simulate/run/`
Advances one simulation tick for all users (app rotate + random notification + random interaction).

**No body.**

**Response `200`**
```json
{
  "tick": "completed",
  "results": [
    {
      "user": "Alex Chen",
      "app_rotated": true,
      "notification": {
        "notification_id": "uuid",
        "decision": "block",
        "inferred_mode": "focus",
        "ai_priority": "low",
        "ai_category": "social",
        "ai_reason": "...",
        "delay_until": null
      }
    }
  ]
}
```
> `notification` is `null` for users who did not get a notification on this tick.

**Errors**
```
500 { "error": "<exception message>" }
```

---

## 8. POST `/api/interactions/`
Logs a user interaction with a specific notification.

**Body**
```json
{
  "user_id": "uuid",
  "notification_id": "uuid",
  "action": "seen"
}
```

**Response `201`**
```json
{
  "id": "uuid",
  "action": "seen"
}
```

**Errors**
```
400 { "error": "user_id, notification_id, and action are required." }
400 { "error": "action must be one of ['seen', 'ignored', 'dismissed', 'snoozed']" }
404 { "error": "User not found." }
404 { "error": "Notification not found." }
```
