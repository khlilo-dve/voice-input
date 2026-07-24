"""Speech-to-text engine using faster-whisper."""
import logging
from pathlib import Path
from faster_whisper import WhisperModel
from config import WHISPER_MODEL, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE, WHISPER_LANGUAGE

logger = logging.getLogger(__name__)

# Lazy-loaded singleton
_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        logger.info(f"Loading faster-whisper model: {WHISPER_MODEL}")
        _model = WhisperModel(
            WHISPER_MODEL,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
    return _model


def transcribe(audio_path: str) -> str:
    """Transcribe audio file to Chinese text.

    Args:
        audio_path: Path to 16kHz mono WAV file.

    Returns:
        Transcribed Chinese text string.

    Raises:
        ValueError: If no speech detected or result is empty.
        FileNotFoundError: If audio file doesn't exist.
    """
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    logger.info(f"Transcribing: {path.name}")
    model = _get_model()
    segments, info = model.transcribe(
        str(path),
        language=WHISPER_LANGUAGE,
        beam_size=3,
        vad_filter=True,  # filter silence
    )

    segments_list = list(segments)
    if not segments_list:
        raise ValueError("No speech detected in audio")

    text = " ".join(seg.text.strip() for seg in segments_list)

    if not text:
        raise ValueError("Transcription produced empty text")

    logger.info(f"Transcribed ({info.language}, p={info.language_probability:.2f}): {text[:80]}...")
    return text
