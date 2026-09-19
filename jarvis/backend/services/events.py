"""Real-time event bus that pushes JARVIS state to every connected UI.

A single :class:`EventBus` instance (``bus``) is shared by the brain, the skills
and the scheduler. Events are JSON-serialisable dicts with a ``type`` field; the
frontend switches on that field to drive the HUD.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Iterable

log = logging.getLogger("jarvis.events")

#: Event types emitted by the backend (kept in one place for the frontend).
EVENT_TYPES: tuple[str, ...] = (
    "state",            # listening | thinking | executing | speaking | idle | error
    "transcript",       # speech recognition result
    "thought",          # reasoning step / plan line
    "tool_call",        # a skill is about to run
    "tool_result",      # skill finished
    "assistant",        # final answer for the turn
    "user",             # user message recorded
    "confirm_request",  # action awaiting operator approval
    "confirm_result",   # approval outcome
    "reminder",         # a reminder fired
    "notification",     # generic toast
    "stats",            # system telemetry snapshot
    "settings",         # settings changed
    "log",              # audit line
    "error",            # something failed
)


def make_event(event_type: str, **payload: Any) -> dict[str, Any]:
    """Build a timestamped event envelope."""
    return {
        "type": event_type,
        "ts": datetime.now(timezone.utc).isoformat(),
        "epoch": time.time(),
        **payload,
    }


class EventBus:
    """Fan-out bus with a small replay buffer for late-joining clients."""

    def __init__(self, history: int = 60) -> None:
        self._clients: set[Any] = set()
        self._history: deque[dict[str, Any]] = deque(maxlen=history)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._lock = asyncio.Lock()

    # -- lifecycle ------------------------------------------------------- #
    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Remember the serving loop so sync code can schedule emissions."""
        self._loop = loop

    @property
    def client_count(self) -> int:
        return len(self._clients)

    @property
    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

    # -- subscriptions --------------------------------------------------- #
    async def register(self, websocket: Any) -> None:
        async with self._lock:
            self._clients.add(websocket)
        log.info("UI connected (%d client(s))", len(self._clients))

    async def unregister(self, websocket: Any) -> None:
        async with self._lock:
            self._clients.discard(websocket)
        log.info("UI disconnected (%d client(s) left)", len(self._clients))

    # -- publishing ------------------------------------------------------ #
    async def publish(self, event: dict[str, Any]) -> None:
        """Send an event to every connected client, dropping dead sockets."""
        self._history.append(event)
        if not self._clients:
            return
        dead: list[Any] = []
        for client in list(self._clients):
            try:
                await client.send_json(event)
            except Exception as exc:  # socket closed / serialisation issue
                log.debug("dropping client after send failure: %s", exc)
                dead.append(client)
        if dead:
            async with self._lock:
                for client in dead:
                    self._clients.discard(client)

    async def emit(self, event_type: str, **payload: Any) -> None:
        await self.publish(make_event(event_type, **payload))

    def emit_soon(self, event_type: str, **payload: Any) -> None:
        """Fire-and-forget emit safe to call from sync code (e.g. threads)."""
        event = make_event(event_type, **payload)
        loop = self._loop
        if loop is None or loop.is_closed():
            self._history.append(event)
            return
        try:
            asyncio.run_coroutine_threadsafe(self.publish(event), loop)
        except RuntimeError:  # loop shutting down
            self._history.append(event)

    async def emit_many(self, events: Iterable[dict[str, Any]]) -> None:
        for event in events:
            await self.publish(event)


#: Shared singleton used across the backend.
bus = EventBus()


__all__ = ["EVENT_TYPES", "EventBus", "bus", "make_event"]