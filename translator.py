"""
translator.py

Framework-independent translation service for LinguaLive.

Responsibilities:
- Detect the language of a piece of text.
- Translate text between any two languages in the config language
  registry.
- Present a single, stable interface (`translate_text`,
  `detect_language_key`, `translate_for_call`) so that swapping the
  underlying provider later (e.g. moving from Google Translate to a
  dedicated live-voice translation API) only requires changes inside
  this file.

Current provider: Google Translate, via the `deep-translator` package.
Language detection uses `langdetect`, a local heuristic detector, so
LinguaLive never needs a separate detection API key.

No Streamlit import. No st.session_state. Pure service layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from deep_translator import GoogleTranslator
from deep_translator.exceptions import (
    LanguageNotSupportedException,
    NotValidPayload,
    RequestError,
    TranslationNotFound,
)
from langdetect import DetectorFactory, LangDetectException, detect

from config import SUPPORTED_LANGUAGES, get_language

# langdetect's detector is non-deterministic by default (it samples n-grams
# probabilistically). Seeding it makes repeated detections of the same text
# stable, which matters for a live call where the same phrase may be
# re-processed.
DetectorFactory.seed = 0


class TranslationError(RuntimeError):
    """Raised when translation or language detection fails unrecoverably."""


@dataclass(frozen=True)
class TranslationResult:
    """
    The outcome of a single translation pass. Consumed by live_call.py
    (to drive the on-screen transcript) and by the Translation
    Assistant page (to render source/target text and history).
    """

    original_text: str
    translated_text: str
    source_language_key: str
    target_language_key: str


# Reverse lookup: Google Translate / langdetect ISO code -> our internal
# language key (e.g. "zh-cn" -> "chinese"). Built once at import time from
# the single source of truth in config.py so this module can never drift
# out of sync with the language registry.
_CODE_TO_KEY: Dict[str, str] = {
    lang.translate_code.lower(): key for key, lang in SUPPORTED_LANGUAGES.items()
}


def detect_language_key(text: str) -> Optional[str]:
    """
    Detect the language of `text` and return the matching internal
    language key (e.g. "tamil"), or None if detection fails or the
    detected language isn't one LinguaLive supports.

    Returns None instead of raising on failure because detection is
    routinely run on short, ambiguous utterances during a live call;
    the caller (live_call.py) is expected to fall back to the
    speaker's configured language when this returns None.
    """
    cleaned = text.strip()
    if not cleaned:
        return None

    try:
        detected_code = detect(cleaned).lower()
    except LangDetectException:
        return None

    if detected_code in _CODE_TO_KEY:
        return _CODE_TO_KEY[detected_code]

    # langdetect sometimes returns a region-qualified code (e.g. "zh-tw")
    # that isn't an exact match. Fall back to a base-code match.
    base_code = detected_code.split("-")[0]
    for code, key in _CODE_TO_KEY.items():
        if code.split("-")[0] == base_code:
            return key

    return None


def translate_text(
    text: str,
    target_language_key: str,
    source_language_key: Optional[str] = None,
) -> TranslationResult:
    """
    Translate `text` into the language identified by
    `target_language_key`.

    If `source_language_key` is omitted, the source language is
    auto-detected by the translation provider. Passing it explicitly
    (e.g. from the speaker's profile during a live call) is faster and
    more reliable than relying on auto-detection for short utterances.

    Raises TranslationError on any failure (unsupported language,
    network/provider error, or empty translation result) so callers
    can show a single, consistent error state instead of handling
    several exception types individually.
    """
    cleaned = text.strip()
    if not cleaned:
        raise TranslationError("Cannot translate empty text.")

    try:
        target_lang = get_language(target_language_key)
    except ValueError as exc:
        raise TranslationError(str(exc)) from exc

    if source_language_key is None:
        source_code = "auto"
        resolved_source_key = detect_language_key(cleaned) or "unknown"
    else:
        try:
            source_lang = get_language(source_language_key)
        except ValueError as exc:
            raise TranslationError(str(exc)) from exc
        source_code = source_lang.translate_code
        resolved_source_key = source_language_key

    try:
        translator = GoogleTranslator(source=source_code, target=target_lang.translate_code)
        translated_text = translator.translate(cleaned)
    except (
        LanguageNotSupportedException,
        NotValidPayload,
        RequestError,
        TranslationNotFound,
    ) as exc:
        raise TranslationError(f"Translation failed: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 - provider errors are not exhaustively typed
        raise TranslationError(f"Unexpected translation error: {exc}") from exc

    if not translated_text or not translated_text.strip():
        raise TranslationError("Translation provider returned an empty result.")

    return TranslationResult(
        original_text=cleaned,
        translated_text=translated_text.strip(),
        source_language_key=resolved_source_key,
        target_language_key=target_language_key,
    )


def translate_for_call(
    text: str,
    speaker_language_key: str,
    listener_language_key: str,
) -> TranslationResult:
    """
    Convenience wrapper used by live_call.py: translates one speaker's
    utterance into the other participant's language. The speaker's
    language is known from the call session (not auto-detected), which
    keeps the live-call pipeline fast and avoids misdetection on short
    phrases.

    If the speaker and listener use the same language, the text is
    returned unchanged rather than round-tripped through the provider.
    """
    if speaker_language_key == listener_language_key:
        return TranslationResult(
            original_text=text.strip(),
            translated_text=text.strip(),
            source_language_key=speaker_language_key,
            target_language_key=listener_language_key,
        )

    return translate_text(
        text=text,
        target_language_key=listener_language_key,
        source_language_key=speaker_language_key,
    )