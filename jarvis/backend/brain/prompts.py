"""System prompt builder for the LLM brain (part 1)."""

from __future__ import annotations

from config import settings


def build_system_prompt(*, memory_block: str = "", skill_catalog: str = "") -> str:
    name = settings.assistant_name or "JARVIS"
    operator = settings.operator_name or "Sir"
    lines = [
        f"You are {name}, a precise desktop assistant for {operator} on Windows.",
        "You control this machine through tools. Prefer calling a tool over guessing.",
        "Keep spoken replies short (1-3 sentences) unless the user asks for detail.",
        "Never claim an action succeeded unless a tool confirmed it.",
        "For destructive actions, explain briefly and wait for confirmation.",
    ]
    if memory_block:
        lines += ["", memory_block]
    if skill_catalog:
        lines += ["", "You have these tool categories available:", skill_catalog]
    return "\n".join(lines)
