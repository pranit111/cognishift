"""
python manage.py seed

Seeds the database with 4 demo users, their schedule blocks, and an active app session.
Safe to re-run — clears existing data first.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from notifications.models import User, AppSession, ScheduleBlock


USERS = [
    {
        'name': 'Alex Chen',
        'role': 'developer',
        'persona_description': (
            'Senior backend engineer who prefers deep focus sessions. '
            'Hates interruptions during coding. Uses VS Code and terminal all day. '
            'Checks Slack only twice a day. Very responsive to GitHub notifications.'
        ),
        'notification_pref': 'priority',
        'active_app': ('vscode', 'productivity'),
        'schedule': [
            {'title': 'Deep work — API refactor', 'block_type': 'focus', 'offset_h': 0, 'duration_h': 2},
            {'title': 'Team standup', 'block_type': 'meeting', 'offset_h': 2, 'duration_h': 1},
            {'title': 'Lunch break', 'block_type': 'break', 'offset_h': 4, 'duration_h': 1},
            {'title': 'Free time', 'block_type': 'free', 'offset_h': 5, 'duration_h': 3},
        ],
    },
    {
        'name': 'Sara Malik',
        'role': 'manager',
        'persona_description': (
            'Engineering manager with back-to-back meetings. '
            'Relies heavily on calendar and Slack. '
            'Needs urgent notifications even during meetings. '
            'Low tolerance for non-work notifications during work hours.'
        ),
        'notification_pref': 'urgent_only',
        'active_app': ('zoom', 'communication'),
        'schedule': [
            {'title': '1-on-1 with Alex', 'block_type': 'meeting', 'offset_h': 0, 'duration_h': 1},
            {'title': 'Sprint planning', 'block_type': 'meeting', 'offset_h': 1, 'duration_h': 2},
            {'title': 'Admin focus block', 'block_type': 'focus', 'offset_h': 3, 'duration_h': 1},
            {'title': 'Free', 'block_type': 'free', 'offset_h': 4, 'duration_h': 4},
        ],
    },
    {
        'name': 'Jordan Lee',
        'role': 'student',
        'persona_description': (
            'CS student who switches between studying, gaming, and YouTube. '
            'Often ignores notifications. '
            'Active late at night, tends to go offline around 2am. '
            'Mostly uses YouTube and Reddit when not studying.'
        ),
        'notification_pref': 'all',
        'active_app': ('youtube', 'leisure'),
        'schedule': [
            {'title': 'Lecture — Algorithms', 'block_type': 'meeting', 'offset_h': 0, 'duration_h': 2},
            {'title': 'Study session', 'block_type': 'focus', 'offset_h': 2, 'duration_h': 3},
            {'title': 'Free time', 'block_type': 'free', 'offset_h': 5, 'duration_h': 8},
        ],
    },
    {
        'name': 'Maya Patel',
        'role': 'designer',
        'persona_description': (
            'UI/UX designer who does long Figma sessions. '
            'Prefers not to be disturbed during design work. '
            'Responds well to Slack messages from the design team. '
            'Takes regular short breaks and checks notifications then.'
        ),
        'notification_pref': 'priority',
        'active_app': ('figma', 'productivity'),
        'schedule': [
            {'title': 'Design sprint — onboarding flow', 'block_type': 'focus', 'offset_h': 0, 'duration_h': 3},
            {'title': 'Design review meeting', 'block_type': 'meeting', 'offset_h': 3, 'duration_h': 1},
            {'title': 'Coffee break', 'block_type': 'break', 'offset_h': 4, 'duration_h': 1},
            {'title': 'Free', 'block_type': 'free', 'offset_h': 5, 'duration_h': 3},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed the database with demo users, schedule blocks, and app sessions.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing existing data...')
        ScheduleBlock.objects.all().delete()
        AppSession.objects.all().delete()
        User.objects.all().delete()

        now = timezone.now()

        for data in USERS:
            user = User.objects.create(
                name=data['name'],
                role=data['role'],
                persona_description=data['persona_description'],
                notification_pref=data['notification_pref'],
            )

            # Create schedule blocks anchored to now
            for block in data['schedule']:
                ScheduleBlock.objects.create(
                    user=user,
                    title=block['title'],
                    block_type=block['block_type'],
                    start_time=now + timedelta(hours=block['offset_h']),
                    end_time=now + timedelta(hours=block['offset_h'] + block['duration_h']),
                )

            # Create active app session
            app_name, app_category = data['active_app']
            AppSession.objects.create(
                user=user,
                app_name=app_name,
                app_category=app_category,
                is_active=True,
            )

            self.stdout.write(self.style.SUCCESS(f'  Created user: {user.name} ({user.role})'))

        self.stdout.write(self.style.SUCCESS(f'\nSeeded {len(USERS)} users successfully.'))
