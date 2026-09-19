"""Long-term memory: facts JARVIS keeps about the operator and their world.

Memories are stored in SQLite with a category, an importance score and usage
statistics. The brain retrieves the most relevant ones (keyword overlap + recent
use + importance) before every reply, which is what gives JARVIS continuity
across sessions.
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from typing import Any

from db import session_scope
from models import Memory
from services.events import bus
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.memory")

_STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "to", "of", "in", "on", "for", "with",
    "my", "me", "i", "you", "your", "it", "that", "this", "be", "do", "does", "did", "have", "has", "had",
    "remember", "please", "jarvis", "about", "than", "then", "so", "if", "at", "by", "as", "from",
}

#: Phrases that signal an explicit request to memorise something.
REMEMBER_PATTERNS = (
    r"\bremember (?:that )?(?P<value>.+)$",
    r"\b(?:keep in mind|note that|make a note that|don'?t forget) (?:that )?(?P<value>.+)$",
    r"\bmy (?P<key>[a-z ]{2,40}) (?:is|are) (?P<value>.+)$",
)


def _words(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9']+", (text or "").lower()) if word not in _STOP_WORDS and len(word) > 2}


def remember(key: str, value: str, *, category: str = "general", importance: int = 3,
             source: str = "explicit") -> dict[str, Any]:
    """Store (or update) a memory keyed by a short label."""
    key = (key or "note").strip()[:120] or "note"
    value = (value or "").strip()
    with session_scope() as session:
        existing = (
            session.query(Memory)
            .filter(Memory.key == key)
            .order_by(Memory.id.desc())
            .first()
        )
        if existing is not None and existing.value.strip().lower() == value.lower():
            existing.importance = max(existing.importance, int(importance))
            return existing.as_dict()
        memory = Memory(key=key, value=value, category=category, importance=int(importance), source=source)
        session.add(memory)
        session.flush()
        return memory.as_dict()


def recall(query: str = "", *, limit: int = 8) -> list[dict[str, Any]]:
    """Retrieve memories ranked by relevance, importance and freshness."""
    terms = _words(query)
    with session_scope() as session:
        memories = session.query(Memory).all()
        scored: list[tuple[float, Memory]] = []
        for memory in memories:
            haystack = f"{memory.key} {memory.value} {memory.category}".lower()
            overlap = len(terms & _words(haystack))
            score = overlap * 3.0 + (memory.importance or 3) * 0.6 + min(memory.use_count or 0, 10) * 0.15
            if terms and overlap == 0 and (memory.importance or 0) < 4:
                continue
            scored.append((score, memory))
        scored.sort(key=lambda item: item[0], reverse=True)
        chosen = [memory for _score, memory in scored[:limit]]
        now = datetime.now()
        for memory in chosen:
            memory.use_count = (memory.use_count or 0) + 1
            memory.last_used_at = now
        return [memory.as_dict() for memory in chosen]


def forget(key_or_id: str) -> bool:
    """Delete a memory by id or by key (exact match, case-insensitive)."""
    with session_scope() as session:
        raw = str(key_or_id or "").strip()
        if raw.isdigit():
            memory = session.get(Memory, int(raw))
            if memory is None:
                return False
            session.delete(memory)
            return True
        match = (
            session.query(Memory)
            .filter(Memory.key.ilike(raw))
            .order_by(Memory.id.desc())
            .first()
        )
        if match is None:
            return False
        session.delete(match)
        return True


def all_memories(*, limit: int = 200) -> list[dict[str, Any]]:
    with session_scope() as session:
        memories = session.query(Memory).order_by(Memory.importance.desc(), Memory.id.desc()).limit(limit).all()
        return [memory.as_dict() for memory in memories]


def memory_context(query: str, *, limit: int = 6) -> str:
    """Compact memory block injected into the LLM system prompt."""
    items = recall(query, limit=limit) if query else recall("", limit=limit)
    if not items:
        return ""
    lines = [f"- {item['key']}: {item['value']}" for item in items]
    return "Things you remember about the operator:\n" + "\n".join(lines)


def extract_candidate(text: str) -> tuple[str, str] | None:
    """Pull a (key, value) pair out of an explicit "remember that …" request."""
    for pattern in REMEMBER_PATTERNS:
        found = re.search(pattern, text or "", re.IGNORECASE)
        if not found:
            continue
        groups = found.groupdict()
        value = (groups.get("value") or "").strip().strip(".!")
        if not value:
            continue
        key = (groups.get("key") or "").strip() or value[:48]
        return key.lower().strip(), value
    return None

@register
class RememberSkill(Skill):
    name = "remember"
    description = "Store a fact in long-term memory so it can be recalled later."
    category = "memory"
    examples = ("remember that I prefer dark mode", "my email is me@example.com")
    params = (
        Param("value", "string", "The fact to remember", required=True),
        Param("key", "string", "Short label for the fact"),
        Param("category", "string", "Category such as preference, contact or project", default="general"),
        Param("importance", "integer", "1 (trivial) to 5 (critical)", default=3),
    )
    patterns = REMEMBER_PATTERNS

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        value = str(kwargs.get("value") or "").strip().strip(".!")
        if not value:
            return SkillResult.failure("What should I remember?", "missing value")
        key = str(kwargs.get("key") or "").strip().lower() or value[:48]
        importance = int(kwargs.get("importance") or 3)
        category = str(kwargs.get("category") or "general")
        stored = await asyncio.to_thread(
            remember, key, value, category=category, importance=importance, source=ctx.source
        )
        await bus.emit("notification", text=f"Memory stored: {key}", level="info")
        return SkillResult.success(
            f"Noted. I will remember that {value}.",
            data=stored,
            display={"kind": "memory", "action": "remember", "key": key, "value": value},
        )


@register
class RecallSkill(Skill):
    name = "recall"
    description = "Retrieve what JARVIS remembers, optionally about a specific topic."
    category = "memory"
    examples = ("what do you remember about me", "what's my email")
    params = (
        Param("query", "string", "Topic to search memory for"),
        Param("limit", "integer", "Maximum number of memories", default=8),
    )
    patterns = (
        r"\bwhat do you (?:remember|know)(?: about (?P<query>.+))?\b",
        r"\b(?:recall|list|show) (?:my )?memories\b",
        r"\bdo you remember (?P<query>.+)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        query = str(kwargs.get("query") or "").strip()
        items = await asyncio.to_thread(recall, query, limit=int(kwargs.get("limit") or 8))
        if not items:
            return SkillResult.success(
                "I have not stored anything about that yet.",
                data={"memories": []},
                display={"kind": "memory", "action": "recall", "memories": []},
            )
        preview = "; ".join(f"{item['key']}: {item['value']}" for item in items[:5])
        return SkillResult.success(
            f"{'On that topic I remember' if query else 'Here is what I remember'}: {preview}.",
            data={"memories": items, "query": query},
            display={"kind": "memory", "action": "recall", "memories": items},
        )


@register
class ForgetSkill(Skill):
    name = "forget"
    description = "Delete something from long-term memory."
    category = "memory"
    dangerous = True
    requires_confirmation = True
    examples = ("forget my old email",)
    params = (Param("key", "string", "Memory key or id to forget", required=True),)
    patterns = (r"\bforget (?:about )?(?:that |my |the )?(?P<key>[a-z0-9][^?]{1,60})$",)
    confirm_template = "Shall I forget '{key}'?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        key = str(kwargs.get("key") or "").strip()
        if not key:
            return SkillResult.failure("What should I forget?", "missing key")
        removed = await asyncio.to_thread(forget, key)
        if not removed:
            return SkillResult.failure(f"I have no memory stored under '{key}'.", "not found")
        return SkillResult.success(f"Forgotten: {key}.", data={"key": key},
                                   display={"kind": "memory", "action": "forget", "key": key})


__all__ = [
    "ForgetSkill",
    "RecallSkill",
    "RememberSkill",
    "REMEMBER_PATTERNS",
    "all_memories",
    "extract_candidate",
    "forget",
    "memory_context",
    "recall",
    "remember",
]