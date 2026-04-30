from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.ChatView.as_view(), name="ai-chat"),
    path("chat/history/", views.ConversationHistoryView.as_view(), name="ai-chat-history"),
    path("insights/", views.InsightsView.as_view(), name="ai-insights"),
    path("questions/", views.QuestionsView.as_view(), name="ai-questions"),
    path("workout/plan/", views.WorkoutPlanView.as_view(), name="ai-workout-plan"),
]
