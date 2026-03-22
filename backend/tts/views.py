import json
import logging
import os

from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .services.tts import TtsService

logger = logging.getLogger(__name__)

# Module-level singleton — initialized once on first request to avoid slowing
# down Django startup / migrations when TTS is not needed.
_tts_service: TtsService | None = None


def _service() -> TtsService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TtsService()
    return _tts_service


# ---------------------------------------------------------------------------
# POST /api/tts/synthesize
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class TtsView(View):
    """
    Generate speech from text via CosyVoice2 zero-shot inference.

    Request body (JSON):
        { "text": "我是哪吒" }

    Response (JSON):
        { "audio_files": ["tts_1234_0.wav", ...] }
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON body."}, status=400)

        text: str = data.get("text", "").strip()
        if not text:
            return JsonResponse({"error": "Missing or empty 'text' field."}, status=400)

        logger.info("TTS request: %s", text)

        try:
            audio_files = _service().synthesize(text)
            return JsonResponse({"audio_files": audio_files})
        except (FileNotFoundError, RuntimeError, ValueError) as exc:
            logger.error("TTS synthesis failed: %s", exc)
            return JsonResponse({"error": str(exc)}, status=500)
        except Exception as exc:
            logger.exception("Unexpected TTS error")
            return JsonResponse({"error": f"An error occurred: {exc}"}, status=500)


# ---------------------------------------------------------------------------
# GET /api/tts/audio/<filename>
# ---------------------------------------------------------------------------

class AudioFileView(View):
    """
    Serve a generated .wav file by name.

    Response: audio/wav binary stream
    """

    def get(self, request, filename: str):
        audio_dir = settings.COSYVOICE_AUDIO_DIR
        file_path = audio_dir / filename

        if not file_path.exists():
            logger.error("Audio file not found: %s", file_path)
            return JsonResponse({"error": "File not found."}, status=404)

        logger.info("Serving audio file: %s", file_path)
        return FileResponse(open(file_path, "rb"), content_type="audio/wav")


# ---------------------------------------------------------------------------
# GET /api/tts/status
# ---------------------------------------------------------------------------

class TtsStatusView(View):
    """
    Health check for the TTS service.

    Response (JSON):
        { "status": "running", "reference_audio": "loaded"|"missing", "audio_dir": "..." }
    """

    def get(self, request):
        ref_path = settings.COSYVOICE_REFERENCE_AUDIO
        audio_dir = settings.COSYVOICE_AUDIO_DIR

        ref_status = "loaded" if ref_path.exists() else "missing"

        return JsonResponse({
            "status": "running",
            "reference_audio": ref_status,
            "audio_dir": str(audio_dir),
        })