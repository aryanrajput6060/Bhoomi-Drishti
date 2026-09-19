"""Text-to-speech for JARVIS.

Two providers, tried in order:

1. **edge** — Microsoft neural voices through ``edge-tts`` (natural sounding,
   needs a network connection). Rendered audio is cached on disk.
2. **sapi** — the offline Windows SAPI 5 engine via ``scripts/speak.ps1``.
   Always available, slightly robotic.

A failing provider degrades to the next one and the failure is reported honestly
to the UI instead of silently doing nothing.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import time
from dataclasses import dataclass
from pathlib import Path

from config import TTS_CACHE_DIR, settings
from services import media, ps
from services.events import bus

log = logging.getLogger("jarvis.tts")

try:  # optional dependency
    import edge_tts

    EDGE_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    edge_tts = None  # type: ignore[assignment]
    EDGE_AVAILABLE = False

#: How long to avoid retrying edge-tts after a network failure.
EDGE_COOLDOWN_SECONDS = 300.0

_MARKDOWN_NOISE = re.compile(r"(\*\*|__|\*+|`{1,3}|~~|^#{1,6}\s*)", re.MULTILINE)
_CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
_URL = re.compile(r"https?://\S+")
_EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\uFE0F]")
_WHITESPACE = re.compile(r"\s+")


def clean_for_speech(text: str, *, limit: int = 1500) -> str:
    """Turn an assistant reply into something pleasant to hear aloud."""
    value = _CODE_BLOCK.sub(" (code block omitted) ", text or "")
    value = _URL.sub(" the link on screen ", value)
    value = _MARKDOWN_NOISE.sub("", value)
    value = _EMOJI.sub("", value)
    value = value.replace("|", " ").replace("•", " ")
    value = _WHITESPACE.sub(" ", value).strip()
    if len(value) > limit:
        value = value[: limit - 1].rsplit(" ", 1)[0] + "…"
    return value


@dataclass(slots=True)
class SpeechResult:
    """Outcome of a synthesis request."""

    text: str
    provider: str
    voice: str
    path: str
    duration: float = 0.0
    cached: bool = False
    played: bool = False
    error: str = ""

    def as_dict(self) -> dict:
        return {
            "text": self.text,
            "provider": self.provider,
            "voice": self.voice,
            "path": self.path,
            "filename": Path(self.path).name if self.path else "",
            "duration": round(self.duration, 2),
            "cached": self.cached,
            "played": self.played,
            "error": self.error,
        }

class TTSEngine:
    """Synthesises and plays speech while tracking provider health."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._edge_failed_at: float = 0.0
        self._edge_error: str = ""
        self._speaking: bool = False
        self._last: SpeechResult | None = None

    @property
    def speaking(self) -> bool:
        return self._speaking

    @property
    def edge_healthy(self) -> bool:
        return EDGE_AVAILABLE and (time.time() - self._edge_failed_at) > EDGE_COOLDOWN_SECONDS

    def provider_order(self) -> list[str]:
        """Providers to try, honouring the configured preference."""
        chosen = (settings.tts_provider or "auto").lower()
        if chosen == "off":
            return []
        if chosen == "edge":
            return ["edge", "sapi"]
        if chosen == "sapi":
            return ["sapi"]
        order: list[str] = ["edge", "sapi"] if EDGE_AVAILABLE else ["sapi"]
        if "edge" in order and not self.edge_healthy:
            order = [name for name in order if name != "edge"] or ["sapi"]
        return order

    @property
    def last_result(self) -> dict | None:
        return self._last.as_dict() if self._last else None

    async def status(self) -> dict:
        voices: list[dict] = []
        sapi_error = ""
        try:
            voices = ps.as_list(await ps.run_json("voices.ps1", {}, timeout=30, default=[]))
        except Exception as exc:
            sapi_error = str(exc)
        return {
            "enabled": settings.tts_enabled,
            "configured_provider": settings.tts_provider,
            "active_order": self.provider_order(),
            "edge_installed": EDGE_AVAILABLE,
            "edge_healthy": self.edge_healthy,
            "edge_error": self._edge_error,
            "edge_voice": settings.tts_voice,
            "sapi_voices": [voice.get("name") for voice in voices],
            "sapi_error": sapi_error,
            "speaking": self._speaking,
            "last": self._last.as_dict() if self._last else None,
            "cache_files": len(list(TTS_CACHE_DIR.glob("*.*"))),
        }

    async def list_voices(self, *, include_edge: bool = True) -> dict:
        """Available voices, grouped by provider."""
        sapi: list[dict] = []
        try:
            sapi = ps.as_list(await ps.run_json("voices.ps1", {}, timeout=30, default=[]))
        except Exception as exc:
            log.warning("could not list SAPI voices: %s", exc)

        edge: list[dict] = []
        if include_edge and EDGE_AVAILABLE:
            try:
                raw = await edge_tts.list_voices()
                edge = [
                    {
                        "name": item["ShortName"],
                        "gender": item.get("Gender", ""),
                        "locale": item.get("Locale", ""),
                    }
                    for item in raw
                    if str(item.get("Locale", "")).startswith(("en-", "hi-"))
                ]
            except Exception as exc:
                log.warning("could not list edge-tts voices: %s", exc)
        return {"provider": settings.tts_provider, "edge": edge, "sapi": sapi}

