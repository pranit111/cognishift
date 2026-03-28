"""
Simulation engine — advances one time step for all users.
Each step: rotate the active app, maybe trigger a notification, log a random interaction.
"""
import random
from datetime import timedelta

from django.utils import timezone

from .models import User, AppSession, NotificationEvent, UserInteractionLog
from .pipeline import run_pipeline

# App pool per category
APP_POOL = {
    'productivity': ['vscode', 'notion', 'figma', 'excel', 'terminal'],
    'communication': ['slack', 'zoom', 'gmail', 'teams', 'discord'],
    'leisure': ['youtube', 'spotify', 'reddit', 'twitter', 'netflix'],
}

# Weighted probability of switching app category per role
ROLE_CATEGORY_WEIGHTS = {
    'developer': {'productivity': 0.6, 'communication': 0.3, 'leisure': 0.1},
    'manager':   {'productivity': 0.3, 'communication': 0.6, 'leisure': 0.1},
    'student':   {'productivity': 0.4, 'communication': 0.2, 'leisure': 0.4},
    'designer':  {'productivity': 0.5, 'communication': 0.3, 'leisure': 0.2},
}

# Notification pool per source
NOTIFICATION_POOL = {
    'slack': [
        "Hey, can you review my PR when you get a chance?",
        "Standup in 5 minutes!",
        "Deployment failed on staging — need help ASAP.",
        "Weekend plans? Anyone up for lunch Friday?",
        "New channel #design-feedback just created.",
    ],
    'gmail': [
        "Invoice #4521 is due tomorrow.",
        "Your subscription renewal is coming up.",
        "Meeting notes from today's sync are attached.",
        "Password reset requested for your account.",
        "You have a new job offer from TechCorp.",
    ],
    'github': [
        "Your pull request #142 was approved.",
        "Critical security vulnerability found in dependency.",
        "Build #99 failed — 3 tests broken.",
        "Issue #88 assigned to you.",
        "New comment on your PR: 'Looks good, but can you add tests?'",
    ],
    'calendar': [
        "Reminder: Sprint standup in 10 minutes.",
        "Your focus block starts now.",
        "1-on-1 with manager in 30 minutes.",
        "All-hands meeting rescheduled to 3pm.",
        "Your lunch break is in 15 minutes.",
    ],
    'youtube': [
        "Your favourite creator just uploaded a new video.",
        "Live stream starting now: 'Build a SaaS in 24hrs'",
        "Recommended for you: 10 productivity hacks.",
    ],
}

# Simulated interaction weights — biased by mode (set externally or randomly)
INTERACTION_WEIGHTS = ['seen', 'seen', 'ignored', 'dismissed', 'snoozed']


def _pick_category(role: str) -> str:
    weights = ROLE_CATEGORY_WEIGHTS.get(role, {'productivity': 0.4, 'communication': 0.3, 'leisure': 0.3})
    return random.choices(list(weights.keys()), weights=list(weights.values()))[0]


def _rotate_app(user: User):
    """Deactivate current session, start a new one."""
    AppSession.objects.filter(user=user, is_active=True).update(
        is_active=False, ended_at=timezone.now()
    )
    category = _pick_category(user.role)
    app_name = random.choice(APP_POOL[category])
    AppSession.objects.create(user=user, app_name=app_name, app_category=category)


def _maybe_fire_notification(user: User) -> dict | None:
    """30% chance of generating a notification for this user on this tick."""
    if random.random() > 0.30:
        return None

    source = random.choice(list(NOTIFICATION_POOL.keys()))
    message = random.choice(NOTIFICATION_POOL[source])
    return run_pipeline(user_id=str(user.id), source_app=source, message=message)


def _simulate_interaction(user: User):
    """
    Randomly log an interaction for a recent uninteracted notification.
    Models realistic user behaviour: sometimes they ignore, sometimes they act.
    """
    recent = NotificationEvent.objects.filter(
        user=user
    ).exclude(
        interactions__isnull=False
    ).order_by('-triggered_at')[:5]

    if not recent:
        return

    notif = random.choice(list(recent))
    action = random.choice(INTERACTION_WEIGHTS)
    UserInteractionLog.objects.create(user=user, notification=notif, action=action)


def run_simulation_step() -> list[dict]:
    """
    Advance simulation one time step for all users.
    Returns a summary of what happened.
    """
    results = []
    users = User.objects.all()

    for user in users:
        step_result = {'user': user.name, 'app_rotated': False, 'notification': None}

        # 50% chance to rotate app
        if random.random() < 0.5:
            _rotate_app(user)
            step_result['app_rotated'] = True

        # Maybe fire a notification through the full pipeline
        notif_result = _maybe_fire_notification(user)
        if notif_result:
            step_result['notification'] = notif_result

        # Simulate interaction with a past notification
        _simulate_interaction(user)

        results.append(step_result)

    return results
