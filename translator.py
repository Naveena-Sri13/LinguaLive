"""
translator.py

Framework-independent translation service for LinguaLive.

Architecture:
    TranslationProvider (ABC)
        - Defines the contract any translation backend must satisfy.
    GoogleTranslateProvider
        - Current implementation using Google Translate.
    TranslationService
        - Public API used everywhere else in LinguaLive.

No Streamlit.
No session state.
Pure business logic.
"""

from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional

from deep_translator import GoogleTranslator
from deep_translator.exceptions import (
    LanguageNotSupportedException,
    NotValidPayload,
    RequestError,
    TranslationNotFound,
)

from langdetect import (
    DetectorFactory,
    LangDetectException,
    detect,
)

from config import (
    SUPPORTED_LANGUAGES,
    get_language,
)

logger = logging.getLogger(__name__)

DetectorFactory.seed = 0

AUTO_DETECT_SOURCE = "auto"


class TranslatorError(RuntimeError):
    """Raised when translation fails."""


# Backward compatibility
TranslationError = TranslatorError


@dataclass(frozen=True)
class TranslationResult:
    """
    Result returned after a successful translation.
    """

    original_text: str

    translated_text: str

    source_language_key: str

    target_language_key: str

    detected_language_name: str


class TranslationProvider(ABC):
    """
    Base class for all translation providers.
    """

    @abstractmethod
    def detect(
        self,
        text: str,
    ) -> Optional[str]:
        pass

    @abstractmethod
    def translate(
        self,
        text: str,
        source_code: str,
        target_code: str,
    ) -> str:
        pass


class GoogleTranslateProvider(
    TranslationProvider
):
    """
    Google Translate implementation.
    """

    @lru_cache(maxsize=256)
    def detect(
        self,
        text: str,
    ) -> Optional[str]:

        cleaned = text.strip()

        if len(cleaned) < 2:
            return None

        try:
            return detect(cleaned).lower()

        except LangDetectException as exc:

            logger.debug(
                "Language detection failed: %s",
                exc,
            )

            return None

    def translate(
        self,
        text: str,
        source_code: str,
        target_code: str,
    ) -> str:

        try:

            translated = GoogleTranslator(
                source=source_code,
                target=target_code,
            ).translate(
                text
            )

        except (
            LanguageNotSupportedException,
            NotValidPayload,
            RequestError,
            TranslationNotFound,
        ) as exc:

            raise TranslatorError(
                f"Translation failed: {exc}"
            ) from exc

        except Exception as exc:

            raise TranslatorError(
                f"Unexpected translation error: {exc}"
            ) from exc

        if translated is None:

            raise TranslatorError(
                "Translation provider returned None."
            )

        translated = translated.strip()

        if not translated:

            raise TranslatorError(
                "Translation provider returned an empty result."
            )

        return translated


