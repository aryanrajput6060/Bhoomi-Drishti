"""Database engine, session helpers and the persisted-settings overlay."""

from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session, sessionmaker

import config
from config import settings
from models import Base, SettingRow

log = logging.getLogger("jarvis.db")

engine = create_engine(
    settings.database_url,
    future=True,
    echo=False,
    connect_args={"check_same_thread": False, "timeout": 15},
)


@event.listens_for(engine, "connect")
def _sqlite_pragmas(dbapi_connection: Any, _record: Any) -> None:
    """Enable foreign keys + WAL so events and UI reads never block each other."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
    finally:
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def init_db() -> None:
    """Create all tables (idempotent)."""
    Base.metadata.create_all(engine)
    log.info("database ready at %s", settings.database_url)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional scope for background work (scheduler, workflows)."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Iterator[Session]:
    """FastAPI dependency."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# --------------------------------------------------------------------------- #
# Runtime settings persisted in SQLite
# --------------------------------------------------------------------------- #
#: Settings the operator may safely change from the UI (non-secret).
UI_EDITABLE_SETTINGS: tuple[str, ...] = (
    "assistant_name",
    "operator_name",
    "wake_word",
    "require_wake_word",
    "llm_provider",
    "llm_model",
    "llm_base_url",
    "llm_temperature",
    "tts_provider",
    "tts_voice",
    "tts_rate",
    "tts_enabled",
    "stt_provider",
    "whisper_model",
    "default_city",
    "search_provider",
    "projects_dir",
    "editor_command",
    "terminal_command",
    "browser_command",
    "confirm_dangerous",
    "shell_enabled",
    "file_ops_enabled",
    "history_turns",
)


def get_setting(session: Session, key: str, default: Any = None) -> Any:
    row = session.get(SettingRow, key)
    return row.value if row is not None else default


def set_setting(session: Session, key: str, value: Any) -> None:
    row = session.get(SettingRow, key)
    if row is None:
        session.add(SettingRow(key=key, value=value))
    else:
        row.value = value


def load_persisted_settings() -> dict[str, Any]:
    """Read the DB overlay and apply it to :data:`config.settings`."""
    overrides: dict[str, Any] = {}
    with session_scope() as session:
        for row in session.scalars(select(SettingRow)):
            overrides[row.key] = row.value
    valid = {k: v for k, v in overrides.items() if hasattr(settings, k)}
    if valid:
        config.settings = settings.update(**valid)
        log.info("applied %d persisted setting(s): %s", len(valid), ", ".join(sorted(valid)))
    return valid


def save_settings(changes: dict[str, Any]) -> dict[str, Any]:
    """Persist UI changes and immediately update the live settings object."""
    applied: dict[str, Any] = {}
    with session_scope() as session:
        for key, value in changes.items():
            if key not in UI_EDITABLE_SETTINGS or not hasattr(settings, key):
                continue
            coerced = _coerce_like(getattr(settings, key), value)
            set_setting(session, key, coerced)
            applied[key] = coerced
    if applied:
        config.settings = config.settings.update(**applied)
    log.info("settings updated: %s", json.dumps(applied, default=str))
    return applied


def _coerce_like(current: Any, value: Any) -> Any:
    """Coerce a JSON value from the UI into the type of the current setting."""
    if isinstance(current, bool):
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)
    if isinstance(current, int) and not isinstance(value, bool):
        try:
            return int(value)
        except (TypeError, ValueError):
            return current
    if isinstance(current, float):
        try:
            return float(value)
        except (TypeError, ValueError):
            return current
    return value


__all__ = [
    "engine",
    "SessionLocal",
    "get_db",
    "session_scope",
    "init_db",
    "load_persisted_settings",
    "save_settings",
    "get_setting",
    "set_setting",
    "UI_EDITABLE_SETTINGS",
]