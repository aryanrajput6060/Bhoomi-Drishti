"""Reminder and timer scheduling on top of APScheduler.

Reminders live in SQLite and are re-registered on startup, so they survive a
restart. When one fires, JARVIS announces it out loud, pushes a WebSocket event
to the HUD, and marks the row as fired (rescheduling repeating reminders).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db import session_scope
from models import Reminder
from services.events import bus

log = logging.getLogger("jarvis.scheduler")


class ReminderScheduler:
    """Owns every scheduled reminder and timer for the running JARVIS process."""

    def __init__(self) -> None:
        self._scheduler: AsyncIOScheduler | None = None
        self._started = False

    # -- lifecycle -------------------------------------------------------- #
    def start(self) -> None:
        if self._started:
            return
        self._scheduler = AsyncIOScheduler()
        self._scheduler.start()
        self._started = True
        restored = self._load_existing()
        log.info("scheduler started (%d reminder(s) restored)", restored)

    def shutdown(self) -> None:
        if self._scheduler is not None:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception as exc:  # pragma: no cover
                log.debug("scheduler shutdown issue: %s", exc)
        self._started = False

    @property
    def running(self) -> bool:
        return bool(self._scheduler and self._scheduler.running)

    @property
    def job_count(self) -> int:
        return len(self._scheduler.get_jobs()) if self._scheduler else 0

    # -- jobs ------------------------------------------------------------- #
    def _load_existing(self) -> int:
        """Re-arm every active reminder stored in the database."""
        count = 0
        with session_scope() as session:
            for reminder in session.query(Reminder).filter(Reminder.is_active.is_(True)).all():
                fire_at = reminder.fire_at
                if fire_at is None:
                    continue
                if fire_at <= datetime.now():
                    # Missed while JARVIS was offline — fire shortly after startup.
                    fire_at = datetime.now() + timedelta(seconds=20)
                    reminder.fire_at = fire_at
                self._arm(reminder.id, reminder.title, fire_at, reminder.repeat)
                count += 1
        return count

    def _arm(self, reminder_id: int, title: str, fire_at: datetime, repeat: str) -> None:
        if self._scheduler is None:
            return
        self._scheduler.add_job(
            self._fire,
            trigger="date",
            run_date=fire_at,
            args=[reminder_id],
            id=f"reminder-{reminder_id}",
            name=title,
            replace_existing=True,
            misfire_grace_time=300,
        )

    def add_reminder(self, title: str, fire_at: datetime, *, repeat: str = "none") -> dict[str, Any]:
        """Create a reminder row and schedule it."""
        with session_scope() as session:
            reminder = Reminder(title=title, fire_at=fire_at, repeat=repeat or "none", is_active=True)
            session.add(reminder)
            session.flush()
            payload = reminder.as_dict()
            reminder_id = int(reminder.id)
        self._arm(reminder_id, title, fire_at, repeat)
        return payload

    def add_timer(self, seconds: float, label: str = "Timer") -> dict[str, Any]:
        """One-shot timer that speaks when it expires."""
        fire_at = datetime.now() + timedelta(seconds=max(1.0, float(seconds)))
        return self.add_reminder(label, fire_at, repeat="none")

    def cancel(self, reminder_id: int) -> bool:
        if self._scheduler is not None:
            try:
                self._scheduler.remove_job(f"reminder-{reminder_id}")
            except Exception:
                pass
        with session_scope() as session:
            reminder = session.get(Reminder, reminder_id)
            if reminder is None:
                return False
            reminder.is_active = False
        return True

    def list_reminders(self, *, active_only: bool = False) -> list[dict[str, Any]]:
        with session_scope() as session:
            query = session.query(Reminder).order_by(Reminder.fire_at)
            if active_only:
                query = query.filter(Reminder.is_active.is_(True))
            return [reminder.as_dict() for reminder in query.all()]

    # -- firing ----------------------------------------------------------- #
    async def _fire(self, reminder_id: int) -> None:
        """Handle a reminder coming due."""
        payload: dict[str, Any] | None = None
        next_fire: datetime | None = None

        with session_scope() as session:
            reminder = session.get(Reminder, reminder_id)
            if reminder is None or not reminder.is_active:
                return
            reminder.fired_count = (reminder.fired_count or 0) + 1
            reminder.last_fired_at = datetime.now()
            repeat = (reminder.repeat or "none").lower()

            if repeat == "daily":
                next_fire = reminder.fire_at + timedelta(days=1)
            elif repeat == "weekly":
                next_fire = reminder.fire_at + timedelta(weeks=1)
            elif repeat == "weekdays":
                candidate = reminder.fire_at + timedelta(days=1)
                while candidate.weekday() >= 5:
                    candidate += timedelta(days=1)
                next_fire = candidate
            elif repeat == "monthly":
                next_fire = reminder.fire_at + timedelta(days=30)

            if next_fire is not None:
                reminder.fire_at = next_fire
            else:
                reminder.is_active = False
            payload = reminder.as_dict()

        title = (payload or {}).get("title", "Reminder")
        log.info("reminder fired: %s", title)

        await bus.emit("reminder", reminder=payload, message=f"Reminder: {title}")

        if next_fire is not None:
            self._arm(reminder_id, title, next_fire, (payload or {}).get("repeat", "none"))

        await self.speak(f"Reminder. {title}.")

    async def speak(self, message: str) -> None:
        """Announce something out loud (best effort — never raises)."""
        try:
            from services.tts import tts

            await tts.speak_in_background(message)
        except Exception as exc:  # pragma: no cover - speech is optional
            log.debug("could not announce: %s", exc)

    async def announce(self, message: str, *, level: str = "info", spoken: bool = True) -> None:
        """Push and optionally speak a notification (used by workflows)."""
        await bus.emit("notification", text=message, level=level)
        if spoken:
            await self.speak(message)


#: Shared scheduler instance.
scheduler = ReminderScheduler()


async def wait(seconds: float) -> None:
    """Pause between workflow steps."""
    await asyncio.sleep(seconds)


__all__ = ["ReminderScheduler", "scheduler", "wait"]