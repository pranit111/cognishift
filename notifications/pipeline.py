"""
Core notification pipeline: context build → AI classify+infer → rule decision → log.
Imported by both views and the simulation engine.
"""
from datetime import timedelta

from django.utils import timezone

from .models import (
    User, AppSession, ScheduleBlock,
    NotificationEvent, UserInteractionLog, DecisionLog,
)
from .ai_service import classify_and_infer, apply_decision_rules, _get_time_of_day


def _build_context(user: User, source_app: str, message: str) -> dict:
    now = timezone.now()

    # Active app session
    session = user.app_sessions.filter(is_active=True).first()
    app_name = session.app_name if session else 'unknown'
    app_category = session.app_category if session else 'productivity'

    # Current schedule block
    block = user.schedule_blocks.filter(start_time__lte=now, end_time__gte=now).first()
    block_type = block.block_type if block else 'free'
    block_title = block.title if block else 'No scheduled block'

    # Recent interactions (last 5)
    recent_logs = UserInteractionLog.objects.filter(
        user=user
    ).order_by('-actioned_at')[:5]
    last_interactions = [log.action for log in recent_logs]

    # Ignored count in last 30 min
    thirty_min_ago = now - timedelta(minutes=30)
    recent_ignored_count = UserInteractionLog.objects.filter(
        user=user,
        action='ignored',
        actioned_at__gte=thirty_min_ago,
    ).count()

    time_of_day = _get_time_of_day(now.hour)

    return {
        'name': user.name,
        'role': user.role,
        'persona_description': user.persona_description,
        'app_name': app_name,
        'app_category': app_category,
        'block_type': block_type,
        'block_title': block_title,
        'time_of_day': time_of_day,
        'last_interactions': ', '.join(last_interactions) if last_interactions else 'none',
        'recent_ignored_count': recent_ignored_count,
        'source_app': source_app,
        'message': message,
        # Snapshots for DecisionLog
        '_session': session,
        '_block': block,
        '_recent_ignored_count': recent_ignored_count,
        '_last_interactions': last_interactions,
        '_time_of_day': time_of_day,
    }


def run_pipeline(user_id: str, source_app: str, message: str) -> dict:
    """
    Full pipeline for one notification event.
    Returns the decision payload.
    """
    user = User.objects.get(id=user_id)

    # 1. Build context
    ctx = _build_context(user, source_app, message)

    # 2. Create the notification event (unclassified)
    notif = NotificationEvent.objects.create(
        user=user,
        source_app=source_app,
        message=message,
    )

    # 3. Classify + infer mode
    # If user has manually set a mode, skip AI inference entirely
    if user.manual_mode != 'auto':
        inferred_mode = user.manual_mode
        ai_result = classify_and_infer(ctx)
        priority = ai_result.get('priority', 'medium')
        category = ai_result.get('category', 'work')
        ai_reason = f"[Manual mode: {inferred_mode}] {ai_result.get('ai_reason', '')}"
    else:
        ai_result = classify_and_infer(ctx)
        priority = ai_result.get('priority', 'medium')
        category = ai_result.get('category', 'work')
        inferred_mode = ai_result.get('inferred_mode', 'work')
        ai_reason = ai_result.get('ai_reason', '')

    # 4. Persist classification on the notification
    notif.ai_priority = priority
    notif.ai_category = category
    notif.save(update_fields=['ai_priority', 'ai_category'])

    # 5. Rule-based decision (no AI)
    decision_result = apply_decision_rules(inferred_mode, priority)
    decision = decision_result['decision']
    delay_minutes = decision_result['delay_minutes']
    delay_until = (timezone.now() + timedelta(minutes=delay_minutes)) if delay_minutes else None

    # 6. Update notification status
    status_map = {'send': 'sent', 'delay': 'queued', 'block': 'blocked'}
    notif.status = status_map[decision]
    notif.save(update_fields=['status'])

    # 7. Log the decision
    session = ctx['_session']
    block = ctx['_block']
    DecisionLog.objects.create(
        user=user,
        notification=notif,
        active_app_snapshot=session.app_name if session else '',
        active_app_category_snapshot=session.app_category if session else '',
        schedule_block_snapshot=block.block_type if block else '',
        recent_ignored_count=ctx['_recent_ignored_count'],
        last_interactions_snapshot=ctx['_last_interactions'],
        time_of_day_snapshot=ctx['_time_of_day'],
        inferred_mode=inferred_mode,
        decision=decision,
        ai_reason=ai_reason,
        delay_until=delay_until,
    )

    return {
        'notification_id': str(notif.id),
        'status': notif.status,
        'decision': decision,
        'inferred_mode': inferred_mode,
        'ai_priority': priority,
        'ai_category': category,
        'ai_reason': ai_reason,
        'delay_until': delay_until.isoformat() if delay_until else None,
    }


def drain_queue(user: User, new_mode: str) -> list:
    """
    Called when user's mode changes.
    Re-evaluates all queued notifications with the new mode.
    Any that now pass the rule table are flipped to 'delivered' and returned.
    """
    queued = NotificationEvent.objects.filter(user=user, status='queued')
    delivered = []
    for notif in queued:
        result = apply_decision_rules(new_mode, notif.ai_priority or 'medium')
        if result['decision'] == 'send':
            notif.status = 'delivered'
            notif.save(update_fields=['status'])
            delivered.append({
                'notification_id': str(notif.id),
                'source_app': notif.source_app,
                'message': notif.message,
                'ai_priority': notif.ai_priority,
                'ai_category': notif.ai_category,
            })
    return delivered
