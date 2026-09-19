"""Safety guardrails: path sandbox, command validation, confirmation handshake.

JARVIS can touch the real machine, so every privileged action passes through
this module:

* **PathGuard** confines file skills to the operator's own folders.
* **CommandGuard** rejects destructive shell commands outright and flags the
  rest for confirmation.
* **ConfirmationStore** implements the ask-then-execute handshake used for
  dangerous actions (delete, shutdown, arbitrary shell commands, closing apps).
"""

from __future__ import annotations

import logging
import os
import re
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from config import settings

log = logging.getLogger("jarvis.safety")


class SafetyError(RuntimeError):
    """Raised when an action violates a guardrail."""


# --------------------------------------------------------------------------- #
# Path sandbox
# --------------------------------------------------------------------------- #
#: Directories that are never writable/deletable through JARVIS, even when they
#: happen to sit inside an allowed root.
PROTECTED_SEGMENTS: tuple[str, ...] = (
    "windows",
    "program files",
    "program files (x86)",
    "programdata",
    "system32",
    "syswow64",
    "appdata\\local\\microsoft",
    "boot",
    "$recycle.bin",
    "system volume information",
    ".ssh",
    ".aws",
    ".git\\config",
)

#: File name fragments that are treated as secrets.
SENSITIVE_NAME_HINTS: tuple[str, ...] = ("id_rsa", "id_ed25519", "credentials", ".env", "shadow", "sam", "ntuser.dat")

WRITE_ACTIONS = {"write", "append", "delete", "move", "copy", "mkdir", "rename", "unzip", "zip"}


class PathGuard:
    """Validates filesystem access against the configured allowed roots."""

    def __init__(self, roots: list[Path] | None = None) -> None:
        self._roots = roots or []

    @property
    def roots(self) -> list[Path]:
        current = settings.allowed_roots
        return current if current else self._roots

    def describe_roots(self) -> list[str]:
        return [str(root) for root in self.roots]

    def resolve(self, raw: str | None, *, action: str = "read", must_exist: bool | None = None) -> Path:
        """Resolve ``raw`` to an absolute path, enforcing the sandbox rules."""
        if not settings.file_ops_enabled:
            raise SafetyError("File operations are disabled in settings.")

        if raw in (None, "", ".", "~"):
            candidate = Path.home()
        else:
            expanded = os.path.expandvars(str(raw).strip().strip('"').strip("'"))
            candidate = Path(expanded).expanduser()
            if not candidate.is_absolute():
                candidate = Path.home() / candidate

        try:
            resolved = candidate.resolve()
        except OSError as exc:
            raise SafetyError(f"Could not resolve path '{raw}': {exc}") from exc

        if not self._is_allowed(resolved):
            roots = ", ".join(self.describe_roots())
            raise SafetyError(
                f"'{resolved}' is outside the folders JARVIS is allowed to use ({roots}). "
                "Add it to JARVIS_EXTRA_ROOTS in .env if that was intended."
            )

        if action in WRITE_ACTIONS and self._is_protected(resolved):
            raise SafetyError(f"'{resolved}' is a protected system location and cannot be modified by JARVIS.")

        if must_exist is True and not resolved.exists():
            raise SafetyError(f"'{resolved}' does not exist.")
        if must_exist is False and resolved.exists():
            raise SafetyError(f"'{resolved}' already exists.")
        return resolved

    def _is_allowed(self, path: Path) -> bool:
        for root in self.roots:
            try:
                if path == root or root in path.parents:
                    return True
            except OSError:  # pragma: no cover
                continue
        return False

    def _is_protected(self, path: Path) -> bool:
        lowered = str(path).lower()
        if any(segment in lowered for segment in PROTECTED_SEGMENTS):
            return True
        return any(hint in path.name.lower() for hint in SENSITIVE_NAME_HINTS)

    def is_sensitive(self, path: Path) -> bool:
        return any(hint in path.name.lower() for hint in SENSITIVE_NAME_HINTS)


path_guard = PathGuard()

