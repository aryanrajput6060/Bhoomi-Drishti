"""Application control: launch, close, focus and list running applications.

Resolution order for a spoken app name:

1. built-in alias table (fast, offline, covers the usual suspects),
2. an explicit file path,
3. ``PATH`` lookup with ``.exe``,
4. the Windows Start Menu inventory (Win32 shortcuts *and* Store/UWP apps),
5. a URL when the request looks like one.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import time
import webbrowser
from pathlib import Path
from typing import Any

from config import DATA_DIR, IS_WINDOWS
from services import ps
from services import windows as win
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.apps")

START_APPS_CACHE = DATA_DIR / "start_apps.json"
START_APPS_TTL = 24 * 3600  # seconds

#: Common application aliases (spoken name -> executable / URI / shell path).
APP_ALIASES: dict[str, str] = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",
    "wordpad": "write.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
    "powershell": "powershell.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "files": "explorer.exe",
    "task manager": "taskmgr.exe",
    "resource monitor": "resmon.exe",
    "registry editor": "regedit.exe",
    "system information": "msinfo32.exe",
    "snipping tool": "explorer.exe shell:AppsFolder\\Microsoft.ScreenSketch_8wekyb3d8bbwe!App",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "firefox": "firefox.exe",
    "brave": "brave.exe",
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "code": "code",
    "visual studio": "devenv.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "outlook": "outlook.exe",
    "onedrive": "onedrive.exe",
    "teams": "ms-teams.exe",
    "microsoft teams": "ms-teams.exe",
    "spotify": "spotify.exe",
    "vlc": "vlc.exe",
    "discord": "discord.exe",
    "slack": "slack.exe",
    "steam": "steam.exe",
    "zoom": "zoom.exe",
    "obs": "obs64.exe",
    "obs studio": "obs64.exe",
    "notepad++": "notepad++.exe",
    "7zip": "7zFM.exe",
    "7-zip": "7zFM.exe",
    "git bash": "git-bash.exe",
    "postman": "postman.exe",
    "figma": "figma.exe",
    "whatsapp": "whatsapp:",
    "telegram": "telegram.exe",
    "settings": "ms-settings:",
    "windows settings": "ms-settings:",
    "control panel": "control.exe",
    "device manager": "devmgmt.msc",
    "services": "services.msc",
    "disk management": "diskmgmt.msc",
    "event viewer": "eventvwr.msc",
    "store": "ms-windows-store:",
    "microsoft store": "ms-windows-store:",
    "photos": "ms-photos:",
    "camera": "microsoft.windows.camera:",
    "mail": "outlookmail:",
    "calendar": "outlookcal:",
    "downloads": "shell:Downloads",
    "documents": "shell:Personal",
    "pictures": "shell:MyPictures",
    "desktop": "shell:Desktop",
    "recycle bin": "shell:RecycleBinFolder",
    "this pc": "shell:MyComputerFolder",
    "wifi settings": "ms-settings:network-wifi",
    "bluetooth settings": "ms-settings:bluetooth",
    "display settings": "ms-settings:display",
    "sound settings": "ms-settings:sound",
    "power settings": "ms-settings:powersleep",
    "update settings": "ms-settings:windowsupdate",
    "apps settings": "ms-settings:appsfeatures",
    "privacy settings": "ms-settings:privacy",
}

_URI_PATTERN = re.compile(r"^[a-z][a-z0-9+.\-]*:[^\\/]*$", re.IGNORECASE)
_URL_PATTERN = re.compile(r"^(?:https?://|www\.)\S+$", re.IGNORECASE)


def start_apps_index(*, refresh: bool = False) -> list[dict[str, Any]]:
    """Start Menu inventory, cached on disk for a day."""
    if not IS_WINDOWS:
        return []
    if not refresh and START_APPS_CACHE.exists():
        age = time.time() - START_APPS_CACHE.stat().st_mtime
        if age < START_APPS_TTL:
            try:
                cached = json.loads(START_APPS_CACHE.read_text(encoding="utf-8"))
                if isinstance(cached, list) and cached:
                    return cached
            except (OSError, json.JSONDecodeError):
                log.debug("start menu cache unreadable; rebuilding")
    try:
        payload = ps.as_list(ps.run_json_sync("start_apps.ps1", {}, timeout=120, default=[]))
        entries = [
            {"name": str(item.get("name", "")), "appId": str(item.get("appId", "")), "kind": str(item.get("kind", ""))}
            for item in payload
            if item.get("name")
        ]
        START_APPS_CACHE.write_text(json.dumps(entries, indent=1), encoding="utf-8")
        return entries
    except Exception as exc:
        log.warning("could not enumerate Start Menu apps: %s", exc)
        return []

def resolve_app(name: str) -> dict[str, Any]:
    """Work out how to launch ``name``. Returns ``{kind, target, label}``."""
    raw = (name or "").strip().strip('"').strip("'")
    if not raw:
        return {"kind": "unknown", "target": "", "label": name}

    lowered = raw.lower()
    # Normalise filler words: "open the chrome app" -> "chrome"
    normalized = re.sub(r"^(?:the|my|a)\s+", "", lowered)
    normalized = re.sub(r"\s+(?:app|application|program|window)$", "", normalized)

    for key in (lowered, normalized):
        if key in APP_ALIASES:
            return {"kind": "alias", "target": APP_ALIASES[key], "label": key}

    if _URL_PATTERN.match(raw):
        return {"kind": "url", "target": raw, "label": raw}
    if lowered.startswith("shell:"):
        return {"kind": "shell", "target": raw, "label": normalized}

    candidate = Path(os.path.expandvars(raw))
    if candidate.exists():
        return {"kind": "path", "target": str(candidate), "label": candidate.name}

    for probe in (raw, f"{raw}.exe"):
        found = shutil.which(probe)
        if found:
            return {"kind": "exe", "target": found, "label": Path(found).stem}

    entries = start_apps_index()
    if entries:
        wanted = normalized
        scored: list[tuple[int, dict[str, Any]]] = []
        for entry in entries:
            app_name = entry["name"].lower()
            if app_name == wanted:
                scored.append((0, entry))
            elif app_name.startswith(wanted):
                scored.append((1, entry))
            elif wanted in app_name:
                scored.append((2, entry))
        if scored:
            scored.sort(key=lambda item: (item[0], len(item[1]["name"])))
            best = scored[0][1]
            kind = "startapp" if best.get("kind") == "startapp" else "shortcut"
            return {"kind": kind, "target": best["appId"], "label": best["name"]}

    if _URI_PATTERN.match(raw):
        return {"kind": "uri", "target": raw, "label": normalized}
    return {"kind": "unknown", "target": "", "label": raw}


def launch_resolved(resolution: dict[str, Any]) -> None:
    """Start an application described by :func:`resolve_app`."""
    kind, target = resolution.get("kind"), resolution.get("target", "")
    if not target:
        raise FileNotFoundError("Nothing to launch")

    if kind in {"alias", "exe", "path"}:
        target_path = target
        if kind == "alias":
            if target.startswith("shell:"):
                subprocess.Popen(["explorer.exe", target], close_fds=True)
                return
            if _URI_PATTERN.match(target):
                os.startfile(target)  # type: ignore[attr-defined]
                return
            resolved = shutil.which(target) or target
            if resolved.lower().endswith((".msc", ".cpl")):
                subprocess.Popen([resolved], close_fds=True)
                return
            target_path = resolved
        if Path(target_path).suffix.lower() in {".lnk", ".url"}:
            os.startfile(target_path)  # type: ignore[attr-defined]
            return
        if not Path(target_path).exists():
            resolved = shutil.which(target_path)
            if not resolved:
                raise FileNotFoundError(f"'{target_path}' was not found on this system")
            target_path = resolved
        subprocess.Popen(
            [target_path],
            close_fds=True,
            creationflags=getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
        )
        return

    if kind == "shell":
        subprocess.Popen(["explorer.exe", target], close_fds=True)
        return
    if kind == "shortcut":
        os.startfile(target)  # type: ignore[attr-defined]
        return
    if kind == "startapp":
        subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{target}"], close_fds=True)
        return
    if kind in {"uri", "url"}:
        if kind == "url" and not target.lower().startswith(("http://", "https://")):
            target = f"https://{target}"
        webbrowser.open(target)
        return
    raise FileNotFoundError(f"Could not work out how to launch '{resolution.get('label')}'")


def close_app_processes(name: str, *, force: bool = False) -> dict[str, Any]:
    """Close windows (or whole processes) matching ``name``."""
    needle = re.sub(r"\s+(?:app|application|program|window)$", "", (name or "").strip().lower())
    targets = win.find_windows(needle)
    if not targets:
        return {"closed": [], "remaining": [], "found": False}

    closed: list[str] = []
    for window in targets:
        try:
            win.close_window(window.hwnd, force=force)
            closed.append(window.title)
        except Exception as exc:
            log.warning("could not close %s: %s", window.title, exc)

    if force:
        try:
            import psutil

            for process in psutil.process_iter(["name", "pid"]):
                process_name = (process.info.get("name") or "").lower()
                if needle and needle in process_name:
                    process.terminate()
                    closed.append(f"{process_name} (pid {process.info.get('pid')})")
        except Exception as exc:
            log.warning("force close failed: %s", exc)

    time.sleep(0.8)
    remaining = [window.title for window in win.find_windows(needle)]
    return {"closed": closed, "remaining": remaining, "found": True}

@register
class OpenAppSkill(Skill):
    name = "open_app"
    description = "Open an application, folder, settings page or website on this computer."
    category = "apps"
    examples = ("open notepad", "launch chrome", "open my downloads folder")
    params = (
        Param("name", "string", "Application, folder, settings page or URL to open", required=True),
        Param("arguments", "string", "Optional command-line arguments"),
    )
    patterns = (
        r"^(?:please\s+)?(?:open|launch|start|fire up|bring up)\s+(?:up\s+)?(?P<name>[a-z0-9][^,]{1,60}?)(?:\s+with\s+(?P<arguments>.+))?$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        name = str(kwargs.get("name", "")).strip()
        if not name:
            return SkillResult.failure("Which application should I open?", "missing name")
        # Keep the router from swallowing other requests ("open a new note").
        if re.match(r"^(?:a|the|my)\s+(?:new\s+)?(?:note|task|reminder|list|file|folder in)\b", name.lower()):
            if not re.match(r"^(?:a|the|my)?\s*(?:file explorer|terminal|folder)\b", name.lower()):
                return SkillResult.skip("That looks like a different command.", data={"name": name})

        resolution = resolve_app(name)
        if resolution["kind"] == "unknown":
            return SkillResult.failure(
                f"I could not find an application called '{name}' on this machine.",
                f"unresolved app: {name}",
            )
        try:
            await asyncio.to_thread(launch_resolved, resolution)
        except Exception as exc:
            log.error("failed to launch %s: %s", name, exc)
            return SkillResult.failure(f"I could not open {resolution['label']}: {exc}", str(exc))

        return SkillResult.success(
            f"Opening {resolution['label']}.",
            data={"requested": name, **resolution},
            display={"kind": "app", "action": "opened", "name": resolution["label"], "method": resolution["kind"]},
        )


@register
class CloseAppSkill(Skill):
    name = "close_app"
    description = "Close a running application or window by name."
    category = "apps"
    dangerous = True
    requires_confirmation = True
    examples = ("close notepad", "close chrome")
    params = (
        Param("name", "string", "Application or window title to close", required=True),
        Param("force", "boolean", "Terminate the process instead of asking it to close", default=False),
    )
    patterns = (
        r"^(?:please\s+)?(?:close|quit|exit|kill|terminate)\s+(?P<name>[a-z0-9][^,]{1,50}?)(?:\s+forcefully)?$",
    )
    confirm_template = "Shall I close {name}? Any unsaved work in it would be lost."

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        name = str(kwargs.get("name", "")).strip()
        force = bool(kwargs.get("force", False))
        if not name:
            return SkillResult.failure("Which application should I close?", "missing name")

        targets = await asyncio.to_thread(win.find_windows, name)
        if not targets:
            return SkillResult.failure(f"I could not find a running window called '{name}'.", "no matching window")

        outcome = await asyncio.to_thread(close_app_processes, name, force=force)
        if outcome["remaining"]:
            return SkillResult.success(
                f"I asked {name} to close, but {len(outcome['remaining'])} window(s) are still open — "
                "it may be waiting for you to save your work.",
                data=outcome,
                display={"kind": "app", "action": "close-pending", "name": name, "remaining": outcome["remaining"]},
            )
        return SkillResult.success(
            f"Closed {name}.",
            data=outcome,
            display={"kind": "app", "action": "closed", "name": name, "closed": outcome["closed"]},
        )

@register
class ListWindowsSkill(Skill):
    name = "list_windows"
    description = "List the applications and windows currently open on this computer."
    category = "apps"
    examples = ("what's open right now", "list my windows")
    patterns = (
        r"\b(?:what(?:'s| is) (?:open|running)|list (?:my |the )?(?:open )?(?:apps|applications|windows|programs))\b",
        r"\b(?:running apps|open windows|open apps)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        windows = await asyncio.to_thread(win.enumerate_windows)
        seen: dict[str, dict[str, Any]] = {}
        for window in windows:
            key = window.process or window.title
            if key not in seen:
                seen[key] = {
                    "process": window.process,
                    "title": window.title,
                    "pid": window.pid,
                    "foreground": window.foreground,
                    "windows": 1,
                }
            else:
                seen[key]["windows"] += 1
        entries = sorted(seen.values(), key=lambda item: (item["process"] or "").lower())
        names = [item["process"] or item["title"] for item in entries[:12]]
        speech = (
            f"There are {len(entries)} applications open: {', '.join(names)}."
            if entries
            else "No application windows are open at the moment."
        )
        return SkillResult.success(
            speech,
            data={"count": len(entries), "windows": entries},
            display={"kind": "windows", "count": len(entries), "items": entries},
        )


@register
class FocusWindowSkill(Skill):
    name = "focus_window"
    description = "Bring an open window to the front, or show the desktop."
    category = "apps"
    examples = ("switch to chrome", "show the desktop")
    params = (Param("name", "string", "Window title or process to focus (omit to show the desktop)"),)
    patterns = (
        r"^(?:please\s+)?(?:switch to|focus on|focus|bring up|activate|go to)\s+(?P<name>[a-z0-9][^,]{1,50})$",
        r"^(?:show|reveal) (?:me )?(?:the )?desktop$",
        r"^minimi[sz]e all(?: windows)?$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        name = str(kwargs.get("name", "") or "").strip()
        if not name or name.lower() in {"desktop", "the desktop"}:
            await asyncio.to_thread(win.minimize_all)
            return SkillResult.success("Showing the desktop.", display={"kind": "windows", "action": "desktop"})

        matches = await asyncio.to_thread(win.find_windows, name)
        if not matches:
            return SkillResult.failure(f"No open window matches '{name}'.", "no matching window")
        target = matches[0]
        focused = await asyncio.to_thread(win.focus_window, target.hwnd)
        if not focused:
            return SkillResult.failure(f"Windows would not let me switch to '{target.title}'.", "focus refused")
        return SkillResult.success(
            f"Switched to {target.title}.",
            data=target.as_dict(),
            display={"kind": "windows", "action": "focused", "title": target.title, "process": target.process},
        )


__all__ = [
    "APP_ALIASES",
    "CloseAppSkill",
    "FocusWindowSkill",
    "ListWindowsSkill",
    "OpenAppSkill",
    "close_app_processes",
    "launch_resolved",
    "resolve_app",
    "start_apps_index",
]