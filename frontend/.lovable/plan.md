

## CogniShift — Operational Console UI

An operational monitoring console for the CogniShift attention management system, connecting to the real backend API at a configurable base URL.

### Global Layout
- **Top bar**: CogniShift logo/name, connection status indicator (green dot = API reachable), configurable API base URL input
- **Tab-based navigation** across four views: Dashboard, Users, Decision Log, Simulation
- Light neutral background (#F4F6F8), thin border separators, no shadows or floating cards
- Inter font for UI, JetBrains Mono for logs/timestamps

### 1. Dashboard Overview
- **Stats row**: Total decisions today, decisions by type (sent/delayed/blocked) with colored dot indicators (green/amber/red), active users count
- **Recent decisions mini-table**: Last 10 decisions showing user, source, message snippet, decision, timestamp
- **Mode distribution**: Simple bar or count breakdown of current inferred modes across users (focus/work/meeting/relax/sleep)

### 2. User Monitor
- **Table of all users** from `GET /api/users/` with columns: Name, Role, Notification Pref, Active App, App Category, Current Block, Block Type, Status dot
- Auto-refresh on interval (configurable toggle)
- Null states shown as `—` for inactive app/block
- Click a row to expand inline details (persona description, block time range)

### 3. Decision Log
- **Full table** from `GET /api/decisions/` with columns: Timestamp, User, Source, Message, Active App, Schedule Block, Inferred Mode, Decision (color-coded dot + label), AI Reason
- Filter controls at top: by decision type (send/delay/block), by source app, by user
- Expandable rows to show full context snapshot (ignored count, last interactions, time of day)
- Monospace font for timestamps and technical fields

### 4. Simulation Control
- **Run Tick button** (single, restrained button) calling `GET /api/simulate/run/`
- **Auto-tick toggle** with interval selector (e.g., every 5s, 10s, 30s)
- **Results log panel** below, styled as a system console output (monospace, light background, scrollable)
  - Each tick result shows: user name, app rotated (yes/no), notification decision details or "no notification"
  - Newest entries at top, timestamped
- Running tick count indicator

### Data Layer
- Centralized API service module with configurable base URL (defaulting to `http://127.0.0.1:8000/api`)
- React Query for all data fetching with appropriate polling intervals
- Types strictly matching the API reference schemas
- Error states shown as inline status messages, not modals

### Interaction Design
- Subtle hover highlights on table rows
- Minimal transitions, no animations
- Toggle switches for auto-refresh and auto-tick controls
- Small colored dots (●) for decision states, not badges

