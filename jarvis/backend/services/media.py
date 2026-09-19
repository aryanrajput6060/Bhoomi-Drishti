"""Audio playback and WAV helpers.

WAV files are played with the stdlib ``winsound`` module; compressed formats
(MP3 from edge-tts) are played through the Windows MCI interface in ``winmm``
via ctypes. Both are synchronous by design — callers run them in a worker thread
so the asyncio event loop stays responsive.
"""

from __future__ import annotations

import ctypes
import logging
import os
import struct
import wave
from pathlib import Path

from config import IS_WINDOWS

log = logging.getLogger("jarvis.audio")

MCI_ALIAS = "jarvis_playback"
COMPRESSED_SUFFIXES = {".mp3", ".m4a", ".wma", ".aac"}
WAV_SUFFIXES = {".wav"}


class AudioPlaybackError(RuntimeError):
    """Raised when audio cannot be played on this machine."""


def _mci(command: str) -> str:
    """Send a command string to the Windows MCI interface."""
    if not IS_WINDOWS:  # pragma: no cover - Windows-only feature
        raise AudioPlaybackError("Audio playback through MCI requires Windows.")
    buffer = ctypes.create_unicode_buffer(512)
    result = ctypes.windll.winmm.mciSendStringW(command, buffer, 511, None)
    if result != 0:
        raise AudioPlaybackError(f"MCI error {result} for command: {command}")
    return buffer.value


def _mci_quiet(command: str) -> None:
    try:
        _mci(command)
    except AudioPlaybackError as exc:
        log.debug("ignored MCI error: %s", exc)


def play_file_sync(path: str | Path) -> None:
    """Play an audio file and block until it finishes."""
    target = Path(path)
    if not target.exists():
        raise AudioPlaybackError(f"Audio file not found: {target}")

    suffix = target.suffix.lower()
    if suffix in WAV_SUFFIXES and IS_WINDOWS:
        import winsound

        try:
            winsound.PlaySound(str(target), winsound.SND_FILENAME)
            return
        except RuntimeError as exc:  # fall through to MCI
            log.debug("winsound failed (%s); retrying with MCI", exc)

    if not IS_WINDOWS:  # pragma: no cover
        raise AudioPlaybackError("Audio playback requires Windows.")

    _mci_quiet(f"close {MCI_ALIAS}")
    _mci(f'open "{target}" type mpegvideo alias {MCI_ALIAS}')
    try:
        _mci(f"play {MCI_ALIAS} wait")
    finally:
        _mci_quiet(f"close {MCI_ALIAS}")


def stop_playback() -> None:
    """Interrupt any audio started through the MCI alias."""
    if IS_WINDOWS:
        _mci_quiet(f"stop {MCI_ALIAS}")
        _mci_quiet(f"close {MCI_ALIAS}")


def play_system_sound(name: str = "SystemAsterisk") -> None:
    """Play a built-in Windows sound without needing an asset file."""
    if not IS_WINDOWS:
        return
    try:
        import winsound

        alias = {
            "info": "SystemAsterisk",
            "warning": "SystemExclamation",
            "error": "SystemHand",
            "confirm": "SystemQuestion",
        }.get(name, name)
        winsound.PlaySound(alias, winsound.SND_ALIAS | winsound.SND_ASYNC)
    except Exception as exc:  # pragma: no cover - best effort only
        log.debug("system sound %s failed: %s", name, exc)


# --------------------------------------------------------------------------- #
# WAV helpers
# --------------------------------------------------------------------------- #
def write_wav(path: str | Path, pcm_bytes: bytes, sample_rate: int = 16000,
              channels: int = 1, sample_width: int = 2) -> Path:
    """Write raw PCM bytes to a WAV container."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(target), "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(sample_width)
        handle.setframerate(sample_rate)
        handle.writeframes(pcm_bytes)
    return target


def read_wav(path: str | Path) -> tuple[bytes, int, int, int]:
    """Return ``(pcm_bytes, sample_rate, channels, sample_width)``."""
    with wave.open(str(path), "rb") as handle:
        return handle.readframes(handle.getnframes()), handle.getframerate(), handle.getnchannels(), handle.getsampwidth()


def wav_duration(path: str | Path) -> float:
    """Duration of a WAV file in seconds (0.0 when unreadable)."""
    try:
        with wave.open(str(path), "rb") as handle:
            rate = handle.getframerate() or 1
            return handle.getnframes() / float(rate)
    except Exception:
        return 0.0


def wav_pcm_from_float32(pcm: bytes) -> bytes:
    """Convert little-endian float32 PCM to 16-bit PCM (Whisper input helper)."""
    count = len(pcm) // 4
    samples = struct.unpack(f"<{count}f", pcm[: count * 4])
    clipped = bytearray()
    for sample in samples:
        value = int(max(-1.0, min(1.0, sample)) * 32767)
        clipped += struct.pack("<h", value)
    return bytes(clipped)


__all__ = [
    "AudioPlaybackError",
    "play_file_sync",
    "play_system_sound",
    "read_wav",
    "stop_playback",
    "wav_duration",
    "wav_pcm_from_float32",
    "write_wav",
]