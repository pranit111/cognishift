"""
Google Calendar helper service.

Provides:
  - get_calendar_credentials(user)  — build/refresh a Credentials object
  - get_current_event(user)         — return the active event right now, or None
  - get_events_window(user, minutes) — return upcoming events within N minutes
"""
from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Map Google Calendar event "summary" keywords → block type
_MEETING_KEYWORDS = {'standup', 'meeting', 'call', 'sync', 'interview', 'review', '1:1', 'catchup'}


def _event_type_from_summary(summary: str) -> str:
    lower = summary.lower()
    for kw in _MEETING_KEYWORDS:
        if kw in lower:
            return 'meeting'
    return 'meeting'  # any calendar block defaults to meeting


def get_calendar_credentials(user) -> Credentials | None:
    """
    Build a google.oauth2.credentials.Credentials object from stored tokens.
    Refreshes automatically if the access token is expired.
    Returns None if the user hasn't connected Google Calendar.
    """
    if not user.google_refresh_token:
        return None

    creds = Credentials(
        token=user.google_access_token or None,
        refresh_token=user.google_refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )

    # Set expiry from the stored timestamp so the library can decide to refresh
    if user.google_token_expiry:
        import datetime
        creds.expiry = user.google_token_expiry.replace(tzinfo=None)  # google-auth expects naive UTC

    if creds.expired or not creds.valid:
        try:
            creds.refresh(Request())
            # Persist refreshed tokens back to the user model
            user.google_access_token = creds.token
            if creds.expiry:
                user.google_token_expiry = timezone.make_aware(
                    creds.expiry, timezone.utc
                ) if creds.expiry.tzinfo is None else creds.expiry
            user.save(update_fields=['google_access_token', 'google_token_expiry'])
        except Exception as exc:
            print(f'[calendar_service] Token refresh failed for user {user.id}: {exc}')
            return None

    return creds


def get_current_event(user) -> dict | None:
    """
    Fetch the Google Calendar event happening right now (±5 min to cover transitions).
    Returns: { "current_event": "Team Standup", "type": "meeting" }
    or None if no event or calendar not connected.
    """
    creds = get_calendar_credentials(user)
    if creds is None:
        return None

    try:
        service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
        now = timezone.now()
        time_min = (now - timedelta(minutes=5)).isoformat()
        time_max = (now + timedelta(minutes=5)).isoformat()

        result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
            maxResults=5,
        ).execute()

        events = result.get('items', [])
        if not events:
            return None

        # Return the first ongoing event
        event = events[0]
        summary = event.get('summary', 'Untitled event')
        return {
            'current_event': summary,
            'type': _event_type_from_summary(summary),
        }
    except Exception as exc:
        print(f'[calendar_service] get_current_event failed for user {user.id}: {exc}')
        return None


def get_events_window(user, minutes: int = 60) -> list[dict]:
    """
    Fetch upcoming events within the next `minutes` from now.
    Returns a list of { summary, start, end } dicts.
    """
    creds = get_calendar_credentials(user)
    if creds is None:
        return []

    try:
        service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
        now = timezone.now()
        time_min = now.isoformat()
        time_max = (now + timedelta(minutes=minutes)).isoformat()

        result = service.events().list(
            calendarId='primary',
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='startTime',
            maxResults=10,
        ).execute()

        out = []
        for ev in result.get('items', []):
            start = ev.get('start', {}).get('dateTime') or ev.get('start', {}).get('date', '')
            end   = ev.get('end',   {}).get('dateTime') or ev.get('end',   {}).get('date', '')
            out.append({'summary': ev.get('summary', 'Untitled'), 'start': start, 'end': end})
        return out
    except Exception as exc:
        print(f'[calendar_service] get_events_window failed for user {user.id}: {exc}')
        return []
