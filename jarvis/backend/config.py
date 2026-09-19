"""
JARVIS — central configuration.

Every tunable comes from an environment variable (see ``.env.example``) so that
no secret or machine-specific value is ever hard-coded. A dependency-light
loader is used instead of ``pydantic-settings`` so JARVIS starts on a stock
Python install with only the packages in ``requirements.txt``.

The environment-variable name for a field is ``JARVIS_`` + the field name in
upper case (``JARVIS_LLM_MODEL`` -> ``llm_model``), with a small alias table for
industry-standard names such as ``OPENAI_API_KEY``.
"""

from __future__ import annotations

import dataclasses
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # python-dotenv is required, but JARVIS must never crash without it
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - defensive only
    def load_dotenv(*_a: Any, **_k: Any) -> bool:  # type: ignore[misc]
        return False

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
BASE_DIR: Path = Path(__file__).resolve().parent.parent          # .../jarvis
BACKEND_DIR: Path = BASE_DIR / "backend"
FRONTEND_DIR: Path = BASE_DIR / "frontend"
FRONTEND_DIST: Path = FRONTEND_DIR / "dist"

DATA_DIR: Path = BACKEND_DIR / "data"
ASSETS_DIR: Path = DATA_DIR / "assets"
SCREENSHOT_DIR: Path = DATA_DIR / "screenshots"
TTS_CACHE_DIR: Path = DATA_DIR / "tts_cache"
RECORDINGS_DIR: Path = DATA_DIR / "recordings"
SCRIPTS_DIR: Path = BACKEND_DIR / "scripts"

for _folder in (DATA_DIR, ASSETS_DIR, SCREENSHOT_DIR, TTS_CACHE_DIR, RECORDINGS_DIR):
    _folder.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env", override=False)
IS_WINDOWS: bool = sys.platform.startswith("win")


# --------------------------------------------------------------------------- #
# Coercion helpers
# --------------------------------------------------------------------------- #
def _csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _coerce(default: Any, raw: str) -> Any:
    """Convert a raw environment string to the type of ``default``."""
    raw = raw.strip()
    if isinstance(default, bool):
        return raw.lower() in {"1", "true", "yes", "y", "on", "enabled"}
    if isinstance(default, int):
        try:
            return int(float(raw))
        except ValueError:
            return default
    if isinstance(default, float):
        try:
            return float(raw)
        except ValueError:
            return default
    if isinstance(default, list):
        return _csv(raw)
    return raw


# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class Settings:
    """Runtime configuration for JARVIS (all fields overridable via env vars)."""

    # identity
    assistant_name: str = "JARVIS"
    operator_name: str = "Sir"
    wake_word: str = "jarvis"
    require_wake_word: bool = False

    # server
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"])

    # AI brain
    llm_provider: str = "auto"          # auto | openai | anthropic | gemini | ollama | none
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = ""
    llm_temperature: float = 0.4
    llm_max_tokens: int = 1024
    llm_timeout: float = 60.0
    llm_max_steps: int = 6              # tool-calling loop budget
    vision_model: str = ""

    # speech to text
    stt_provider: str = "auto"          # auto | whisper | browser | none
    whisper_model: str = "base.en"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    stt_language: str = "en"
    mic_sample_rate: int = 16000
    vad_silence_ms: int = 900
    vad_threshold: float = 0.012
    max_record_seconds: int = 20

    # text to speech
    tts_provider: str = "auto"          # auto | edge | sapi | off
    tts_voice: str = "en-GB-RyanNeural"
    tts_sapi_voice: str = ""
    tts_rate: int = 0                   # SAPI rate, -10..10
    tts_volume: int = 100
    tts_enabled: bool = True

    # safety
    extra_allowed_roots: list[str] = field(default_factory=list)
    file_ops_enabled: bool = True
    shell_enabled: bool = True
    shell_allowlist: list[str] = field(default_factory=list)
    shell_timeout: int = 120
    confirm_dangerous: bool = True

    # integrations
    search_provider: str = "auto"       # auto | duckduckgo | tavily | serper | brave
    tavily_api_key: str = ""
    serper_api_key: str = ""
    brave_api_key: str = ""
    home_assistant_url: str = ""
    home_assistant_token: str = ""
    webhook_url: str = ""
    webhook_secret: str = ""
    weather_latitude: str = ""
    weather_longitude: str = ""
    default_city: str = ""

    # developer workflows
    projects_dir: str = ""
    editor_command: str = ""
    terminal_command: str = ""
    browser_command: str = ""

    # memory / context
    history_turns: int = 12
    memory_enabled: bool = True
    identity_facts: list[str] = field(default_factory=list)


    # ------------------------------------------------------------------ #
    @classmethod
    def from_env(cls) -> "Settings":
        """Build a Settings instance from environment variables / .env."""
        aliases: dict[str, tuple[str, ...]] = {
            "llm_api_key": ("JARVIS_LLM_API_KEY", "OPENAI_API_KEY", "JARVIS_OPENAI_API_KEY"),
            "llm_model": ("JARVIS_LLM_MODEL", "OPENAI_MODEL"),
            "llm_base_url": ("JARVIS_LLM_BASE_URL", "OPENAI_BASE_URL"),
            "tavily_api_key": ("JARVIS_TAVILY_API_KEY", "TAVILY_API_KEY"),
            "serper_api_key": ("JARVIS_SERPER_API_KEY", "SERPER_API_KEY"),
            "brave_api_key": ("JARVIS_BRAVE_API_KEY", "BRAVE_API_KEY"),
            "home_assistant_url": ("JARVIS_HA_URL", "HOME_ASSISTANT_URL"),
            "home_assistant_token": ("JARVIS_HA_TOKEN", "HOME_ASSISTANT_TOKEN"),
        }
        values: dict[str, Any] = {}
        for spec in dataclasses.fields(cls):
            if spec.default is not dataclasses.MISSING:
                default: Any = spec.default
            elif spec.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
                default = spec.default_factory()  # type: ignore[misc]
            else:
                default = None
            candidates = aliases.get(spec.name, (f"JARVIS_{spec.name.upper()}",))
            for env_name in candidates:
                raw = os.environ.get(env_name)
                if raw is not None and raw.strip() != "":
                    values[spec.name] = _coerce(default, raw)
                    break
        if isinstance(values.get("wake_word"), str):
            values["wake_word"] = values["wake_word"].lower()
        for lower_field in ("llm_provider", "stt_provider", "tts_provider", "search_provider"):
            if isinstance(values.get(lower_field), str):
                values[lower_field] = values[lower_field].lower()
        return cls(**values)

    # ------------------------------------------------------------------ #
    def update(self, **changes: Any) -> "Settings":
        """Return a copy with ``changes`` applied (used by the settings API)."""
        clean = {k: v for k, v in changes.items() if hasattr(self, k) and v is not None}
        return dataclasses.replace(self, **clean)

    @property
    def database_url(self) -> str:
        return f"sqlite:///{(DATA_DIR / 'jarvis.db').as_posix()}"

    @property
    def allowed_roots(self) -> list[Path]:
        """Directories that file skills are permitted to touch."""
        roots: list[Path] = []
        for candidate in (Path.home(), *[Path(p) for p in self.extra_allowed_roots]):
            try:
                resolved = candidate.expanduser().resolve()
            except OSError:
                continue
            if resolved not in roots:
                roots.append(resolved)
        return roots

    def provider_summary(self) -> dict[str, Any]:
        """Non-secret description of integration state (used by /api/status)."""
        return {
            "assistant_name": self.assistant_name,
            "operator_name": self.operator_name,
            "llm": {
                "provider": self.llm_provider,
                "model": self.llm_model or "(provider default)",
                "api_key_present": bool(self.llm_api_key),
                "base_url": self.llm_base_url or "(provider default)",
            },
            "stt": {"provider": self.stt_provider, "model": self.whisper_model},
            "tts": {"provider": self.tts_provider, "voice": self.tts_voice, "enabled": self.tts_enabled},
            "search": {
                "provider": self.search_provider,
                "tavily": bool(self.tavily_api_key),
                "serper": bool(self.serper_api_key),
                "brave": bool(self.brave_api_key),
            },
            "home_assistant": bool(self.home_assistant_url and self.home_assistant_token),
            "webhook": bool(self.webhook_url),
            "shell_enabled": self.shell_enabled,
            "file_ops_enabled": self.file_ops_enabled,
            "weather_configured": bool(self.default_city or (self.weather_latitude and self.weather_longitude)),
        }


settings: Settings = Settings.from_env()


def reload_settings() -> Settings:
    """Re-read .env/environment and refresh the module-level singleton."""
    global settings
    load_dotenv(BASE_DIR / ".env", override=False)
    settings = Settings.from_env()
    return settings