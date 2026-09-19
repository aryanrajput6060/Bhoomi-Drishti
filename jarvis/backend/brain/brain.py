"""JARVIS brain: intent routing, LLM reasoning and multi-step orchestration."""
from __future__ import annotations
import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from config import settings
from db import session_scope
from models import Conversation, Message
from services import audit
from services.events import bus
from services.safety import confirmations
from skills import get_registry
from skills.base import Skill, SkillContext, SkillResult
from skills.memory_skill import memory_context
from brain.prompts import build_system_prompt
from brain.workflows import split_steps
log = logging.getLogger("jarvis.brain")
try:
    from services import llm as llm_client
except Exception:
    llm_client = None  # type: ignore[assignment]
_SMALLTALK = {
    "hello": "Hello {op}. All systems are online.",
    "hi": "Hello {op}. How can I help?",
    "hey": "Yes {op}? I'm listening.",
    "good morning": "Good morning {op}. What shall we work on first?",
    "good afternoon": "Good afternoon {op}.",
    "good evening": "Good evening {op}.",
    "good night": "Good night {op}. I'll keep watch.",
    "how are you": "Running at full capacity, {op}. How can I assist?",
    "thank you": "Always a pleasure, {op}.",
    "thanks": "Anytime, {op}.",
    "bye": "Standing by, {op}.",
    "goodbye": "Goodbye {op}. I'll be here when you need me.",
}
_WAKE_STRIP = re.compile(r"^(jarvis|hey jarvis|ok jarvis|computer)[,\s:;-]+", re.IGNORECASE)
@dataclass(slots=True)
class TurnResult:
    speech: str
    ok: bool = True
    intent: str = ""
    skill: str = ""
    conversation_id: int | None = None
    data: dict[str, Any] = field(default_factory=dict)
    display: dict[str, Any] | None = None
    requires_confirmation: bool = False
    confirm_prompt: str = ""
    confirm_token: str = ""
    latency_ms: float = 0.0
    def as_dict(self) -> dict[str, Any]:
        return {"speech": self.speech, "ok": self.ok, "intent": self.intent,
                "skill": self.skill, "conversation_id": self.conversation_id,
                "data": self.data, "display": self.display,
                "requires_confirmation": self.requires_confirmation,
                "confirm_prompt": self.confirm_prompt, "confirm_token": self.confirm_token,
                "latency_ms": round(self.latency_ms, 1)}
