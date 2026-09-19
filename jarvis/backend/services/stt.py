"""Speech recognition: local Whisper (faster-whisper) plus real mic capture.

JARVIS supports two independent recognition paths:

* **server** — capture the microphone with ``sounddevice``, trim silence with a
  simple energy VAD, and transcribe locally with ``faster-whisper`` (fully
  offline after the first model download).
* **browser** — the frontend can post recorded audio to
  ``/api/voice/transcribe``; it lands in the same :class:`SpeechRecognizer`.

Model loading is lazy so JARVIS starts instantly and only pays the cost when
speech recognition is actually used.
"""

from __future__ import annotations

import asyncio
import logging
import math
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from config import RECORDINGS_DIR, settings
from services import media
from services.events import bus

log = logging.getLogger("jarvis.stt")

try:  # optional dependency
    import numpy as np
    import sounddevice as sd

    AUDIO_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    np = None  # type: ignore[assignment]
    sd = None  # type: ignore[assignment]
    AUDIO_AVAILABLE = False

try:  # optional dependency
    from faster_whisper import WhisperModel

    WHISPER_AVAILABLE = True
except Exception:  # pragma: no cover - optional
    WhisperModel = None  # type: ignore[assignment]
    WHISPER_AVAILABLE = False


@dataclass(slots=True)
class Transcript:
    """Result of a transcription request."""

    text: str
    source: str = "unknown"          # microphone | upload | browser
    language: str = ""
    duration: float = 0.0
    confidence: float = 0.0
    segments: list[dict[str, Any]] = field(default_factory=list)
    speech_detected: bool = True
    audio_path: str = ""
    error: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "source": self.source,
            "language": self.language,
            "duration": round(self.duration, 2),
            "confidence": round(self.confidence, 3),
            "segments": self.segments,
            "speech_detected": self.speech_detected,
            "audio_path": self.audio_path,
            "error": self.error,
        }


@dataclass(slots=True)
class Recording:
    """A finished microphone capture."""

    path: str
    duration: float
    speech_detected: bool
    peak_level: float
    noise_floor: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "duration": round(self.duration, 2),
            "speech_detected": self.speech_detected,
            "peak_level": round(self.peak_level, 4),
            "noise_floor": round(self.noise_floor, 4),
        }