# --------------------------------------------------------------------------- #
# Shell command validation
# --------------------------------------------------------------------------- #
class CommandGuard:
    """Allow-lists shell commands and refuses clearly destructive ones."""

    #: Patterns that are never permitted, regardless of the allow-list.
    DENY_PATTERNS: tuple[tuple[str, str], ...] = (
        (r"\bformat\b\s+[a-z]:", "disk formatting"),
        (r"\bdiskpart\b", "raw disk partitioning"),
        (r"\bcipher\b\s*/w", "disk wiping"),
        (r"rm\s+-rf\s+/(\s|$)", "recursive delete of the filesystem root"),
        (r"rm\s+-rf\s+~", "recursive delete of the home directory"),
        (r"\bdel\b.*/[fsq]\b.*[a-z]:\\?\s*$", "recursive delete of a drive"),
        (r"remove-item\s+.*-recurse.*-force.*[a-z]:\\?\s*$", "recursive delete of a drive"),
        (r"\breg\s+delete\b", "registry deletion"),
        (r"\bbcdedit\b", "boot configuration changes"),
        (r"\bvssadmin\b\s+delete", "shadow copy deletion"),
        (r"\bmkfs\b", "filesystem creation"),
        (r"\bdd\b\s+if=.*of=/dev", "raw device writes"),
        (r":\(\)\s*\{.*\};\s*:", "fork bomb"),
        (r"\bnet\s+user\b.*/add", "account creation"),
        (r"\btakeown\b.*/f", "ownership takeover"),
        (r"\bicacls\b.*/grant\s+everyone", "permission widening"),
        (r"\bshutdown\b(?!\s*/a)", "direct shutdown/restart"),
        (r"(rm|del|erase)\b\s+.*\bc:\\windows", "deleting Windows system files"),
        (r"\bchoco\b\s+uninstall\s+all", "mass package removal"),
    )

    #: Read-only / informational commands that run without an explicit entry in
    #: JARVIS_SHELL_ALLOWLIST.
    SAFE_PREFIXES: tuple[str, ...] = (
        "echo", "dir", "ls", "pwd", "cd", "whoami", "hostname", "date", "time", "ver",
        "ipconfig", "systeminfo", "tasklist", "where", "which", "get-date", "get-childitem",
        "get-process", "get-service", "get-computerinfo", "get-ciminstance", "type",
        "cat", "findstr", "ping", "tracert", "netstat", "route", "nslookup", "curl",
        "git status", "git log", "git diff", "git branch", "git remote",
        "python --version", "node --version", "npm --version", "pip list", "pip show",
        "nvidia-smi", "wmic",
    )

    def __init__(self) -> None:
        self._deny = [(re.compile(pattern, re.IGNORECASE), label) for pattern, label in self.DENY_PATTERNS]

    @property
    def allowlist(self) -> list[str]:
        return [item.lower() for item in settings.shell_allowlist]

    def evaluate(self, command: str) -> dict[str, Any]:
        """Return ``{allowed, reason, needs_confirmation, kind}`` for a command."""
        text = (command or "").strip()
        if not text:
            return {"allowed": False, "reason": "Empty command.", "needs_confirmation": False, "kind": "invalid"}
        if not settings.shell_enabled:
            return {
                "allowed": False,
                "reason": "Shell access is disabled in settings.",
                "needs_confirmation": False,
                "kind": "disabled",
            }

        for pattern, label in self._deny:
            if pattern.search(text):
                return {
                    "allowed": False,
                    "reason": f"Refused: this command matches a blocked pattern ({label}).",
                    "needs_confirmation": False,
                    "kind": "denied",
                }

        lowered = text.lower()
        for prefix in self.allowlist:
            if lowered.startswith(prefix):
                return {
                    "allowed": True,
                    "reason": f"Allowed by JARVIS_SHELL_ALLOWLIST ('{prefix}').",
                    "needs_confirmation": False,
                    "kind": "allowlisted",
                }

        for prefix in self.SAFE_PREFIXES:
            if lowered.startswith(prefix):
                return {
                    "allowed": True,
                    "reason": "Read-only/informational command.",
                    "needs_confirmation": False,
                    "kind": "safe",
                }

        return {
            "allowed": True,
            "reason": "Not on the safe list — operator confirmation required.",
            "needs_confirmation": bool(settings.confirm_dangerous),
            "kind": "confirm",
        }


command_guard = CommandGuard()

# --------------------------------------------------------------------------- #
# Confirmation handshake
# --------------------------------------------------------------------------- #
@dataclass(slots=True)
class PendingAction:
    """A dangerous action parked until the operator approves it."""

    token: str
    skill: str
    args: dict[str, Any]
    prompt: str
    created_at: float = field(default_factory=time.time)
    ttl: float = 180.0
    conversation_id: int | None = None

    @property
    def expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl

    def as_dict(self) -> dict[str, Any]:
        return {
            "token": self.token,
            "skill": self.skill,
            "args": self.args,
            "prompt": self.prompt,
            "expires_in": max(0.0, round(self.ttl - (time.time() - self.created_at), 1)),
        }


class ConfirmationStore:
    """In-memory store of actions awaiting a yes/no from the operator."""

    def __init__(self, max_pending: int = 32) -> None:
        self._pending: dict[str, PendingAction] = {}
        self._max_pending = max_pending

    def create(
        self,
        skill: str,
        args: dict[str, Any],
        prompt: str,
        conversation_id: int | None = None,
    ) -> PendingAction:
        self.prune()
        if len(self._pending) >= self._max_pending:
            oldest = min(self._pending.values(), key=lambda item: item.created_at)
            self._pending.pop(oldest.token, None)
        action = PendingAction(
            token=secrets.token_urlsafe(12),
            skill=skill,
            args=dict(args or {}),
            prompt=prompt,
            conversation_id=conversation_id,
        )
        self._pending[action.token] = action
        log.info("confirmation requested for %s (token %s)", skill, action.token)
        return action

    def get(self, token: str) -> PendingAction | None:
        action = self._pending.get(token)
        if action is None:
            return None
        if action.expired:
            self._pending.pop(token, None)
            return None
        return action

    def consume(self, token: str) -> PendingAction | None:
        action = self.get(token)
        if action is not None:
            self._pending.pop(token, None)
        return action

    def latest(self) -> PendingAction | None:
        self.prune()
        if not self._pending:
            return None
        return max(self._pending.values(), key=lambda item: item.created_at)

    def prune(self) -> None:
        for token in [token for token, action in self._pending.items() if action.expired]:
            self._pending.pop(token, None)

    @property
    def pending_count(self) -> int:
        self.prune()
        return len(self._pending)


confirmations = ConfirmationStore()


def summarise_roots() -> str:
    return ", ".join(path_guard.describe_roots())


__all__ = [
    "CommandGuard",
    "ConfirmationStore",
    "PathGuard",
    "PendingAction",
    "SafetyError",
    "command_guard",
    "confirmations",
    "path_guard",
    "summarise_roots",
]