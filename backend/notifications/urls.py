from django.urls import path
from . import views

urlpatterns = [
    path('generate-event/', views.generate_event, name='generate-event'),
    path('classify/', views.classify, name='classify'),
    path('detect-mode/', views.detect_mode, name='detect-mode'),
    path('decision/', views.decision, name='decision'),
    path('users/', views.list_users, name='list-users'),
    path('decisions/', views.list_decisions, name='list-decisions'),
    path('simulate/run/', views.simulate_run, name='simulate-run'),
    path('interactions/', views.log_interaction, name='log-interaction'),
]
