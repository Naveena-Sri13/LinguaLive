"""
config.py

Central configuration module for LinguaLive.

This module owns every piece of static configuration the application
depends on: filesystem paths, supported languages, audio defaults,
feature flags, and shared data contracts (dataclasses/enums) that are
reused across the UI layer, the service layer, and any future backend
(FastAPI) or frontend (Flutter/React) replacement.

Rules enforced in this file:
- No Streamlit import. No UI concerns. Pure Python + stdlib only.
- Every other module reads settings through the `settings` singleton
  instead of re-reading environment variables directly, so behaviour
  stays consistent across the whole codebase.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Final


# --------------------------------------------------------------------------- #
# Filesystem layout
# --------------------------------------------------------------------------- #

BASE_DIR: Final[Path] = Path(__file__).resolve().parent
ASSETS_DIR: Final[Path] = BASE_DIR / "assets"
DATA_DIR: Final[Path] = BASE_DIR / "data"

IMAGES_DIR: Final[Path] = ASSETS_DIR / "images"
ICONS_DIR: Final[Path] = ASSETS_DIR / "icons"
SOUNDS_DIR: Final[Path] = ASSETS_DIR / "sounds"
ANIMATIONS_DIR: Final[Path] = ASSETS_DIR / "animations"

CONTACTS_FILE: Final[Path] = DATA_DIR / "contacts.json"
RECENT_CALLS_FILE: Final[Path] = DATA_DIR / "recent_calls.json"
FEEDBACK_FILE: Final[Path] = DATA_DIR / "feedback.json"

for _directory in (
    ASSETS_DIR,
    IMAGES_DIR,
    ICONS_DIR,
    SOUNDS_DIR,
    ANIMATIONS_DIR,
    DATA_DIR,
):
    _directory.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------- #
# Shared enums
# --------------------------------------------------------------------------- #

class Theme(str, Enum):
    """Application colour theme. Persisted in user preferences."""

    LIGHT = "light"
    DARK = "dark"


class CallStatus(str, Enum):
    """Lifecycle states of a live call session."""

    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ENDED = "ended"


class TranslationStage(str, Enum):
    """
    Fine-grained state of the real-time translation pipeline, used to
    drive the "Listening... / Understanding... / Translating..." status
    indicators on the active call screen.
    """

    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    TRANSLATING = "translating"
    SYNTHESIZING = "synthesizing"
    DELIVERED = "delivered"
    ERROR = "error"


# --------------------------------------------------------------------------- #
# Language registry
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Language:
    """
    A single supported language and every locale code the pipeline
    needs for it. Kept in one place so speech recognition, translation,
    and text-to-speech never disagree about what a language is called.
    """

    display_name: str
    translate_code: str        # Google Translate language code
    speech_recognition_code: str  # BCP-47 code for SpeechRecognition
    tts_code: str               # gTTS language code


SUPPORTED_LANGUAGES: Final[Dict[str, Language]] = {
    "english": Language("English", "en", "en-US", "en"),
    "tamil": Language("Tamil", "ta", "ta-IN", "ta"),
    "hindi": Language("Hindi", "hi", "hi-IN", "hi"),
    "french": Language("French", "fr", "fr-FR", "fr"),
    "spanish": Language("Spanish", "es", "es-ES", "es"),
    "german": Language("German", "de", "de-DE", "de"),
    "japanese": Language("Japanese", "ja", "ja-JP", "ja"),
    "korean": Language("Korean", "ko", "ko-KR", "ko"),
    "chinese": Language("Chinese (Simplified)", "zh-cn", "zh-CN", "zh-CN"),
    "arabic": Language("Arabic", "ar", "ar-SA", "ar"),
    "russian": Language("Russian", "ru", "ru-RU", "ru"),
    "portuguese": Language("Portuguese", "pt", "pt-PT", "pt"),
    "italian": Language("Italian", "it", "it-IT", "it"),
    "telugu": Language("Telugu", "te", "te-IN", "te"),
    "malayalam": Language("Malayalam", "ml", "ml-IN", "ml"),
    "kannada": Language("Kannada", "kn", "kn-IN", "kn"),
    "bengali": Language("Bengali", "bn", "bn-IN", "bn"),
}

DEFAULT_LANGUAGE_KEY: Final[str] = "english"


def get_language(key: str) -> Language:
    """
    Resolve a language key to its Language record.

    Raises a ValueError instead of a bare KeyError so callers in the
    service layer can surface a clean, user-facing error message
    without needing to know this registry's internal structure.
    """
    normalized = key.strip().lower()
    if normalized not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language key: '{key}'")
    return SUPPORTED_LANGUAGES[normalized]


def language_choices() -> Dict[str, str]:
    """Return {key: display_name} pairs, suitable for populating a UI dropdown."""
    return {key: lang.display_name for key, lang in SUPPORTED_LANGUAGES.items()}


# --------------------------------------------------------------------------- #
# Audio settings
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class AudioSettings:
    """Defaults for recording, silence detection, and playback."""

    sample_rate_hz: int = 16_000
    channels: int = 1
    max_recording_seconds: int = 30
    silence_threshold_seconds: float = 1.2
    playback_format: str = "mp3"
    recording_format: str = "wav"


# --------------------------------------------------------------------------- #
# Feature flags
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class FeatureFlags:
    """
    Toggle points for behaviour that will change as LinguaLive matures
    (e.g. swapping Google Translate for a dedicated live-voice API).
    Reading these through `settings.features` keeps call sites stable
    even when the underlying provider changes.
    """

    live_translation_enabled: bool = True
    auto_detect_contact_language: bool = True
    save_call_history: bool = True
    save_feedback: bool = True


# --------------------------------------------------------------------------- #
# Top-level application settings
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class AppSettings:
    """
    Single settings object the rest of the application depends on.
    Values are sourced from environment variables where it makes sense
    (so deployment config can override them) and fall back to sane
    production defaults otherwise.
    """

    app_name: str = "LinguaLive"
    tagline: str = "Real-Time AI Multilingual Communication Platform"
    version: str = "1.0.0"

    default_theme: Theme = Theme.LIGHT
    default_language_key: str = DEFAULT_LANGUAGE_KEY

    audio: AudioSettings = field(default_factory=AudioSettings)
    features: FeatureFlags = field(default_factory=FeatureFlags)

    paths: Dict[str, Path] = field(
        default_factory=lambda: {
            "base": BASE_DIR,
            "assets": ASSETS_DIR,
            "images": IMAGES_DIR,
            "icons": ICONS_DIR,
            "sounds": SOUNDS_DIR,
            "animations": ANIMATIONS_DIR,
            "data": DATA_DIR,
            "contacts": CONTACTS_FILE,
            "recent_calls": RECENT_CALLS_FILE,
            "feedback": FEEDBACK_FILE,
        }
    )

    @staticmethod
    def _env_bool(name: str, default: bool) -> bool:
        raw = os.environ.get(name)
        if raw is None:
            return default
        return raw.strip().lower() in {"1", "true", "yes", "on"}

    @classmethod
    def from_env(cls) -> "AppSettings":
        """
        Build settings from environment variables, falling back to
        defaults. Kept as a classmethod (rather than doing this at
        import time unconditionally) so tests can construct isolated
        instances without touching the process environment.
        """
        theme = Theme.DARK if os.environ.get("LINGUALIVE_THEME", "light").lower() == "dark" else Theme.LIGHT
        default_language = os.environ.get("LINGUALIVE_DEFAULT_LANGUAGE", DEFAULT_LANGUAGE_KEY)

        features = FeatureFlags(
            live_translation_enabled=cls._env_bool("LINGUALIVE_LIVE_TRANSLATION", True),
            auto_detect_contact_language=cls._env_bool("LINGUALIVE_AUTO_DETECT_LANGUAGE", True),
            save_call_history=cls._env_bool("LINGUALIVE_SAVE_HISTORY", True),
            save_feedback=cls._env_bool("LINGUALIVE_SAVE_FEEDBACK", True),
        )

        return cls(
            default_theme=theme,
            default_language_key=default_language,
            features=features,
        )


# Process-wide settings singleton. Every module should import `settings`
# from here rather than constructing its own AppSettings instance.
settings: Final[AppSettings] = AppSettings.from_env()
