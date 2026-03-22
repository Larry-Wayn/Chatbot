import logging
import os
import sys
import time
import traceback

import torch
import torchaudio
from django.conf import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CosyVoice2 lazy singleton
# ---------------------------------------------------------------------------
# CosyVoice2 and load_wav are imported at first use so that Django can start
# without the model being present (useful for running migrations, tests, etc.)
# ---------------------------------------------------------------------------

_cosyvoice = None


def _get_cosyvoice():
    global _cosyvoice
    if _cosyvoice is not None:
        return _cosyvoice

    cosyvoice_root = settings.COSYVOICE_ROOT          # e.g. BASE_DIR / "COSYVoice"
    model_path     = settings.COSYVOICE_MODEL_PATH    # e.g. cosyvoice_root / "pretrained_models/CosyVoice2-0.5B"

    sys.path.insert(0, str(cosyvoice_root / "third_party" / "Matcha-TTS"))
    sys.path.insert(0, str(cosyvoice_root))

    from COSYVoice.cosyvoice.cli.cosyvoice import CosyVoice2

    if not model_path.exists():
        raise FileNotFoundError(f"CosyVoice2 model not found: {model_path}")

    logger.info("Initializing CosyVoice2 from %s", model_path)
    _cosyvoice = CosyVoice2(
        str(model_path),
        load_jit=False,
        load_trt=False,
        fp16=False,
    )
    logger.info("CosyVoice2 initialized.")
    return _cosyvoice


def _load_prompt_wav():
    """Load the reference audio once and cache it."""
    cosyvoice_root = settings.COSYVOICE_ROOT
    sys.path.insert(0, str(cosyvoice_root / "third_party" / "Matcha-TTS"))
    sys.path.insert(0, str(cosyvoice_root))
    from COSYVoice.cosyvoice.utils.file_utils import load_wav

    ref_path = settings.COSYVOICE_REFERENCE_AUDIO   # Path to NZ_angry.mp3
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference audio not found: {ref_path}")
    return load_wav(str(ref_path), 16000)


# Module-level reference audio cache
_prompt_wav = None


def _get_prompt_wav():
    global _prompt_wav
    if _prompt_wav is None:
        _prompt_wav = _load_prompt_wav()
    return _prompt_wav


# ---------------------------------------------------------------------------
# Public service
# ---------------------------------------------------------------------------

class TtsService:
    """
    Wraps CosyVoice2 zero-shot inference.

    Settings expected in Django settings.py:
        COSYVOICE_ROOT            = BASE_DIR / "COSYVoice"
        COSYVOICE_MODEL_PATH      = COSYVOICE_ROOT / "pretrained_models/CosyVoice2-0.5B"
        COSYVOICE_REFERENCE_AUDIO = BASE_DIR / "resource/voice/NZ_angry.mp3"
        COSYVOICE_REFERENCE_TEXT  = "拜个屁的师我什么都不学！..."
        COSYVOICE_AUDIO_DIR       = BASE_DIR / "generated_audio"
    """

    def synthesize(self, text: str) -> list[str]:
        """
        Run zero-shot TTS inference on *text*.

        Returns a list of generated .wav filenames (relative to COSYVOICE_AUDIO_DIR).
        """
        if not text or not text.strip():
            raise ValueError("Empty text.")

        audio_dir: "Path" = settings.COSYVOICE_AUDIO_DIR
        audio_dir.mkdir(parents=True, exist_ok=True)

        reference_text: str = settings.COSYVOICE_REFERENCE_TEXT

        cosyvoice = _get_cosyvoice()
        prompt_wav = _get_prompt_wav()

        try:
            inference_result = list(
                cosyvoice.inference_zero_shot(
                    text,
                    reference_text,
                    prompt_wav,
                    stream=False,
                )
            )
        finally:
            torch.cuda.empty_cache()

        if not inference_result:
            raise RuntimeError("TTS engine returned no audio segments.")

        audio_files: list[str] = []
        ts = int(time.time())

        for i, segment in enumerate(inference_result):
            if "tts_speech" not in segment:
                logger.warning("Segment %d missing 'tts_speech', skipping.", i)
                continue

            speech = segment["tts_speech"].cpu()
            filename = f"tts_{ts}_{i}.wav"
            filepath = audio_dir / filename

            try:
                torchaudio.save(str(filepath), speech, cosyvoice.sample_rate)
                audio_files.append(filename)
                logger.info("Saved audio: %s", filepath)
            except Exception:
                logger.error("Failed to save %s:\n%s", filepath, traceback.format_exc())

        if not audio_files:
            raise RuntimeError("No audio files were saved.")

        return audio_files