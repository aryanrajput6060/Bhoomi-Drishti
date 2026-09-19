"""JARVIS skills package.

Importing this package exposes the framework pieces; concrete capabilities live
in sibling modules and register themselves automatically via ``@register``.
"""

from __future__ import annotations

from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import SkillRegistry, register, registry, skill


def get_registry() -> SkillRegistry:
    """Return the shared registry, discovering skill modules on first use."""
    registry.discover()
    return registry


__all__ = [
    "Param",
    "Skill",
    "SkillContext",
    "SkillRegistry",
    "SkillResult",
    "get_registry",
    "register",
    "registry",
    "skill",
]