class TranslationService:
    """
    Main translation service.

    Every UI component, Live Call,
    Translation Assistant,
    FastAPI endpoint,
    or future Flutter application
    should use THIS class.
    """

    def __init__(
        self,
        provider: Optional[
            TranslationProvider
        ] = None,
    ):

        self._provider = (
            provider
            or GoogleTranslateProvider()
        )

        self._code_to_key: Dict[
            str,
            str,
        ] = {

            language.translate_code.lower(): key

            for key, language in SUPPORTED_LANGUAGES.items()

        }

    def _resolve_detected_code(
        self,
        code: str,
    ) -> Optional[str]:

        normalized = code.lower()

        if normalized in self._code_to_key:

            return self._code_to_key[
                normalized
            ]

        base = normalized.split("-")[0]

        for provider_code, key in self._code_to_key.items():

            if provider_code.split("-")[0] == base:

                return key

        return None

    def detect_language_key(
        self,
        text: str,
    ) -> Optional[str]:

        cleaned = text.strip()

        if not cleaned:

            return None

        detected = self._provider.detect(
            cleaned
        )

        if detected is None:

            return None

        return self._resolve_detected_code(
            detected
        )
    def translate(
        self,
        text: str,
        target_language_key: str,
        source_language_key: Optional[str] = None,
    ) -> TranslationResult:
        """
        Translate text into the requested target language.

        If source_language_key is omitted,
        language is detected automatically.
        """

        cleaned = text.strip()

        if not cleaned:
            raise TranslatorError(
                "Cannot translate empty text."
            )

        try:
            target_language = get_language(
                target_language_key
            )

        except ValueError as exc:

            raise TranslatorError(
                str(exc)
            ) from exc

        # ---------------------------------------
        # Determine source language
        # ---------------------------------------

        if source_language_key is None:

            detected_key = self.detect_language_key(
                cleaned
            )

            if detected_key is None:

                raise TranslatorError(
                    "Unable to detect source language."
                )

            source_language_key = detected_key

            source_code = AUTO_DETECT_SOURCE

        else:

            try:

                source_language = get_language(
                    source_language_key
                )

            except ValueError as exc:

                raise TranslatorError(
                    str(exc)
                ) from exc

            source_code = (
                source_language.translate_code
            )

        # ---------------------------------------
        # Prevent unnecessary translation
        # ---------------------------------------

        if source_language_key == target_language_key:

            return TranslationResult(

                original_text=cleaned,

                translated_text=cleaned,

                source_language_key=source_language_key,

                target_language_key=target_language_key,

                detected_language_name=get_language(
                    source_language_key
                ).display_name,
            )

        translated = self._provider.translate(

            cleaned,

            source_code,

            target_language.translate_code,

        )

        return TranslationResult(

            original_text=cleaned,

            translated_text=translated,

            source_language_key=source_language_key,

            target_language_key=target_language_key,

            detected_language_name=get_language(
                source_language_key
            ).display_name,
        )

    def translate_batch(
        self,
        texts: List[str],
        target_language_key: str,
        source_language_key: Optional[str] = None,
    ) -> List[TranslationResult]:

        if not texts:

            raise TranslatorError(
                "Cannot batch translate an empty list."
            )

        results: List[
            TranslationResult
        ] = []

        for index, text in enumerate(texts):

            try:

                results.append(

                    self.translate(

                        text=text,

                        target_language_key=target_language_key,

                        source_language_key=source_language_key,

                    )

                )

            except TranslatorError as exc:

                raise TranslatorError(

                    f"Batch translation failed at index {index}: {exc}"

                ) from exc

        return results

    def translate_for_call(
        self,
        text: str,
        speaker_language_key: str,
        listener_language_key: str,
    ) -> TranslationResult:
        """
        Translation used during a live call.

        The speaker language is already known,
        therefore no detection is performed.
        """

        cleaned = text.strip()

        if not cleaned:

            raise TranslatorError(
                "Cannot translate empty text."
            )

        if speaker_language_key == listener_language_key:

            return TranslationResult(

                original_text=cleaned,

                translated_text=cleaned,

                source_language_key=speaker_language_key,

                target_language_key=listener_language_key,

                detected_language_name=get_language(
                    speaker_language_key
                ).display_name,
            )

        return self.translate(

            text=cleaned,

            target_language_key=listener_language_key,

            source_language_key=speaker_language_key,

        )

    def translate_assistant(
        self,
        text: str,
        target_language_key: str,
    ) -> TranslationResult:
        """
        Translation Assistant workflow.

        1. Detect language.
        2. Show detected language.
        3. Translate only if needed.
        """

        cleaned = text.strip()

        if not cleaned:

            raise TranslatorError(
                "Cannot translate empty text."
            )

        detected = self.detect_language_key(
            cleaned
        )

        if detected is None:

            raise TranslatorError(
                "Unable to detect source language."
            )

        if detected == target_language_key:

            return TranslationResult(

                original_text=cleaned,

                translated_text=cleaned,

                source_language_key=detected,

                target_language_key=target_language_key,

                detected_language_name=get_language(
                    detected
                ).display_name,
            )

        return self.translate(

            text=cleaned,

            target_language_key=target_language_key,

            source_language_key=detected,

        )
# ---------------------------------------------------------------------
# Default Translation Service
# ---------------------------------------------------------------------

_default_service = TranslationService()


# ---------------------------------------------------------------------
# Module-level Convenience Functions
#
# These preserve the original API so existing modules
# (live_call.py, app.py, etc.) continue to work without
# constructing TranslationService manually.
# ---------------------------------------------------------------------


def detect_language_key(
    text: str,
) -> Optional[str]:
    """
    Detect the language of a piece of text.

    Returns the LinguaLive language key,
    or None if detection fails.
    """
    return _default_service.detect_language_key(
        text
    )


def translate_text(
    text: str,
    target_language_key: str,
    source_language_key: Optional[str] = None,
) -> TranslationResult:
    """
    Generic translation wrapper.
    """
    return _default_service.translate(
        text=text,
        target_language_key=target_language_key,
        source_language_key=source_language_key,
    )


def translate_batch(
    texts: List[str],
    target_language_key: str,
    source_language_key: Optional[str] = None,
) -> List[TranslationResult]:
    """
    Batch translation wrapper.
    """
    return _default_service.translate_batch(
        texts=texts,
        target_language_key=target_language_key,
        source_language_key=source_language_key,
    )


def translate_for_call(
    text: str,
    speaker_language_key: str,
    listener_language_key: str,
) -> TranslationResult:
    """
    Live Call translation wrapper.
    """
    return _default_service.translate_for_call(
        text=text,
        speaker_language_key=speaker_language_key,
        listener_language_key=listener_language_key,
    )


def translate_assistant(
    text: str,
    target_language_key: str,
) -> TranslationResult:
    """
    Translation Assistant wrapper.
    """
    return _default_service.translate_assistant(
        text=text,
        target_language_key=target_language_key,
    )   
    