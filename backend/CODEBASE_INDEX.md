# Cognishift Codebase Index

## 1) System Overview
- Framework: Django + Django REST Framework.
- Project package: cognishift.
- Main app: notifications.
- Core behavior: incoming notification -> context snapshot -> AI classify/infer mode -> rule decision -> decision log.

## 2) Project Structure
- manage.py: Django entry point.
- cognishift/settings.py: app settings, keys, CORS, DB.
- cognishift/urls.py: root routing.
- notifications/models.py: domain models.
- notifications/views.py: API endpoints.
- notifications/pipeline.py: main orchestration.
- notifications/ai_service.py: LLM integration + fallback + decision rules.
- notifications/simulation.py: synthetic activity generator.
- notifications/serializers.py: DRF serializers.
- notifications/management/commands/seed.py: demo data seeding.

## 3) Domain Models
- User: role, persona, notification preference, optional telegram chat id.
- AppSession: active/ended app usage snapshots.
- ScheduleBlock: meeting/focus/break/free windows.
- NotificationEvent: raw incoming notifications and AI labels.
- UserInteractionLog: seen/ignored/dismissed/snoozed actions.
- DecisionLog: final send/delay/block plus context snapshots and AI reason.

## 4) API Surface (/api/)
- POST generate-event/: full pipeline.
- POST classify/: classification only from provided context.
- POST detect-mode/: infer mode from built context.
- POST decision/: pure rule lookup.
- GET users/: users with active app + current block.
- GET decisions/: recent decision logs.
- GET simulate/run/: one simulation tick over all users.
- POST interactions/: store user interaction.

## 5) Processing Pipeline
1. Build context from user, active app, schedule block, recent interactions, ignored count, and time of day.
2. Create NotificationEvent.
3. Run AI classify_and_infer (OpenAI first, Gemini second, rule fallback).
4. Persist AI priority/category to NotificationEvent.
5. Apply deterministic decision table by (mode, priority).
6. Persist DecisionLog with snapshots and optional delay_until.
7. Return payload to API caller.

## 6) AI + Rule Logic
- AI prompt asks for: priority, category, inferred_mode, ai_reason.
- Mode space: focus, work, meeting, relax, sleep.
- Priority space: low, medium, high.
- Category space: social, work, urgent.
- Fallback mode heuristics use block type, time of day, app category, ignored count.
- Decision table in ai_service.py maps (mode, priority) to send/delay/block.

## 7) Simulation Behavior
- For each user on each tick:
  - 50% chance rotate active app.
  - 30% chance generate notification through full pipeline.
  - attempt to log interaction for recent uninteracted notifications.
- App switching is role-weighted (developer/manager/student/designer).

## 8) Seed Command
- Command: python manage.py seed
- Clears existing User, AppSession, ScheduleBlock records.
- Creates four demo personas with schedules and active app sessions.

## 9) Settings Notes
- Secret key from DJANGO_SECRET_KEY env var.
- AI keys: OPENAI_API_KEY and GEMINI_API_KEY.
- DEBUG is True.
- SQLite is default database.
- CORS allows localhost:5173 for frontend dev.

## 10) Quick Onboarding Path
1. Read models.py and pipeline.py first.
2. Run seed command.
3. Hit POST /api/generate-event/ and inspect DecisionLog entries.
4. Run GET /api/simulate/run/ repeatedly to see dynamics.
5. Read ai_service.py for AI and decision-table behavior.

## 11) Current Gaps To Keep In Mind
- tests.py is currently minimal/empty (no automated coverage yet).
- API endpoints are open by default (no auth/permissions configured).
- AI calls are synchronous inside request path.
