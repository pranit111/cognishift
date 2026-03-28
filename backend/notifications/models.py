import uuid
from django.db import models


class User(models.Model):
    ROLE_CHOICES = [
        ('developer', 'Developer'),
        ('manager', 'Manager'),
        ('student', 'Student'),
        ('designer', 'Designer'),
    ]
    NOTIF_PREF_CHOICES = [
        ('all', 'All'),
        ('priority', 'Priority'),
        ('urgent_only', 'Urgent Only'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    persona_description = models.TextField()
    notification_pref = models.CharField(max_length=20, choices=NOTIF_PREF_CHOICES, default='all')
    telegram_chat_id = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.role})"


class AppSession(models.Model):
    CATEGORY_CHOICES = [
        ('productivity', 'Productivity'),
        ('communication', 'Communication'),
        ('leisure', 'Leisure'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_sessions')
    app_name = models.CharField(max_length=100)
    app_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.name} - {self.app_name} ({'active' if self.is_active else 'ended'})"


class ScheduleBlock(models.Model):
    BLOCK_TYPE_CHOICES = [
        ('meeting', 'Meeting'),
        ('focus', 'Focus'),
        ('break', 'Break'),
        ('free', 'Free'),
]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_blocks')
    title = models.CharField(max_length=200)
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.name} - {self.title} ({self.block_type})"


class NotificationEvent(models.Model):
    SOURCE_CHOICES = [
        ('slack', 'Slack'),
        ('gmail', 'Gmail'),
        ('github', 'GitHub'),
        ('calendar', 'Calendar'),
        ('youtube', 'YouTube'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    CATEGORY_CHOICES = [
        ('social', 'Social'),
        ('work', 'Work'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    source_app = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    ai_priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, blank=True, default='')
    ai_category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, blank=True, default='')

    def __str__(self):
        return f"[{self.source_app}] {self.message[:50]}"


class UserInteractionLog(models.Model):
    ACTION_CHOICES = [
        ('seen', 'Seen'),
        ('ignored', 'Ignored'),
        ('dismissed', 'Dismissed'),
        ('snoozed', 'Snoozed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interaction_logs')
    notification = models.ForeignKey(NotificationEvent, on_delete=models.CASCADE, related_name='interactions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actioned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} {self.action} notification"


class DecisionLog(models.Model):
    MODE_CHOICES = [
        ('focus', 'Focus'),
        ('work', 'Work'),
        ('meeting', 'Meeting'),
        ('relax', 'Relax'),
        ('sleep', 'Sleep'),
    ]
    DECISION_CHOICES = [
        ('send', 'Send'),
        ('delay', 'Delay'),
        ('block', 'Block'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decision_logs')
    notification = models.ForeignKey(NotificationEvent, on_delete=models.CASCADE, related_name='decisions')
    active_app_snapshot = models.CharField(max_length=100, blank=True)
    active_app_category_snapshot = models.CharField(max_length=20, blank=True)
    schedule_block_snapshot = models.CharField(max_length=20, blank=True)
    recent_ignored_count = models.IntegerField(default=0)
    last_interactions_snapshot = models.JSONField(default=list)
    time_of_day_snapshot = models.CharField(max_length=20, blank=True)
    inferred_mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    decision = models.CharField(max_length=10, choices=DECISION_CHOICES)
    ai_reason = models.TextField(blank=True)
    delay_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.name} → {self.decision} ({self.inferred_mode})"
