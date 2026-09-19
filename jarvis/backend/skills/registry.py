"""Skill registry: auto-discovery, lookup and LLM tool schemas.

New capabilities are added by dropping a module into ``backend/skills`` and
decorating the class with :func:`register` — nothing else needs to change:

    @register
    class OpenAppSkill(Skill):
        name = "open_app"
        ...
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from typing import Any, Iterable, Iterator

from skills.base import Skill, SkillContext, SkillResult

log = logging.getLogger("jarvis.skills")

#: Modules that provide framework plumbing rather than concrete skills.
_INTERNAL_MODULES = {"base", "registry"}


class SkillRegistry:
    """Holds every registered skill and answers brain/API queries."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._loaded = False

    # -- registration ----------------------------------------------------- #
    def register(self, instance: Skill) -> Skill:
        if not instance.name:
            raise ValueError(f"{type(instance).__name__} must define a skill name")
        if instance.name in self._skills:
            log.warning("skill '%s' registered twice — the newer definition wins", instance.name)
        self._skills[instance.name] = instance
        return instance

    def get(self, name: str) -> Skill | None:
        self.discover()
        return self._skills.get(name)

    def names(self) -> list[str]:
        self.discover()
        return sorted(self._skills)

    def all(self) -> list[Skill]:
        self.discover()
        return [self._skills[name] for name in sorted(self._skills)]

    def by_category(self) -> dict[str, list[Skill]]:
        grouped: dict[str, list[Skill]] = {}
        for skill in self.all():
            grouped.setdefault(skill.category, []).append(skill)
        return grouped

    def __len__(self) -> int:
        return len(self._skills)

    def __iter__(self) -> Iterator[Skill]:
        return iter(self.all())

    # -- discovery -------------------------------------------------------- #
    def discover(self, force: bool = False) -> None:
        """Import every module in the ``skills`` package exactly once."""
        if self._loaded and not force:
            return
        self._loaded = True
        package = importlib.import_module("skills")
        for module_info in pkgutil.iter_modules(package.__path__):
            if module_info.name.startswith("_") or module_info.name in _INTERNAL_MODULES:
                continue
            try:
                importlib.import_module(f"skills.{module_info.name}")
            except Exception as exc:  # a broken skill must not kill JARVIS
                log.error("could not load skill module '%s': %s", module_info.name, exc, exc_info=True)
        log.info("skill registry ready: %d capabilities", len(self._skills))

    # -- brain helpers ---------------------------------------------------- #
    def tool_schemas(self) -> list[dict[str, Any]]:
        """Tool definitions for LLM function calling."""
        return [skill.tool_schema() for skill in self.all()]

    def route(self, text: str, *, exclude: Iterable[str] = ()) -> tuple[Skill, dict[str, Any]] | None:
        """Match raw user text against declared skill patterns (offline router).

        Skills are consulted in registry order (sorted by name) but patterns are
        written to be specific, and the router prefers the match with the most
        captured, non-empty groups so the richest interpretation wins.
        """
        blocked = set(exclude)
        best: tuple[Skill, dict[str, Any], int] | None = None
        for skill in self.all():
            if skill.name in blocked:
                continue
            found = skill.match(text)
            if not found:
                continue
            captured = {
                key: value.strip()
                for key, value in found.groupdict().items()
                if isinstance(value, str) and value.strip()
            }
            score = len(captured)
            if best is None or score > best[2]:
                best = (skill, captured, score)
        if best is None:
            return None
        return best[0], best[1]

    def route_all(self, text: str, *, exclude: Iterable[str] = ()) -> list[tuple[Skill, dict[str, Any]]]:
        """Every skill whose pattern matches, best (most captured groups) first.

        The brain walks this list so that a skill which decides a request belongs
        to someone else (``SkillResult.skip``) does not block the correct one.
        """
        blocked = set(exclude)
        matches: list[tuple[Skill, dict[str, Any], int]] = []
        for skill in self.all():
            if skill.name in blocked:
                continue
            found = skill.match(text)
            if not found:
                continue
            captured = {
                key: value.strip()
                for key, value in found.groupdict().items()
                if isinstance(value, str) and value.strip()
            }
            matches.append((skill, captured, len(captured)))
        matches.sort(key=lambda item: (-item[2], item[0].name))
        return [(skill, captured) for skill, captured, _score in matches]

    def describe_for_prompt(self, *, max_per_skill: int = 2) -> str:
        """Compact catalogue of capabilities, used in the offline help reply."""
        lines: list[str] = []
        for category, skills in sorted(self.by_category().items()):
            lines.append(f"{category.upper()}")
            for skill in skills:
                example = f" — e.g. \"{skill.examples[0]}\"" if skill.examples[:max_per_skill] else ""
                lines.append(f"  • {skill.name}: {skill.description}{example}")
        return "\n".join(lines)


registry = SkillRegistry()


def register(instance: Skill) -> Skill:
    """Register a skill *instance* (used by the ``@register`` decorator)."""
    return registry.register(instance)


def skill(cls: type[Skill]) -> type[Skill]:
    """Class decorator: instantiate and register a skill."""

    register(cls())
    return cls


__all__ = ["SkillRegistry", "register", "registry", "skill"]