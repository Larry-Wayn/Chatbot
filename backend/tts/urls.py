from django.urls import path
from .views import TtsView, AudioFileView, TtsStatusView

urlpatterns = [
    path("synthesize", TtsView.as_view(),           name="tts-synthesize"),
    path("audio/<str:filename>", AudioFileView.as_view(), name="tts-audio"),
    path("status",   TtsStatusView.as_view(),       name="tts-status"),
]