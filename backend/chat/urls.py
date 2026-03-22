from django.urls import path
from .views import ChatView, ResetConversationView

urlpatterns = [
    path("message", ChatView.as_view(), name="chat-message"),
    path("reset", ResetConversationView.as_view(), name="chat-reset"),
]