"""Core conversational skills that work with no LLM and no network.

Time, date, identity, capability listing and arithmetic — the requests JARVIS
must always be able to answer, even fully offline.
"""

from __future__ import annotations

import ast
import operator
from datetime import datetime
from typing import Any, Callable

from config import settings
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

_WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


@register
class GetTimeSkill(Skill):
    name = "get_time"
    description = "Report the current local time, date and day of the week."
    category = "core"
    examples = ("what time is it", "what's today's date")
    patterns = (
        r"\b(?:what(?:'s| is)? the time|what time is it|tell me the time|current time)\b",
        r"\b(?:what(?:'s| is)? (?:today'?s )?date|what day is (?:it|today)|today'?s date)\b",
        r"\b(?:time and date|date and time)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        now = datetime.now()
        stamp = f"{now.hour % 12 or 12}:{now.minute:02d} {now.strftime('%p')}"
        speech = f"It is {stamp} on {_WEEKDAYS[now.weekday()]}, {now.day} {now.strftime('%B %Y')}."
        return SkillResult.success(
            speech,
            data={
                "iso": now.isoformat(),
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%Y-%m-%d"),
                "day": _WEEKDAYS[now.weekday()],
                "timezone": now.astimezone().tzname() or "",
            },
            display={
                "kind": "clock",
                "time": now.strftime("%H:%M:%S"),
                "date": now.strftime("%d %B %Y"),
                "day": _WEEKDAYS[now.weekday()],
            },
        )


@register
class IdentitySkill(Skill):
    name = "assistant_identity"
    description = "Explain who JARVIS is and how it is currently configured."
    category = "core"
    examples = ("who are you", "introduce yourself")
    patterns = (
        r"\b(?:who are you|what are you|introduce yourself|what is your name|your name)\b",
        r"\b(?:are you (?:an? )?(?:ai|robot|human|real))\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        provider = settings.llm_provider
        model = settings.llm_model or "the configured model"
        if provider in {"none", ""}:
            reasoner = "I am in local mode, so I answer from my built-in skills without an external model."
        elif settings.llm_api_key or provider == "ollama":
            reasoner = f"My reasoning runs on the {provider} provider using {model}."
        else:
            reasoner = "No language-model key is configured, so I am running fully local."
        speech = (
            f"I am {settings.assistant_name}, your desktop assistant. I control this machine, search the web, "
            f"read your screen, manage tasks, notes and reminders, and remember what matters to you. {reasoner}"
        )
        return SkillResult.success(
            speech,
            data={"name": settings.assistant_name, "operator": settings.operator_name,
                  "provider": provider, "model": settings.llm_model},
        )


@register
class CapabilitiesSkill(Skill):
    name = "list_capabilities"
    description = "List everything JARVIS can currently do, grouped by category."
    category = "core"
    examples = ("what can you do", "list your skills")
    patterns = (
        r"^(?:jarvis[,\s]+)?(?:help|help me)\b",
        r"\bwhat can you (?:do|help with)\b",
        r"\b(?:list|show) (?:your |the )?(?:skills|capabilities|commands|features)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        from skills.registry import registry

        skills = registry.all()
        grouped = registry.by_category()
        summary = ", ".join(f"{len(items)} in {name}" for name, items in sorted(grouped.items()))
        speech = (
            f"I have {len(skills)} capabilities online ({summary}). "
            "Ask me to open or close apps, manage files, search the web, read your screen, run approved "
            "commands, handle tasks, notes and reminders, control smart-home devices, run developer "
            "workflows, or report system status."
        )
        return SkillResult.success(
            speech,
            data={"total": len(skills), "categories": {key: [item.name for item in value] for key, value in grouped.items()}},
            display={
                "kind": "capabilities",
                "total": len(skills),
                "groups": [
                    {
                        "category": category,
                        "skills": [
                            {
                                "name": item.name,
                                "description": item.description,
                                "example": item.examples[0] if item.examples else "",
                            }
                            for item in items
                        ],
                    }
                    for category, items in sorted(grouped.items())
                ],
            },
        )

# --- safe arithmetic ------------------------------------------------------- #
_BINARY_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_MAX_POWER = 1000.0


def evaluate_expression(expression: str) -> float:
    """Evaluate a pure arithmetic expression with no names, calls or attributes."""
    return _eval_node(ast.parse(expression, mode="eval"))


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        raise ValueError("only numbers are allowed")
    if isinstance(node, ast.BinOp):
        handler = _BINARY_OPS.get(type(node.op))
        if handler is None:
            raise ValueError("unsupported operator")
        left, right = _eval_node(node.left), _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and (abs(right) > _MAX_POWER or abs(left) > 1e6):
            raise ValueError("exponent too large")
        return handler(left, right)
    if isinstance(node, ast.UnaryOp):
        unary = _UNARY_OPS.get(type(node.op))
        if unary is None:
            raise ValueError("unsupported unary operator")
        return unary(_eval_node(node.operand))
    raise ValueError("unsupported expression")


@register
class CalculateSkill(Skill):
    name = "calculate"
    description = "Evaluate a pure arithmetic expression safely (no code execution)."
    category = "core"
    examples = ("calculate 12 * (4 + 7)", "what is 250 * 0.15")
    params = (Param("expression", "string", "Arithmetic expression, e.g. '12*(4+7)'", required=True),)
    patterns = (
        r"^(?:calculate|compute|what is|what's|how much is)\s+(?P<expression>[-+*/().\d\s^]+?)\s*=?$",
        r"^(?:calculate|compute)\s+(?P<expression>.+)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        raw = str(kwargs.get("expression", "")).strip()
        expression = raw.replace("^", "**")
        if not expression:
            return SkillResult.failure("I need an expression to calculate.", "missing expression")
        try:
            value = evaluate_expression(expression)
        except ZeroDivisionError:
            return SkillResult.failure("That would divide by zero.", "division by zero")
        except Exception as exc:
            return SkillResult.failure(f"I could not evaluate that expression: {exc}", str(exc))

        pretty = int(value) if float(value).is_integer() else round(value, 10)
        return SkillResult.success(
            f"{raw} equals {pretty}.",
            data={"expression": raw, "result": pretty},
            display={"kind": "calculation", "expression": raw, "result": pretty},
        )


__all__ = [
    "CalculateSkill",
    "CapabilitiesSkill",
    "GetTimeSkill",
    "IdentitySkill",
    "evaluate_expression",
]