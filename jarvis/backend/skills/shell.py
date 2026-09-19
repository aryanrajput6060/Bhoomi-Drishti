"""Approved shell command execution.

JARVIS will run commands, but only through a real safety gate
(:mod:`services.safety`): destructive patterns are refused outright, read-only
commands run directly, and everything else needs explicit operator confirmation.
"""

from __future__ import annotations

import asyncio
import logging
import re
import subprocess
from typing import Any

from config import settings
from services.safety import command_guard
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.shell")

#: Commands are children of JARVIS, so cwd defaults to the operator's home.
DEFAULT_SHELL = "powershell"


def run_command_sync(command: str, *, cwd: str | None = None, timeout: int | None = None,
                     shell: str = DEFAULT_SHELL) -> dict[str, Any]:
    """Execute a command and capture its output (never raises on failure)."""
    timeout = timeout or settings.shell_timeout
    executable = ["powershell", "-NoProfile", "-NonInteractive", "-Command", command] if shell == "powershell" \
        else ["cmd.exe", "/c", command]
    try:
        completed = subprocess.run(
            executable,
            capture_output=True,
            timeout=timeout,
            cwd=cwd or None,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"Command timed out after {timeout}s", "command": command,
                "stdout": "", "stderr": "", "returncode": None}
    except FileNotFoundError as exc:
        return {"ok": False, "error": str(exc), "command": command, "stdout": "", "stderr": "", "returncode": None}

    return {
        "ok": completed.returncode == 0,
        "command": command,
        "returncode": completed.returncode,
        "stdout": (completed.stdout or "").strip()[:20000],
        "stderr": (completed.stderr or "").strip()[:8000],
        "error": "" if completed.returncode == 0 else f"Exit code {completed.returncode}",
    }


@register
class RunCommandSkill(Skill):
    name = "run_command"
    description = "Run a shell command on this machine through the safety gate (read-only commands run directly, everything else asks first)."
    category = "automation"
    dangerous = True
    requires_confirmation = True
    works_offline = True
    examples = ("run git status", "run ipconfig")
    params = (
        Param("command", "string", "Command to execute", required=True),
        Param("cwd", "string", "Working directory for the command"),
        Param("shell", "string", "powershell | cmd", enum=["powershell", "cmd"], default="powershell"),
    )
    patterns = (
        r"^(?:please\s+)?(?:run|execute|exec)\s+(?:the\s+)?(?:command\s+)?(?P<command>.+)$",
        r"^(?:in )?(?:powershell|terminal|cmd)[,:]?\s+run\s+(?P<command>.+)$",
    )
    confirm_template = "Shall I run the command '{command}'?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        command = str(kwargs.get("command") or "").strip()
        if not command:
            return SkillResult.failure("Which command should I run?", "missing command")
        # Requests like "run the tests" belong to the developer workflow skills.
        if re.fullmatch(r"(?:the\s+)?(?:my\s+)?(?:unit\s+|integration\s+)?tests?(?:\s+suite)?", command, re.IGNORECASE):
            return SkillResult.skip("That is a test-run request.", data={"command": command})

        verdict = command_guard.evaluate(command)
        if not verdict["allowed"]:
            return SkillResult.failure(verdict["reason"], verdict["kind"])
        if verdict["needs_confirmation"] and not ctx.confirmed and settings.confirm_dangerous:
            # The brain turns this into a confirmation request; the operator's
            # approval replays the call with ctx.confirmed set.
            return SkillResult.confirm(
                f"Shall I run this command? `{command}`\n({verdict['reason']})",
                command=command,
                cwd=kwargs.get("cwd"),
                shell=str(kwargs.get("shell") or DEFAULT_SHELL),
            )

        result = await asyncio.to_thread(
            run_command_sync,
            command,
            cwd=kwargs.get("cwd"),
            shell=str(kwargs.get("shell") or DEFAULT_SHELL),
        )
        output = result["stdout"] or result["stderr"] or "(no output)"
        if not result["ok"]:
            return SkillResult.failure(
                f"The command failed with exit code {result['returncode']}: {output[:600]}",
                result["error"] or "command failed",
            )
        return SkillResult.success(
            f"Command finished successfully. Output: {output[:800]}",
            data=result,
            display={"kind": "command", "command": command, "output": output[:6000],
                     "returncode": result["returncode"], "verified": verdict["kind"]},
        )


__all__ = ["RunCommandSkill", "run_command_sync"]