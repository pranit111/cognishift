from rest_framework import serializers
from .models import User, AppSession, ScheduleBlock, NotificationEvent, UserInteractionLog, DecisionLog


class AppSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSession
        fields = ['id', 'app_name', 'app_category', 'started_at', 'is_active']


class ScheduleBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleBlock
        fields = ['id', 'title', 'block_type', 'start_time', 'end_time']


class UserSerializer(serializers.ModelSerializer):
    active_app = serializers.SerializerMethodField()
    current_block = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'role', 'persona_description', 'notification_pref', 'active_app', 'current_block']

    def get_active_app(self, obj):
        session = obj.app_sessions.filter(is_active=True).first()
        return AppSessionSerializer(session).data if session else None

    def get_current_block(self, obj):
        from django.utils import timezone
        now = timezone.now()
        block = obj.schedule_blocks.filter(start_time__lte=now, end_time__gte=now).first()
        return ScheduleBlockSerializer(block).data if block else None


class NotificationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationEvent
        fields = ['id', 'user', 'source_app', 'message', 'triggered_at', 'ai_priority', 'ai_category']


class DecisionLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    notification_source = serializers.CharField(source='notification.source_app', read_only=True)
    notification_message = serializers.CharField(source='notification.message', read_only=True)

    class Meta:
        model = DecisionLog
        fields = [
            'id', 'user_name', 'user_role',
            'notification_source', 'notification_message',
            'active_app_snapshot', 'active_app_category_snapshot',
            'schedule_block_snapshot', 'recent_ignored_count',
            'last_interactions_snapshot', 'time_of_day_snapshot',
            'inferred_mode', 'decision', 'ai_reason',
            'delay_until', 'created_at',
        ]


class UserInteractionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteractionLog
        fields = ['id', 'user', 'notification', 'action', 'actioned_at']
