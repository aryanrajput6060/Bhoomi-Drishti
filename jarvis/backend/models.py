"""SQLAlchemy ORM models — JARVIS local persistent state.

Everything JARVIS knows lives in one SQLite file (``backend/data/jarvis.db``):
conversations, long-term memory, tasks, reminders, notes and the audit trail of
every action the assistant performed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class Base(DeclarativeBase):
    """Declarative base for all JARVIS tables."""


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), default="New conversation")
    source: Mapped[str] = mapped_column(String(20), default="text")  # text | voice | system
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.id"
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "created_at": _iso(self.created_at),
            "updated_at": _iso(self.updated_at),
        }


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))           # user | assistant | system | tool
    content: Mapped[str] = mapped_column(Text, default="")
    intent: Mapped[str] = mapped_column(String(80), default="")
    skill: Mapped[str] = mapped_column(String(80), default="")
    ok: Mapped[bool] = mapped_column(Boolean, default=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    meta: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "intent": self.intent,
            "skill": self.skill,
            "ok": self.ok,
            "latency_ms": round(self.latency_ms, 2),
            "meta": self.meta or {},
            "created_at": _iso(self.created_at),
        }


class Memory(Base):
    """A long-term fact JARVIS remembers about the user or their environment."""

    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(60), default="general", index=True)
    importance: Mapped[int] = mapped_column(Integer, default=3)      # 1 (trivial) .. 5 (critical)
    source: Mapped[str] = mapped_column(String(40), default="explicit")
    use_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "importance": self.importance,
            "source": self.source,
            "use_count": self.use_count,
            "created_at": _iso(self.created_at),
            "last_used_at": _iso(self.last_used_at),
        }

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)   # open | done
    priority: Mapped[int] = mapped_column(Integer, default=2)                     # 1 high, 2 normal, 3 low
    project: Mapped[str] = mapped_column(String(80), default="")
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "notes": self.notes,
            "status": self.status,
            "priority": self.priority,
            "project": self.project,
            "due_at": _iso(self.due_at),
            "created_at": _iso(self.created_at),
            "completed_at": _iso(self.completed_at),
        }


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    fire_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    repeat: Mapped[str] = mapped_column(String(20), default="none")   # none | daily | weekly | weekdays
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    fired_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    last_fired_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "fire_at": _iso(self.fire_at),
            "repeat": self.repeat,
            "is_active": self.is_active,
            "fired_count": self.fired_count,
            "last_fired_at": _iso(self.last_fired_at),
        }


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), default="Untitled note")
    content: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(String(200), default="")
    pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "pinned": self.pinned,
            "created_at": _iso(self.created_at),
            "updated_at": _iso(self.updated_at),
        }


class AuditEntry(Base):
    """Record of every skill execution — powers the audit trail in the UI."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    skill: Mapped[str] = mapped_column(String(80), index=True)
    args: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    ok: Mapped[bool] = mapped_column(Boolean, default=True)
    risky: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    speech: Mapped[str] = mapped_column(Text, default="")
    error: Mapped[str] = mapped_column(Text, default="")

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": _iso(self.created_at),
            "skill": self.skill,
            "args": self.args or {},
            "ok": self.ok,
            "risky": self.risky,
            "confirmed": self.confirmed,
            "duration_ms": round(self.duration_ms or 0.0, 2),
            "speech": self.speech,
            "error": self.error,
        }


class SettingRow(Base):
    """Key/value store for runtime settings changed from the UI."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[Any] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


__all__ = [
    "Base",
    "Conversation",
    "Message",
    "Memory",
    "Task",
    "Reminder",
    "Note",
    "AuditEntry",
    "SettingRow",
    "utcnow",
]