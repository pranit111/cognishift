from django.contrib import admin

from .models import (
	User,
	AppSession,
	ScheduleBlock,
	NotificationEvent,
	UserInteractionLog,
	DecisionLog,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('name', 'role', 'notification_pref', 'telegram_chat_id')
	search_fields = ('name', 'role', 'persona_description', 'telegram_chat_id')
	list_filter = ('role', 'notification_pref')


@admin.register(AppSession)
class AppSessionAdmin(admin.ModelAdmin):
	list_display = ('user', 'app_name', 'app_category', 'is_active', 'started_at', 'ended_at')
	search_fields = ('user__name', 'app_name')
	list_filter = ('app_category', 'is_active')


@admin.register(ScheduleBlock)
class ScheduleBlockAdmin(admin.ModelAdmin):
	list_display = ('user', 'title', 'block_type', 'start_time', 'end_time')
	search_fields = ('user__name', 'title')
	list_filter = ('block_type',)


@admin.register(NotificationEvent)
class NotificationEventAdmin(admin.ModelAdmin):
	list_display = ('user', 'source_app', 'ai_priority', 'ai_category', 'triggered_at')
	search_fields = ('user__name', 'source_app', 'message')
	list_filter = ('source_app', 'ai_priority', 'ai_category')


@admin.register(UserInteractionLog)
class UserInteractionLogAdmin(admin.ModelAdmin):
	list_display = ('user', 'notification', 'action', 'actioned_at')
	search_fields = ('user__name', 'notification__message')
	list_filter = ('action',)


@admin.register(DecisionLog)
class DecisionLogAdmin(admin.ModelAdmin):
	list_display = ('user', 'notification', 'inferred_mode', 'decision', 'delay_until', 'created_at')
	search_fields = ('user__name', 'notification__message', 'ai_reason')
	list_filter = ('inferred_mode', 'decision', 'time_of_day_snapshot')
