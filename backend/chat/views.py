import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .services.chat import ChatService

logger = logging.getLogger(__name__)

# Module-level singleton — loaded once when Django starts, just like the
# original chat_api.py did at import time.
_chat_service: ChatService | None = None

try:
    _chat_service = ChatService()
    logger.info("ChatService initialized successfully.")
except Exception as exc:
    logger.critical("Failed to initialize ChatService: %s", exc)


def _service() -> ChatService:
    if _chat_service is None:
        raise RuntimeError("ChatService is not initialized.")
    return _chat_service


# ---------------------------------------------------------------------------
# POST /api/chat/message
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class ChatView(View):
    """
    Accept a user message and return the model's reply.

    Request body (JSON):
        { "message": "你好" }

    Response (JSON):
        { "reply": "..." }
    """

    def post(self, request):
        try:
            service = _service()
        except RuntimeError as exc:
            return JsonResponse({"error": str(exc)}, status=500)

        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON body."}, status=400)

        user_message: str = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Empty message."}, status=400)

        try:
            reply = service.chat(user_message)
            return JsonResponse({"reply": reply})
        except Exception as exc:
            logger.error("Error processing chat request: %s", exc)
            return JsonResponse({"error": f"An error occurred: {exc}"}, status=500)


# ---------------------------------------------------------------------------
# POST /api/chat/reset
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class ResetConversationView(View):
    """
    Clear the conversation history.

    Response (JSON):
        { "status": "success", "message": "Conversation history reset." }
    """

    def post(self, request):
        try:
            _service().reset_history()
            return JsonResponse({"status": "success", "message": "Conversation history reset."})
        except RuntimeError as exc:
            return JsonResponse({"error": str(exc)}, status=500)
        except Exception as exc:
            logger.error("Error resetting conversation: %s", exc)
            return JsonResponse({"error": f"An error occurred: {exc}"}, status=500)