"""Skill framework: the unit of capability inside JARVIS.

A *skill* is a self-contained, testable action (open an app, read the screen,
search the web, set a reminder …). Each skill:

* declares typed :class:`Param` s which are published as a JSON schema so the LLM
  brain can call it through native function calling,
* may declare regex :attr:`Skill.patterns` so the offline intent router can run
  it **without any API key**, with named groups mapping to parameters,
* returns a :class:`SkillResult` carrying what to say, what to show, and whether
  operator confirmation is required.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

PARAM_TYPES = {"string", "integer", "number", "boolean", "array"}


@dataclass(slots=True)
class Param:
    """A single named input accepted by a skill."""

    name: str
    type: str = "string"
    description: str = ""
    required: bool = False
    default: Any = None
    enum: list[str] | None = None
    items: str | None = None  # element type when type == "array"

    def to_schema(self) -> dict[str, Any]:
        schema: dict[str, Any] = {"type": self.type if self.type in PARAM_TYPES else "string"}
        if self.description:
            schema["description"] = self.description
        if self.enum:
            schema["enum"] = list(self.enum)
        if self.type == "array":
            schema["items"] = {"type": self.items or "string"}
        if self.default is not None:
            schema["default"] = self.default
        return schema

    def coerce(self, value: Any) -> Any:
        """Best-effort conversion of an LLM/UI supplied value to the declared type."""
        if value is None:
            return self.default
        try:
            if self.type == "integer":
                return int(value)
            if self.type == "number":
                return float(value)
            if self.type == "boolean":
                if isinstance(value, str):
                    return value.strip().lower() in {"1", "true", "yes", "on"}
                return bool(value)
            if self.type == "array":
                if isinstance(value, str):
                    return [item.strip() for item in value.split(",") if item.strip()]
                return list(value)
            return str(value)
        except (TypeError, ValueError):
            return self.default


@dataclass
class SkillResult:
    """Everything a skill reports back to the brain and the HUD."""

    ok: bool = True
    speech: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    display: dict[str, Any] | None = None
    requires_confirmation: bool = False
    confirm_prompt: str = ""
    token: str = ""
    error: str = ""
    skipped: bool = False

    @classmethod
    def success(cls, speech: str = "", data: dict[str, Any] | None = None,
                display: dict[str, Any] | None = None) -> "SkillResult":
        return cls(ok=True, speech=speech, data=data or {}, display=display)

    @classmethod
    def failure(cls, speech: str = "", error: str = "") -> "SkillResult":
        return cls(ok=False, speech=speech or error, error=error or speech)

    @classmethod
    def confirm(cls, prompt: str, token: str = "", **data: Any) -> "SkillResult":
        return cls(ok=True, requires_confirmation=True, confirm_prompt=prompt, token=token,
                   data=data, speech=prompt)

    @classmethod
    def skip(cls, speech: str = "", **data: Any) -> "SkillResult":
        return cls(ok=True, skipped=True, speech=speech, data=data)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "speech": self.speech,
            "data": self.data,
            "display": self.display,
            "requires_confirmation": self.requires_confirmation,
            "confirm_prompt": self.confirm_prompt,
            "token": self.token,
            "skipped": self.skipped,
            "error": self.error,
        }


@dataclass(slots=True)
class SkillContext:
    """Ambient information about the request being served."""

    conversation_id: int | None = None
    session_id: str = ""
    source: str = "text"                 # text | voice | api | workflow | scheduler
    raw_text: str = ""
    confirmed: bool = False
    confirm_token: str = ""
    extras: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.extras.get(key, default)

class Skill(ABC):
    """Base class for every JARVIS capability."""

    #: Machine name used by the brain, the API and the audit log.
    name: str = ""
    #: One-line description shown to the LLM and the UI.
    description: str = ""
    #: Grouping for the UI (system, files, web, productivity, memory, automation).
    category: str = "general"
    #: Declared inputs.
    params: tuple[Param, ...] = ()
    #: Natural-language examples shown in the help panel.
    examples: tuple[str, ...] = ()
    #: Regular expressions for the offline intent router. Named groups become
    #: keyword arguments passed to :meth:`run`.
    patterns: tuple[str, ...] = ()
    #: True when the action can change or destroy something.
    dangerous: bool = False
    #: True when the operator must approve the action first.
    requires_confirmation: bool = False
    #: True when the skill works without any LLM provider configured.
    works_offline: bool = True
    #: Sentence used when asking for confirmation ("Shall I {action}?").
    confirm_template: str = "Shall I {action}?"

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._compiled = tuple(re.compile(pattern, re.IGNORECASE) for pattern in cls.patterns)

    # -- execution -------------------------------------------------------- #
    @abstractmethod
    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        """Perform the action. Must never raise — return a failed SkillResult."""

    # -- introspection ---------------------------------------------------- #
    def tool_schema(self) -> dict[str, Any]:
        """OpenAI-style function/tool schema used by the LLM brain."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {param.name: param.to_schema() for param in self.params},
                    "required": [param.name for param in self.params if param.required],
                },
            },
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "dangerous": self.dangerous,
            "requires_confirmation": self.requires_confirmation,
            "works_offline": self.works_offline,
            "examples": list(self.examples),
            "patterns": list(self.patterns),
            "params": [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                    "default": param.default,
                    "enum": param.enum,
                }
                for param in self.params
            ],
        }

    def match(self, text: str) -> re.Match[str] | None:
        """First declared pattern that matches ``text``."""
        for pattern in getattr(self, "_compiled", ()):
            found = pattern.search(text)
            if found:
                return found
        return None

    def clean_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Drop empty values and coerce declared parameters to their types."""
        declared = {param.name: param for param in self.params}
        cleaned: dict[str, Any] = {}
        for key, value in kwargs.items():
            if value is None:
                continue
            if key in declared:
                coerced = declared[key].coerce(value)
                if coerced is None or coerced == "":
                    continue
                cleaned[key] = coerced
            else:
                cleaned[key] = value
        return cleaned

    def missing_required(self, kwargs: dict[str, Any]) -> list[str]:
        return [param.name for param in self.params if param.required and kwargs.get(param.name) in (None, "")]

    def confirm_prompt(self, kwargs: dict[str, Any]) -> str:
        described = _describe_action(self.name, kwargs)
        safe_values = {key: value for key, value in kwargs.items() if isinstance(value, (str, int, float))}
        try:
            return self.confirm_template.format(action=described, **safe_values)
        except (KeyError, IndexError):
            return f"Shall I {described}?"

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Skill {self.name}>"


#: Friendly phrasing for the confirmation prompt.
_ACTION_VERBS: dict[str, str] = {
    "close_app": "close {name}",
    "delete_path": "delete {path}",
    "run_command": "run the command '{command}'",
    "power_action": "{action} this machine",
    "write_file": "write to {path}",
    "move_path": "move {source} to {destination}",
    "set_volume": "change the volume",
    "empty_recycle_bin": "empty the recycle bin",
    "toggle_wifi": "turn Wi-Fi {state}",
    "run_tests": "run the test suite in {project}",
    "git_commit": "commit with the message '{message}'",
    "zip_path": "create the archive {destination}",
    "clean_temp_files": "delete temporary files",
    "click_text": "click on '{text}'",
    "set_brightness": "change the display brightness",
    "shutdown_routine": "run the end-of-day shutdown routine",
}


def _describe_action(skill_name: str, kwargs: dict[str, Any]) -> str:
    template = _ACTION_VERBS.get(skill_name, skill_name.replace("_", " "))
    try:
        return template.format(**{key: (value if value is not None else "") for key, value in kwargs.items()})
    except (KeyError, IndexError):
        return skill_name.replace("_", " ")


__all__ = ["PARAM_TYPES", "Param", "Skill", "SkillContext", "SkillResult"]