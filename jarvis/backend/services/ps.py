"""Bridge that runs the PowerShell helper scripts in ``backend/scripts``.

JARVIS talks to the deeper parts of Windows (SAPI speech, screen capture,
Windows.Media.Ocr, UI Automation, Core Audio, WMI, clipboard, Start Menu app
inventory) through small, self-contained PowerShell scripts. Scripts are always
invoked with ``-File`` plus pass-through parameters, which avoids every quoting
and escaping problem of inline ``-Command`` strings.

Windows PowerShell 5.1 (``powershell.exe``) is used deliberately: it ships with
supported Windows builds and exposes the .NET / WinRT types these scripts need.
"""

from __future__ import annotations

import asyncio
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping

from config import IS_WINDOWS, SCRIPTS_DIR

log = logging.getLogger("jarvis.ps")

POWERSHELL: str = "powershell"
BASE_FLAGS: tuple[str, ...] = ("-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass")


class PowerShellError(RuntimeError):
    """Raised when a helper script fails or PowerShell is unavailable."""

    def __init__(self, message: str, *, returncode: int | None = None, stderr: str = "") -> None:
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


def script_path(name: str) -> Path:
    """Resolve a script name to an absolute ``.ps1`` path."""
    candidate = SCRIPTS_DIR / (name if name.endswith(".ps1") else f"{name}.ps1")
    if not candidate.exists():
        raise PowerShellError(f"PowerShell helper not found: {candidate.name}")
    return candidate


def _format_value(value: Any) -> list[str]:
    """Render a Python value as PowerShell CLI arguments."""
    if value is None:
        return []
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [str(value)]
    if isinstance(value, (list, tuple, set)):
        return [",".join(str(item) for item in value)]
    return [str(value)]


def build_args(script: str, params: Mapping[str, Any] | None = None) -> list[str]:
    """Build the full ``powershell`` argument list for a helper script.

    Order matters: host flags, then ``-File <script>``, then the script's own
    parameters.
    """
    args: list[str] = [*BASE_FLAGS, "-File", str(script_path(script))]
    for key, value in (params or {}).items():
        flag = f"-{key}"
        rendered = _format_value(value)
        if not rendered:
            if value is True:  # booleans map to PowerShell switch parameters
                args.append(flag)
            continue
        args.append(flag)
        args.extend(rendered)
    return args


def _decode(raw: bytes | str | None) -> str:
    if raw is None:
        return ""
    if isinstance(raw, bytes):
        for encoding in ("utf-8", "cp1252", "latin-1"):
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")
    return raw


def require_windows() -> None:
    if not IS_WINDOWS:
        raise PowerShellError("This capability requires Windows.")


def run_script_sync(
    script: str,
    params: Mapping[str, Any] | None = None,
    *,
    timeout: float = 60.0,
    check: bool = True,
) -> str:
    """Run a helper script and return stripped stdout."""
    require_windows()
    args = build_args(script, params)
    log.debug("powershell %s", " ".join(args[1:]))
    try:
        proc = subprocess.run(
            [POWERSHELL, *args],
            capture_output=True,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired as exc:  # pragma: no cover - host dependent
        raise PowerShellError(f"{Path(args[0]).name} timed out after {timeout}s") from exc
    except FileNotFoundError as exc:  # pragma: no cover
        raise PowerShellError("powershell.exe is not available on this system") from exc

    stdout = _decode(proc.stdout).strip()
    stderr = _decode(proc.stderr).strip()
    if check and proc.returncode != 0:
        raise PowerShellError(
            f"{Path(args[0]).name} failed (exit {proc.returncode}): {stderr or stdout}",
            returncode=proc.returncode,
            stderr=stderr,
        )
    if stderr:
        log.debug("%s stderr: %s", Path(args[0]).name, stderr)
    return stdout


async def run_script(
    script: str,
    params: Mapping[str, Any] | None = None,
    *,
    timeout: float = 60.0,
    check: bool = True,
) -> str:
    """Async variant of :func:`run_script_sync` (never blocks the event loop)."""
    return await asyncio.to_thread(run_script_sync, script, params, timeout=timeout, check=check)

def parse_json(raw: str, *, default: Any = None) -> Any:
    """Parse JSON emitted by a helper script (tolerates BOM and stray log lines)."""
    text = (raw or "").strip()
    if not text:
        return default
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for line in reversed(text.splitlines()):
            line = line.strip()
            if line.startswith(("{", "[")):
                try:
                    return json.loads(line)
                except json.JSONDecodeError:
                    continue
    log.debug("could not parse JSON from PowerShell output: %.200s", text)
    return default


def run_json_sync(
    script: str,
    params: Mapping[str, Any] | None = None,
    *,
    timeout: float = 60.0,
    check: bool = True,
    default: Any = None,
) -> Any:
    return parse_json(run_script_sync(script, params, timeout=timeout, check=check), default=default)


async def run_json(
    script: str,
    params: Mapping[str, Any] | None = None,
    *,
    timeout: float = 60.0,
    check: bool = True,
    default: Any = None,
) -> Any:
    raw = await run_script(script, params, timeout=timeout, check=check)
    return parse_json(raw, default=default)


def run_code_sync(code: str, *, timeout: float = 60.0, check: bool = True) -> str:
    """Run an ad-hoc PowerShell snippet, written to a temporary script file."""
    require_windows()
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False, encoding="utf-8") as handle:
        handle.write(code)
        temp_path = Path(handle.name)
    try:
        return run_script_sync(str(temp_path), {}, timeout=timeout, check=check)
    finally:
        temp_path.unlink(missing_ok=True)


async def run_code(code: str, *, timeout: float = 60.0, check: bool = True) -> str:
    return await asyncio.to_thread(run_code_sync, code, timeout=timeout, check=check)


def run_code_json(code: str, *, timeout: float = 60.0, check: bool = True, default: Any = None) -> Any:
    return parse_json(run_code_sync(code, timeout=timeout, check=check), default=default)


def as_list(payload: Any, *, key: str = "value") -> list[Any]:
    """Normalise PowerShell JSON output into a plain list.

    ``ConvertTo-Json`` sometimes serialises an array as a PSObject wrapper
    (``{"value": [...], "Count": n}``) when the pipeline only carries one item;
    this flattens both shapes and ``None``.
    """
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        wrapped = payload.get(key)
        if isinstance(wrapped, list):
            return wrapped
        if wrapped is not None:
            return [wrapped]
        return [payload]
    return [payload]


def available_scripts() -> list[str]:
    """Names of the helper scripts shipped with JARVIS."""
    return sorted(path.stem for path in SCRIPTS_DIR.glob("*.ps1"))


def missing_scripts(names: Iterable[str]) -> list[str]:
    wanted = [name if name.endswith(".ps1") else f"{name}.ps1" for name in names]
    return [name for name in wanted if not (SCRIPTS_DIR / name).exists()]


__all__ = [
    "PowerShellError",
    "POWERSHELL",
    "as_list",
    "available_scripts",
    "build_args",
    "missing_scripts",
    "parse_json",
    "require_windows",
    "run_code",
    "run_code_json",
    "run_code_sync",
    "run_json",
    "run_json_sync",
    "run_script",
    "run_script_sync",
    "script_path",
]