class Microphone:
    """Microphone discovery plus silence-trimmed recording via sounddevice."""

    def available(self) -> bool:
        return AUDIO_AVAILABLE

    def devices(self) -> list[dict[str, Any]]:
        """Every capture device with a friendly name and default marker."""
        if not AUDIO_AVAILABLE:
            return []
        result: list[dict[str, Any]] = []
        try:
            try:
                default_input: Any = sd.default.device[0]  # type: ignore[index]
            except Exception:
                default_input = None
            for index, device in enumerate(sd.query_devices()):
                if int(device.get("max_input_channels", 0)) < 1:
                    continue
                result.append(
                    {
                        "index": index,
                        "name": device.get("name", ""),
                        "channels": int(device.get("max_input_channels", 0)),
                        "sample_rate": int(device.get("default_samplerate", 0) or 0),
                        "is_default": index == default_input,
                    }
                )
        except Exception as exc:
            log.warning("could not enumerate audio devices: %s", exc)
        return result

    def default_device(self) -> dict[str, Any] | None:
        devices = self.devices()
        for device in devices:
            if device["is_default"]:
                return device
        return devices[0] if devices else None

    def record(
        self,
        *,
        max_seconds: float | None = None,
        silence_ms: int | None = None,
        threshold: float | None = None,
        sample_rate: int | None = None,
        device: int | None = None,
        path: Path | None = None,
    ) -> Recording:
        """Record until the speaker pauses, then return the captured WAV.

        An energy-based VAD keeps a 1.5 s pre-roll (so the first syllable is never
        clipped) and stops after ``silence_ms`` of quiet. Levels are returned so
        callers can tell "silence" apart from "speech that failed to transcribe".
        """
        if not AUDIO_AVAILABLE:
            raise RuntimeError(
                "Microphone capture needs 'sounddevice' and 'numpy' (pip install sounddevice numpy)."
            )

        max_seconds = float(max_seconds or settings.max_record_seconds)
        silence_target = (silence_ms or settings.vad_silence_ms) / 1000.0
        threshold = float(threshold or settings.vad_threshold)
        sample_rate = int(sample_rate or settings.mic_sample_rate)
        block_seconds = 0.03
        block_size = max(1, int(sample_rate * block_seconds))
        pre_roll_blocks = int(1.5 / block_seconds)

        frames: list[bytes] = []
        pre_roll: list[bytes] = []
        peak = 0.0
        noise_samples: list[float] = []
        speech_started = False
        silence_elapsed = 0.0
        started_at = time.monotonic()

        stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            blocksize=block_size,
            device=device,
        )
        with stream:
            while True:
                if time.monotonic() - started_at > max_seconds:
                    break
                chunk, overflowed = stream.read(block_size)
                if overflowed:
                    log.debug("microphone input overflow")
                raw = chunk.tobytes()
                samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                level = float(np.sqrt(np.mean(samples**2)) + 1e-9)
                peak = max(peak, level)

                if not speech_started:
                    noise_samples.append(level)
                    pre_roll.append(raw)
                    if len(pre_roll) > pre_roll_blocks:
                        pre_roll.pop(0)
                    if level > threshold:
                        speech_started = True
                        frames.extend(pre_roll)
                        silence_elapsed = 0.0
                    continue

                frames.append(raw)
                if level < threshold * 0.8:
                    silence_elapsed += block_seconds
                    if silence_elapsed >= silence_target:
                        break
                else:
                    silence_elapsed = 0.0

        pcm = b"".join(frames)
        noise_floor = float(np.mean(noise_samples)) if noise_samples else 0.0
        target = path or RECORDINGS_DIR / f"capture_{datetime.now():%Y%m%d_%H%M%S}.wav"

        if not pcm:
            media.write_wav(target, b"\x00\x00" * (sample_rate // 10), sample_rate)
            return Recording(str(target), 0.0, False, peak, noise_floor)

        media.write_wav(target, pcm, sample_rate)
        return Recording(str(target), len(pcm) / (2.0 * sample_rate), True, peak, noise_floor)

class SpeechRecognizer:
    """Local Whisper speech recognition with graceful degradation."""

    def __init__(self) -> None:
        self._model: Any = None
        self._model_name: str = ""
        self._load_lock = threading.Lock()
        self._loading = False
        self._last_error: str = ""
        self._last_transcript: Transcript | None = None

    # -- model lifecycle -------------------------------------------------- #
    @property
    def ready(self) -> bool:
        return self._model is not None

    @property
    def model_name(self) -> str:
        return self._model_name or settings.whisper_model

    def _load_model_sync(self) -> Any:
        """Load (and download on first use) the Whisper model. Blocking."""
        if self._model is not None:
            return self._model
        if not WHISPER_AVAILABLE:
            raise RuntimeError(
                "Local speech recognition needs 'faster-whisper' (pip install faster-whisper)."
            )
        with self._load_lock:
            if self._model is not None:
                return self._model
            self._loading = True
            try:
                log.info("loading Whisper model '%s' (first run downloads it)", settings.whisper_model)
                self._model = WhisperModel(
                    settings.whisper_model,
                    device=settings.whisper_device,
                    compute_type=settings.whisper_compute_type,
                    download_root=str(RECORDINGS_DIR.parent / "whisper"),
                )
                self._model_name = settings.whisper_model
                self._last_error = ""
                log.info("Whisper model ready")
                return self._model
            except Exception as exc:
                self._last_error = str(exc)
                raise
            finally:
                self._loading = False

    async def warmup(self) -> dict:
        """Pre-load the model so the first utterance is not slow."""
        if not WHISPER_AVAILABLE:
            return {"ok": False, "error": "faster-whisper is not installed.", "ready": False}
        try:
            await asyncio.to_thread(self._load_model_sync)
            return {"ok": True, "model": self.model_name, "ready": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc), "ready": False}

    async def status(self) -> dict:
        microphone = Microphone()
        devices = await asyncio.to_thread(microphone.devices)
        return {
            "provider": settings.stt_provider,
            "whisper_installed": WHISPER_AVAILABLE,
            "whisper_model": settings.whisper_model,
            "model_loaded": self.ready,
            "model_loading": self._loading,
            "language": settings.stt_language,
            "compute_type": settings.whisper_compute_type,
            "audio_available": AUDIO_AVAILABLE,
            "microphones": devices,
            "default_microphone": await asyncio.to_thread(microphone.default_device),
            "last_error": self._last_error,
            "last_transcript": self._last_transcript.as_dict() if self._last_transcript else None,
        }

    @property
    def last_transcript(self) -> dict | None:
        return self._last_transcript.as_dict() if self._last_transcript else None

    # -- transcription ---------------------------------------------------- #
    def _transcribe_sync(self, audio_path: str | Path, source: str) -> Transcript:
        """Run Whisper over an audio file. Blocking — call from a worker thread."""
        model = self._load_model_sync()
        language = None if settings.stt_language in {"", "auto"} else settings.stt_language
        segment_iter, info = model.transcribe(
            str(audio_path),
            language=language,
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
        )

        segments: list[dict[str, Any]] = []
        probabilities: list[float] = []
        for segment in segment_iter:
            text = (segment.text or "").strip()
            if not text:
                continue
            segments.append({"start": round(segment.start, 2), "end": round(segment.end, 2), "text": text})
            if segment.avg_logprob is not None:
                probabilities.append(math.exp(min(0.0, float(segment.avg_logprob))))

        return Transcript(
            text=" ".join(item["text"] for item in segments).strip(),
            source=source,
            language=str(getattr(info, "language", "") or ""),
            duration=float(getattr(info, "duration", 0.0) or 0.0),
            confidence=(sum(probabilities) / len(probabilities)) if probabilities else 0.0,
            segments=segments,
            audio_path=str(audio_path),
        )

    async def transcribe_file(self, audio_path: str | Path, source: str = "upload") -> Transcript:
        """Transcribe a WAV/MP3 file on disk."""
        path = Path(audio_path)
        if not path.exists():
            return Transcript(text="", source=source, error=f"Audio file not found: {path}", speech_detected=False)
        try:
            transcript = await asyncio.to_thread(self._transcribe_sync, path, source)
        except Exception as exc:
            self._last_error = str(exc)
            log.warning("transcription failed: %s", exc)
            transcript = Transcript(text="", source=source, audio_path=str(path), error=str(exc))
        self._last_transcript = transcript
        await bus.emit("transcript", **transcript.as_dict())
        return transcript

    async def transcribe_pcm(
        self,
        pcm: bytes,
        *,
        sample_rate: int = 16000,
        source: str = "browser",
    ) -> Transcript:
        """Transcribe raw 16-bit PCM (e.g. audio posted by the browser)."""
        target = RECORDINGS_DIR / f"upload_{datetime.now():%Y%m%d_%H%M%S_%f}.wav"
        media.write_wav(target, pcm, sample_rate)
        return await self.transcribe_file(target, source=source)

    async def listen(
        self,
        *,
        max_seconds: float | None = None,
        device: int | None = None,
        silence_ms: int | None = None,
    ) -> Transcript:
        """Record from the microphone and transcribe the result."""
        microphone = Microphone()
        try:
            recording = await asyncio.to_thread(
                microphone.record,
                max_seconds=max_seconds,
                device=device,
                silence_ms=silence_ms,
            )
        except Exception as exc:
            return Transcript(text="", source="microphone", error=str(exc), speech_detected=False)

        if not recording.speech_detected:
            transcript = Transcript(
                text="",
                source="microphone",
                speech_detected=False,
                audio_path=recording.path,
                error="I did not hear any speech.",
            )
            self._last_transcript = transcript
            return transcript

        transcript = await self.transcribe_file(recording.path, source="microphone")
        transcript.speech_detected = True
        return transcript


#: Shared recogniser + microphone helpers.
recognizer = SpeechRecognizer()
microphone = Microphone()


__all__ = [
    "AUDIO_AVAILABLE",
    "WHISPER_AVAILABLE",
    "Microphone",
    "Recording",
    "SpeechRecognizer",
    "Transcript",
    "microphone",
    "recognizer",
]