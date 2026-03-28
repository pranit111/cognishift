from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .ai_service import classify_and_infer, apply_decision_rules, _get_time_of_day
from .models import User, AppSession, ScheduleBlock, NotificationEvent, DecisionLog, UserInteractionLog
from .pipeline import run_pipeline, _build_context
from .serializers import UserSerializer, DecisionLogSerializer
from .simulation import run_simulation_step

USER_NOT_FOUND = 'User not found.'


@api_view(['POST'])
def generate_event(request):
    """
    POST /api/generate-event/
    Body: { user_id, source_app, message }
    Runs the full pipeline and returns the decision.
    """
    user_id = request.data.get('user_id')
    source_app = request.data.get('source_app')
    message = request.data.get('message')

    if not all([user_id, source_app, message]):
        return Response({'error': 'user_id, source_app, and message are required.'}, status=400)

    try:
        result = run_pipeline(user_id=user_id, source_app=source_app, message=message)
        return Response(result, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({'error': USER_NOT_FOUND}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def classify(request):
    """
    POST /api/classify/
    Body: { message, context_snapshot }
    Lightweight endpoint: calls LLM and returns classification only.
    """
    message = request.data.get('message')
    context_snapshot = request.data.get('context_snapshot', {})

    if not message:
        return Response({'error': 'message is required.'}, status=400)

    context_snapshot['message'] = message
    # Fill in defaults for any missing context fields
    context_snapshot.setdefault('name', 'Unknown')
    context_snapshot.setdefault('role', 'developer')
    context_snapshot.setdefault('persona_description', 'No persona provided.')
    context_snapshot.setdefault('app_name', 'unknown')
    context_snapshot.setdefault('app_category', 'productivity')
    context_snapshot.setdefault('block_type', 'free')
    context_snapshot.setdefault('block_title', 'No block')
    context_snapshot.setdefault('time_of_day', _get_time_of_day(timezone.now().hour))
    context_snapshot.setdefault('last_interactions', 'none')
    context_snapshot.setdefault('recent_ignored_count', 0)
    context_snapshot.setdefault('source_app', 'unknown')

    try:
        result = classify_and_infer(context_snapshot)
        return Response({
            'priority': result.get('priority'),
            'category': result.get('category'),
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def detect_mode(request):
    """
    POST /api/detect-mode/
    Body: { user_id }
    Reads current context and returns inferred mode via AI.
    """
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'error': 'user_id is required.'}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': USER_NOT_FOUND}, status=404)

    ctx = _build_context(user, source_app='system', message='mode detection probe')
    try:
        result = classify_and_infer(ctx)
        return Response({'inferred_mode': result.get('inferred_mode'), 'ai_reason': result.get('ai_reason')})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def decision(request):
    """
    POST /api/decision/
    Body: { user_id, priority, inferred_mode }
    Pure rule-based decision — no AI.
    """
    priority = request.data.get('priority')
    inferred_mode = request.data.get('inferred_mode')

    if not all([priority, inferred_mode]):
        return Response({'error': 'priority and inferred_mode are required.'}, status=400)

    result = apply_decision_rules(inferred_mode, priority)
    return Response({'decision': result['decision'], 'delay_minutes': result['delay_minutes']})


@api_view(['GET'])
def list_users(request):
    """
    GET /api/users/
    Returns all users with their current active app and schedule block.
    """
    users = User.objects.prefetch_related('app_sessions', 'schedule_blocks').all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def list_decisions(request):
    """
    GET /api/decisions/
    Returns last 50 DecisionLog entries across all users.
    """
    logs = DecisionLog.objects.select_related('user', 'notification').all()[:50]
    serializer = DecisionLogSerializer(logs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def simulate_run(request):
    """
    GET /api/simulate/run/
    Advances one simulation tick for all users.
    """
    try:
        results = run_simulation_step()
        return Response({'tick': 'completed', 'results': results})
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
def log_interaction(request):
    """
    POST /api/interactions/
    Body: { user_id, notification_id, action }
    Logs a user interaction with a notification.
    """
    user_id = request.data.get('user_id')
    notification_id = request.data.get('notification_id')
    action = request.data.get('action')

    if not all([user_id, notification_id, action]):
        return Response({'error': 'user_id, notification_id, and action are required.'}, status=400)

    valid_actions = ['seen', 'ignored', 'dismissed', 'snoozed']
    if action not in valid_actions:
        return Response({'error': f'action must be one of {valid_actions}'}, status=400)

    try:
        user = User.objects.get(id=user_id)
        notif = NotificationEvent.objects.get(id=notification_id, user=user)
        log = UserInteractionLog.objects.create(user=user, notification=notif, action=action)
        return Response({'id': str(log.id), 'action': action}, status=201)
    except User.DoesNotExist:
        return Response({'error': USER_NOT_FOUND}, status=404)
    except NotificationEvent.DoesNotExist:
        return Response({'error': 'Notification not found.'}, status=404)
