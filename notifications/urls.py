from django.urls import path
from . import views

urlpatterns = [
    path('generate-event/', views.generate_event, name='generate-event'),
    path('classify/', views.classify, name='classify'),
    path('detect-mode/', views.detect_mode, name='detect-mode'),
    path('decision/', views.decision, name='decision'),
    path('users/', views.list_users, name='list-users'),
    path('users/<uuid:user_id>/', views.user_detail, name='user-detail'),
    path('users/<uuid:user_id>/set-mode/', views.set_mode, name='set-mode'),
    path('users/<uuid:user_id>/queue/', views.user_queue, name='user-queue'),
    path('users/<uuid:user_id>/notifications/', views.user_notifications, name='user-notifications'),
    path('decisions/', views.list_decisions, name='list-decisions'),
    path('simulate/run/', views.simulate_run, name='simulate-run'),
    path('interactions/', views.log_interaction, name='log-interaction'),
]
