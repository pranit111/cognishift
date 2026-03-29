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
    path('users/<uuid:user_id>/summarise/', views.summarise_notifications, name='user-summarise'),
    path('users/<uuid:user_id>/telegram-link/', views.telegram_link, name='telegram-link'),
    path('users/<uuid:user_id>/calendar/current/', views.user_calendar_current, name='user-calendar-current'),
    path('decisions/', views.list_decisions, name='list-decisions'),
    path('simulate/run/', views.simulate_run, name='simulate-run'),
    path('interactions/', views.log_interaction, name='log-interaction'),
    path('auth/send-otp/',         views.send_otp,         name='send-otp'),
    path('auth/verify-otp/',       views.verify_otp,       name='verify-otp'),
    path('auth/login/send-otp/',   views.send_login_otp,   name='login-send-otp'),
    path('auth/login/verify-otp/', views.login_verify_otp, name='login-verify-otp'),
    path('users/<uuid:user_id>/app-session/', views.set_app_session,     name='set-app-session'),
    path('auth/google/<uuid:user_id>/init/', views.google_auth_init,     name='google-auth-init'),
    path('auth/google/callback/',            views.google_auth_callback, name='google-auth-callback'),
]
