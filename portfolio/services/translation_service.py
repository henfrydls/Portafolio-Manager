"""
Translation service abstraction with LibreTranslate support.
"""
import logging
import time
from dataclasses import dataclass
from typing import Optional

import requests
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """Raised when the translation provider fails."""


@dataclass
class TranslationResult:
    translated_text: str
    provider: str
    duration_ms: int
    cached: bool = False
    auto_generated: bool = True


class BaseTranslationClient:
    """Interface for translation clients."""

    def translate(self, text: str, source: str, target: str, **kwargs) -> str:
        raise NotImplementedError


class LibreTranslateClient(BaseTranslationClient):
    """Simple HTTP client for LibreTranslate."""

    def __init__(self, api_url: str, api_key: Optional[str] = None, timeout: int = 30):
        if not api_url:
            raise ImproperlyConfigured("LibreTranslate API URL is required")
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def translate(self, text: str, source: str, target: str, **kwargs) -> str:
        if not text:
            return ""

        payload = {
            "q": text,
            "source": source,
            "target": target,
            "format": kwargs.get("format", "text"),
        }
        if self.api_key:
            payload["api_key"] = self.api_key

        try:
            response = requests.post(
                f"{self.api_url}/translate",
                data=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            logger.error("LibreTranslate request failed: %s", exc)
            raise TranslationError(str(exc)) from exc
        if not response.ok:
            logger.error("LibreTranslate error: %s", response.text)
            raise TranslationError(f"LibreTranslate responded with {response.status_code}")

        data = response.json()
        translated_text = data.get("translatedText")
        if translated_text is None:
            raise TranslationError("LibreTranslate response missing translatedText")

        return translated_text


class TranslationService:
    """Facade to translate content according to site configuration."""

    def __init__(self, provider: str, api_url: str, api_key: str = "", timeout: int = 30):
        self.provider = provider
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self._cache = {}
        self.client = self._build_client()

    def _build_client(self) -> BaseTranslationClient:
        if self.provider == "libretranslate":
            return LibreTranslateClient(self.api_url, self.api_key, timeout=self.timeout)
        raise ImproperlyConfigured(f"Unsupported translation provider: {self.provider}")
    @staticmethod
    def _cache_key(text: str, source: str, target: str, provider: str) -> str:
        return "|".join((provider, source, target, text))

    def translate(self, text: str, source: str, target: str, **kwargs) -> TranslationResult:
        cache_key = self._cache_key(text, source, target, self.provider)
        cached_text = self._cache.get(cache_key)
        if cached_text is not None:
            return TranslationResult(
                translated_text=cached_text,
                provider=self.provider,
                duration_ms=0,
                cached=True,
            )

        start = time.monotonic()
        translated_text = self.client.translate(text, source, target, **kwargs)
        duration_ms = int((time.monotonic() - start) * 1000)

        # store in simple cache attached to the method
        self._cache[cache_key] = translated_text

        logger.debug(
            "Translated %s chars %s->%s in %sms via %s",
            len(text),
            source,
            target,
            duration_ms,
            self.provider,
        )

        return TranslationResult(
            translated_text=translated_text,
            provider=self.provider,
            duration_ms=duration_ms,
        )
