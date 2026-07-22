"""
speech.py

Framework-independent speech I/O service for LinguaLive:
speech-to-text (transcription) and text-to-speech (synthesis).

Responsibilities:
- Convert recorded audio (arbitrary browser/mic formats) into text,
  using the language pair information from config.py.
- Convert translated text into playable speech audio.
- Normalize audio formats via pydub so the rest of the app never has
  to think about codecs.

This module does not know how audio was captured (microphone widget,
uploaded file, etc.) — it only accepts raw audio bytes plus a format
hint. The UI layer is responsible for capturing audio and handing it
here; live_call.py's session logic is responsible for sequencing
"record -> transcribe -> translate -> synthesize -> play".

No Streamlit import. No st.session_state.
"""

from __future__ import annotations

import io
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import speech_recognition as sr
from gtts import gTTS
from gtts.tts import gTTSError
from pydub import AudioSegment

from config import SOUNDS_DIR, get_language

logger = logging.getLogger(__name__)

# Synthesized audio is cached to disk (rather than kept purely in memory)
# so the "call again with the same phrase" and "replay" cases in the UI
# don't need to re-hit the TTS provider. Nested under the assets sounds
# directory, which config.py already guarantees exists.
GENERATED_AUDIO_DIR: Path = SOUNDS_DIR / "generated"
GENERATED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


class SpeechError(RuntimeError):
    """Raised when transcription or synthesis fails unrecoverably."""


@dataclass(frozen=True)
class TranscriptionResult:
    """The text recognized from a chunk of recorded speech."""

    text: str
    language_key: str


def _to_wav_audio_segment(audio_bytes: bytes, source_format: str) -> AudioSegment:
    """
    Decode arbitrary audio bytes (webm, ogg, m4a, mp3, wav, ...) into a
    pydub AudioSegment, normalized to mono / 16kHz — the format the
    Google Web Speech API (via SpeechRecognition) expects for reliable
    recognition.
    """
    try:
        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=source_format)
    except Exception as exc:  # noqa: BLE001 - pydub/ffmpeg errors are not exhaustively typed
        raise SpeechError(f"Could not decode audio (format='{source_format}'): {exc}") from exc

    return segment.set_channels(1).set_frame_rate(16_000)


def transcribe_audio_bytes(
    audio_bytes: bytes,
    source_format: str,
    language_key: str,
) -> TranscriptionResult:
    """
    Transcribe raw audio bytes into text.

    `source_format` is the container/codec the bytes were captured in
    (e.g. "webm", "wav", "ogg") — whatever the UI's audio recorder
    widget produced. `language_key` must match a key in
    config.SUPPORTED_LANGUAGES and determines which speech-recognition
    locale is used (e.g. "ta-IN" for Tamil).

    Raises SpeechError if the audio can't be decoded, contains no
    recognizable speech, or the recognition service is unreachable.
    """
    if not audio_bytes:
        raise SpeechError("No audio data provided.")

    try:
        language = get_language(language_key)
    except ValueError as exc:
        raise SpeechError(str(exc)) from exc

    segment = _to_wav_audio_segment(audio_bytes, source_format)

    wav_buffer = io.BytesIO()
    segment.export(wav_buffer, format="wav")
    wav_buffer.seek(0)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_buffer) as source:
            audio_data = recognizer.record(source)
    except Exception as exc:  # noqa: BLE001
        raise SpeechError(f"Could not read decoded audio: {exc}") from exc

    try:
        text = recognizer.recognize_google(
            audio_data, language=language.speech_recognition_code
        )
    except sr.UnknownValueError as exc:
        raise SpeechError("Could not understand the audio; no speech was recognized.") from exc
    except sr.RequestError as exc:
        raise SpeechError(f"Speech recognition service error: {exc}") from exc

    cleaned_text = text.strip()
    if not cleaned_text:
        raise SpeechError("Recognition produced empty text.")

    return TranscriptionResult(text=cleaned_text, language_key=language_key)


def transcribe_audio_file(path: Path, language_key: str) -> TranscriptionResult:
    """Convenience wrapper: transcribe audio already saved to disk."""
    if not path.exists():
        raise SpeechError(f"Audio file not found: {path}")

    source_format = path.suffix.lstrip(".").lower() or "wav"
    return transcribe_audio_bytes(path.read_bytes(), source_format, language_key)


def synthesize_speech_bytes(text: str, language_key: str) -> bytes:
    """
    Convert `text` into speech audio (MP3-encoded bytes) using the
    voice for `language_key`. Used when the caller wants to hand audio
    straight to a UI player without touching the filesystem.

    Raises SpeechError if the text is empty, the language is
    unsupported, or the TTS provider fails.
    """
    cleaned = text.strip()
    if not cleaned:
        raise SpeechError("Cannot synthesize empty text.")

    try:
        language = get_language(language_key)
    except ValueError as exc:
        raise SpeechError(str(exc)) from exc

    buffer = io.BytesIO()
    try:
        gTTS(text=cleaned, lang=language.tts_code).write_to_fp(buffer)
    except gTTSError as exc:
        raise SpeechError(f"Speech synthesis failed: {exc}") from exc
    except Exception as exc:  # noqa: BLE001
        raise SpeechError(f"Unexpected synthesis error: {exc}") from exc

    audio_bytes = buffer.getvalue()
    if not audio_bytes:
        raise SpeechError("Speech synthesis produced no audio data.")

    return audio_bytes


def synthesize_speech_to_file(
    text: str,
    language_key: str,
    output_path: Optional[Path] = None,
) -> Path:
    """
    Synthesize `text` to speech and save it as an MP3 file, returning
    the path. If `output_path` is omitted, a uniquely named file is
    created under GENERATED_AUDIO_DIR so repeated calls never collide.
    """
    audio_bytes = synthesize_speech_bytes(text, language_key)

    target_path = output_path or (GENERATED_AUDIO_DIR / f"{uuid.uuid4().hex}.mp3")
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        target_path.write_bytes(audio_bytes)
    except OSError as exc:
        raise SpeechError(f"Could not write synthesized audio to {target_path}: {exc}") from exc

    return target_path


def clear_generated_audio() -> int:
    """
    Delete every cached synthesized audio file. Returns the number of
    files removed. Intended for a "clear cache" settings action.
    """
    removed = 0
    for file_path in GENERATED_AUDIO_DIR.glob("*.mp3"):
        try:
            file_path.unlink()
            removed += 1
        except OSError as exc:
            logger.warning("Failed to remove cached audio file %s: %s", file_path, exc)

    return removed