# -- synthesis -------------------------------------------------------- #
    def _cache_path(self, text: str, provider: str, voice: str) -> Path:
        digest = hashlib.sha1(f"{provider}|{voice}|{settings.tts_rate}|{text}".encode("utf-8")).hexdigest()[:20]
        suffix = ".mp3" if provider == "edge" else ".wav"
        return TTS_CACHE_DIR / f"{provider}_{digest}{suffix}"

    async def _synthesize_edge(self, text: str, voice: str) -> Path:
        target = self._cache_path(text, "edge", voice)
        if target.exists() and target.stat().st_size > 0:
            return target
        rate = f"{(settings.tts_rate or 0) * 5:+d}%"
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(str(target))
        if not target.exists() or target.stat().st_size == 0:
            raise RuntimeError("edge-tts produced no audio")
        return target

    def _synthesize_sapi(self, text: str, voice: str) -> Path:
        target = self._cache_path(text, "sapi", voice)
        if target.exists() and target.stat().st_size > 0:
            return target
        ps.run_script_sync(
            "speak.ps1",
            {"Text": text, "Voice": voice or "", "Rate": settings.tts_rate, "OutputFile": str(target)},
            timeout=max(30.0, len(text) / 6.0),
        )
        if not target.exists():
            raise RuntimeError("SAPI produced no audio file")
        return target

    async def synthesize(self, text: str, voice: str | None = None) -> SpeechResult:
        """Render speech to an audio file (cached) and return its location."""
        spoken = clean_for_speech(text)
        if not spoken:
            return SpeechResult(text="", provider="none", voice="", path="", error="Nothing to say.")

        chosen_voice = voice or settings.tts_voice
        sapi_voice = settings.tts_sapi_voice
        errors: list[str] = []

        for provider in self.provider_order():
            target_voice = chosen_voice if provider == "edge" else sapi_voice
            was_cached = self._cache_path(spoken, provider, target_voice).exists()
            try:
                if provider == "edge":
                    path = await self._synthesize_edge(spoken, chosen_voice)
                else:
                    path = await asyncio.to_thread(self._synthesize_sapi, spoken, sapi_voice)
                result = SpeechResult(
                    text=spoken,
                    provider=provider,
                    voice=target_voice or "(system default)",
                    path=str(path),
                    duration=media.wav_duration(path) if path.suffix == ".wav" else 0.0,
                    cached=was_cached,
                )
                self._last = result
                return result
            except Exception as exc:
                errors.append(f"{provider}: {exc}")
                log.warning("TTS provider failed — %s: %s", provider, exc)
                if provider == "edge":
                    self._edge_failed_at = time.time()
                    self._edge_error = str(exc)

        return SpeechResult(
            text=spoken,
            provider="none",
            voice="",
            path="",
            error="; ".join(errors) or "No text-to-speech provider is available.",
        )

# -- playback --------------------------------------------------------- #
    async def speak(
        self,
        text: str,
        voice: str | None = None,
        *,
        wait: bool = True,
        emit: bool = True,
    ) -> SpeechResult:
        """Synthesise and play ``text`` through the machine's speakers."""
        if not settings.tts_enabled:
            return SpeechResult(text=text, provider="none", voice="", path="", error="Speech is muted.")

        async with self._lock:
            result = await self.synthesize(text, voice)
            if not result.path:
                if emit:
                    await bus.emit("error", text=result.error, source="tts")
                return result

            self._speaking = True
            if emit:
                await bus.emit("state", state="speaking", provider=result.provider, voice=result.voice)
            try:
                if wait:
                    await asyncio.to_thread(media.play_file_sync, result.path)
            except Exception as exc:
                log.warning("playback failed: %s", exc)
                result.error = f"playback failed: {exc}"
            finally:
                if wait:
                    self._speaking = False
                    if emit:
                        await bus.emit("state", state="idle")
            return result

    async def speak_in_background(self, text: str, voice: str | None = None) -> SpeechResult:
        """Speak without tying up the caller (used for notifications/reminders)."""

        async def runner() -> None:
            await self.speak(text, voice, wait=True, emit=True)

        asyncio.create_task(runner())
        return SpeechResult(text=text, provider="pending", voice=voice or settings.tts_voice, path="")

    async def stop(self) -> None:
        """Stop any speech that is currently playing."""
        await asyncio.to_thread(media.stop_playback)
        self._speaking = False
        await bus.emit("state", state="idle")


#: Shared engine instance.
tts = TTSEngine()


__all__ = [
    "EDGE_AVAILABLE",
    "SpeechResult",
    "TTSEngine",
    "clean_for_speech",
    "tts",
]