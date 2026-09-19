"""Machine control: volume, brightness, power, Wi-Fi, clipboard, wallpaper, input.

These skills change real hardware and OS state, so anything destructive or hard
to undo is marked ``requires_confirmation`` and goes through the ask-then-execute
handshake before it runs.
"""

from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from typing import Any

from services import ps
from services import windows as win
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.system")


def _clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(value)))


@register
class SetVolumeSkill(Skill):
    name = "set_volume"
    description = "Read or change the system master volume, and mute or unmute the speakers."
    category = "system"
    examples = ("volume up", "set volume to 30", "mute")
    params = (
        Param("level", "integer", "Absolute volume percentage (0-100)"),
        Param("delta", "integer", "Relative change in percent, e.g. -10"),
        Param("mute", "boolean", "True to mute, False to unmute"),
    )
    patterns = (
        r"\b(?:turn (?:the )?volume|volume) (?:up|higher|increase)(?:\s+by\s+(?P<delta>\d+))?\b",
        r"\b(?:turn (?:the )?volume|volume) (?:down|lower|decrease)(?:\s+by\s+(?P<delta>\d+))?\b",
        r"\b(?:set|change) (?:the )?volume to (?P<level>\d{1,3})\b",
        r"\bvolume (?:to )?(?P<level>\d{1,3})(?:\s*%)?\b",
        r"\b(?:mute|silence)(?: the (?:sound|volume|speakers|audio))?\b",
        r"\b(?:unmute|unsilence)(?: the (?:sound|volume|speakers|audio))?\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        text = (ctx.raw_text or "").lower()
        payload: dict[str, Any] = {"Json": True}

        if kwargs.get("level") is not None:
            payload["Level"] = _clamp(kwargs["level"])
        elif kwargs.get("delta") is not None:
            direction = -1 if any(word in text for word in ("down", "lower", "decrease")) else 1
            payload["Delta"] = direction * abs(int(kwargs["delta"]))
        elif any(word in text for word in ("up", "higher", "increase")):
            payload["Delta"] = 10
        elif any(word in text for word in ("down", "lower", "decrease")):
            payload["Delta"] = -10

        asks_mute = bool(re.search(r"\bmute\b", text))
        asks_unmute = bool(re.search(r"\bunmute|unsilence\b", text))
        if asks_mute and not asks_unmute:
            payload["Mute"] = True
        if asks_unmute:
            payload["Unmute"] = True
        if kwargs.get("mute") is not None:
            payload["Mute" if kwargs["mute"] else "Unmute"] = True

        try:
            result = await ps.run_json("volume.ps1", payload, timeout=90, default={}) or {}
        except Exception as exc:
            return SkillResult.failure(f"I could not change the volume: {exc}", str(exc))

        level, muted = result.get("level"), result.get("muted")
        if muted:
            speech = f"Volume is muted (set to {level} percent)."
        elif asks_unmute:
            speech = f"Unmuted — volume is at {level} percent."
        elif "Level" in payload or "Delta" in payload:
            speech = f"Volume is now {level} percent."
        else:
            speech = f"Volume is at {level} percent." + (" Speakers are muted." if muted else "")
        return SkillResult.success(speech, data=result, display={"kind": "volume", "level": level, "muted": muted})

@register
class SetBrightnessSkill(Skill):
    name = "set_brightness"
    description = "Read or change the display brightness (laptop panels expose this)."
    category = "system"
    examples = ("set brightness to 70", "dim the screen", "brightness")
    params = (Param("level", "integer", "Brightness percentage (0-100)"),)
    patterns = (
        r"\b(?:set|change) (?:the )?(?:screen |display |monitor )?brightness to (?P<level>\d{1,3})\b",
        r"\b(?:dim|darken) (?:the )?(?:screen|display|brightness)\b",
        r"\b(?:brighten|increase) (?:the )?(?:screen|display|brightness)\b",
        r"\bbrightness(?: level| setting)?\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        lowered = (ctx.raw_text or "").lower()
        payload: dict[str, Any] = {"Json": True}
        if kwargs.get("level") is not None:
            payload["Level"] = _clamp(kwargs["level"])
        elif "dim" in lowered or "darken" in lowered:
            payload["Level"] = 25
        elif "brighten" in lowered:
            payload["Level"] = 90

        try:
            result = await ps.run_json("brightness.ps1", payload, timeout=90, default={}) or {}
        except Exception as exc:
            return SkillResult.failure(f"I could not read the brightness: {exc}", str(exc))

        if not result.get("supported"):
            return SkillResult.failure(
                result.get("message") or "This display does not support brightness control.",
                "brightness unsupported",
            )
        level = result.get("level")
        if "Level" in payload:
            return SkillResult.success(f"Brightness set to {level} percent.", data=result,
                                       display={"kind": "brightness", "level": level})
        return SkillResult.success(f"Brightness is at {level} percent.", data=result,
                                   display={"kind": "brightness", "level": level})


_CLIPBOARD_WRITE = (
    r"^(?:copy|put)\s+(?P<text>.+?)\s+(?:to|into|on) (?:my |the )?clipboard$",
    r"^copy this\s*[:,-]?\s*(?P<text>.+)$",
    r"^(?:set|write) (?:the )?clipboard to\s+(?P<text>.+)$",
)


@register
class ClipboardSkill(Skill):
    name = "clipboard"
    description = "Read the clipboard, or put text on it."
    category = "system"
    examples = ("what's in my clipboard", "copy hello world to my clipboard")
    params = (
        Param("action", "string", "read | write", enum=["read", "write"], default="read"),
        Param("text", "string", "Text to place on the clipboard"),
    )
    patterns = (
        r"\b(?:what(?:'s| is) (?:in|on) (?:my |the )?clipboard|read (?:my |the )?clipboard|paste clipboard)\b",
        *_CLIPBOARD_WRITE,
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        text = kwargs.get("text")
        if not text:
            for pattern in _CLIPBOARD_WRITE:
                found = re.search(pattern, ctx.raw_text or "", re.IGNORECASE | re.MULTILINE)
                if found:
                    text = found.group("text").strip()
                    break

        if kwargs.get("action") == "write" or text:
            if not text:
                return SkillResult.failure("What should I copy to the clipboard?", "missing text")
            try:
                await asyncio.to_thread(win.set_clipboard_text, str(text))
            except Exception as exc:
                return SkillResult.failure(f"I could not write to the clipboard: {exc}", str(exc))
            preview = str(text)[:120]
            return SkillResult.success(
                f"Copied to the clipboard: {preview}",
                data={"characters": len(str(text)), "text": str(text)},
                display={"kind": "clipboard", "action": "write", "preview": preview},
            )

        try:
            content = await asyncio.to_thread(win.clipboard_text)
        except Exception as exc:
            return SkillResult.failure(f"I could not read the clipboard: {exc}", str(exc))
        if not content.strip():
            return SkillResult.success("The clipboard is empty.", data={"length": 0},
                                       display={"kind": "clipboard", "action": "read", "preview": ""})
        return SkillResult.success(
            f"The clipboard holds {len(content)} characters. {content[:400]}",
            data={"length": len(content), "text": content},
            display={"kind": "clipboard", "action": "read", "preview": content[:400]},
        )

_POWER_WORDS = {
    "lock": "lock",
    "sleep": "sleep",
    "suspend": "sleep",
    "hibernate": "hibernate",
    "restart": "restart",
    "reboot": "restart",
    "shutdown": "shutdown",
    "shut down": "shutdown",
    "power off": "shutdown",
    "turn off": "shutdown",
    "cancel": "cancel",
}


@register
class PowerActionSkill(Skill):
    name = "power_action"
    description = "Lock, sleep, hibernate, restart or shut down this computer."
    category = "system"
    dangerous = True
    requires_confirmation = True
    examples = ("lock the computer", "shut down the pc", "cancel shutdown")
    params = (
        Param("action", "string", "lock | sleep | hibernate | restart | shutdown | cancel",
              required=True, enum=["lock", "sleep", "hibernate", "restart", "shutdown", "cancel"]),
        Param("delay_seconds", "integer", "Grace period before a restart/shutdown", default=15),
    )
    patterns = (
        r"\b(?P<action>lock) (?:the )?(?:computer|pc|screen|machine|workstation)\b",
        r"\b(?P<action>sleep|suspend) (?:the )?(?:computer|pc|machine)\b",
        r"\b(?P<action>hibernate) (?:the )?(?:computer|pc|machine)?\b",
        r"\b(?P<action>restart|reboot) (?:the )?(?:computer|pc|machine|system)\b",
        r"\b(?P<action>shut ?down|power off|turn off) (?:the )?(?:computer|pc|machine|system)\b",
        r"\bcancel (?:the )?(?P<action>shutdown|restart)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        raw_action = str(kwargs.get("action") or "").lower()
        action = _POWER_WORDS.get(raw_action, raw_action)

        if action == "cancel":
            try:
                await ps.run_script("power.ps1", {"Action": "cancel"}, timeout=60)
            except Exception as exc:
                return SkillResult.failure(f"I could not cancel the pending shutdown: {exc}", str(exc))
            return SkillResult.success("Cancelled the pending shutdown.", display={"kind": "power", "action": "cancel"})

        if action not in {"lock", "sleep", "hibernate", "restart", "shutdown"}:
            return SkillResult.failure("Which power action should I perform?", "unknown power action")

        delay = int(kwargs.get("delay_seconds") or 15)
        try:
            await ps.run_script("power.ps1", {"Action": action, "DelaySeconds": delay}, timeout=60)
        except Exception as exc:
            return SkillResult.failure(f"I could not {action} the machine: {exc}", str(exc))

        messages = {
            "lock": "Locking the workstation.",
            "sleep": "Putting the machine to sleep.",
            "hibernate": "Hibernating the machine.",
            "restart": f"Restarting in {delay} seconds. Say 'cancel shutdown' to abort.",
            "shutdown": f"Shutting down in {delay} seconds. Say 'cancel shutdown' to abort.",
        }
        return SkillResult.success(
            messages[action],
            data={"action": action, "delay_seconds": delay},
            display={"kind": "power", "action": action, "delay_seconds": delay},
        )


@register
class ToggleWifiSkill(Skill):
    name = "toggle_wifi"
    description = "Turn the Wi-Fi adapter on or off (changing it requires Administrator rights)."
    category = "system"
    dangerous = True
    requires_confirmation = True
    examples = ("turn off wifi", "turn on wifi")
    params = (Param("state", "string", "on | off | status", enum=["on", "off", "status"], default="status"),)
    patterns = (
        r"\bturn (?P<state>on|off) (?:the )?(?:wi-?fi|wireless|wlan)\b",
        r"\b(?:enable|disable) (?:the )?(?:wi-?fi|wireless)\b",
        r"\bwi-?fi (?:status|state)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        text = (ctx.raw_text or "").lower()
        state = kwargs.get("state")
        if state not in {"on", "off", "status"}:
            if re.search(r"\b(?:turn on|enable)\b", text):
                state = "on"
            elif re.search(r"\b(?:turn off|disable)\b", text):
                state = "off"
            else:
                state = "status"

        try:
            result = await ps.run_json("wifi.ps1", {"Action": state}, timeout=120, default={}) or {}
        except Exception as exc:
            return SkillResult.failure(f"I could not reach the Wi-Fi adapter: {exc}", str(exc))

        if state == "status":
            if result.get("ssid"):
                return SkillResult.success(f"Connected to '{result['ssid']}' at {result.get('signal')} percent signal.",
                                           data=result, display={"kind": "wifi", **result})
            return SkillResult.success(f"Wi-Fi is {result.get('status', 'unknown')}.", data=result,
                                       display={"kind": "wifi", **result})

        if result.get("message"):
            return SkillResult.failure(result["message"], "wifi change refused")
        if not result.get("ok"):
            return SkillResult.success(
                f"I sent the command to turn Wi-Fi {state}, but the adapter still reports "
                f"{result.get('status')}. Administrator rights are likely required.",
                data=result,
                display={"kind": "wifi", **result},
            )
        return SkillResult.success(f"Wi-Fi is now {state}.", data=result, display={"kind": "wifi", **result})

@register
class EmptyRecycleBinSkill(Skill):
    name = "empty_recycle_bin"
    description = "Permanently delete everything in the recycle bin."
    category = "system"
    dangerous = True
    requires_confirmation = True
    examples = ("empty the recycle bin",)
    patterns = (r"\bempty (?:the )?(?:recycle|recycling) bin\b", r"\bclear (?:the )?(?:recycle|recycling) bin\b")
    confirm_template = "Shall I empty the recycle bin? This cannot be undone."

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        try:
            output = await ps.run_code("Clear-RecycleBin -Force -ErrorAction Stop; 'cleared'", timeout=180, check=False)
        except Exception as exc:
            return SkillResult.failure(f"I could not empty the recycle bin: {exc}", str(exc))
        if "cleared" not in (output or ""):
            detail = output.strip()
            return SkillResult.failure(
                "Windows refused to empty the recycle bin" + (f": {detail}" if detail else "."),
                "recycle bin refusal",
            )
        return SkillResult.success("The recycle bin is now empty.",
                                   display={"kind": "system", "action": "recycle-bin"})


@register
class SetWallpaperSkill(Skill):
    name = "set_wallpaper"
    description = "Change the desktop wallpaper to an image file."
    category = "system"
    examples = ("change my wallpaper to C:/Users/me/Pictures/pic.jpg",)
    params = (Param("path", "string", "Image file to use as wallpaper", required=True),)
    patterns = (r"\b(?:set|change) (?:my |the )?wallpaper to (?P<path>.+)$",)

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        from services.safety import SafetyError, path_guard

        try:
            target = path_guard.resolve(kwargs.get("path"), action="read", must_exist=True)
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        if target.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}:
            return SkillResult.failure("That file is not an image I can use as wallpaper.", "bad image type")
        try:
            await asyncio.to_thread(win.set_wallpaper, str(target))
        except Exception as exc:
            return SkillResult.failure(f"I could not change the wallpaper: {exc}", str(exc))
        return SkillResult.success(f"Wallpaper set to {target.name}.", data={"path": str(target)},
                                   display={"kind": "wallpaper", "path": str(target)})


@register
class TypeTextSkill(Skill):
    name = "type_text"
    description = "Type text into the focused window, or press a key combination."
    category = "system"
    dangerous = True
    requires_confirmation = True
    examples = ("type hello world", "press ctrl+s")
    params = (
        Param("text", "string", "Text to type"),
        Param("keys", "string", "Key combination, e.g. ctrl+shift+s"),
    )
    patterns = (
        r"^(?:please\s+)?type\s+(?P<text>.+)$",
        r"^(?:please\s+)?press\s+(?P<keys>[a-z0-9+\s]{2,30})$",
    )
    confirm_template = "Shall I send that input to the focused window?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        text, keys = kwargs.get("text"), kwargs.get("keys")
        try:
            if keys:
                await asyncio.to_thread(win.press_keys, str(keys))
                return SkillResult.success(f"Pressed {keys}.", display={"kind": "input", "keys": keys})
            if text:
                count = await asyncio.to_thread(win.type_text, str(text))
                return SkillResult.success(f"Typed {count} characters.", data={"characters": count},
                                           display={"kind": "input", "typed": str(text)[:120]})
        except Exception as exc:
            return SkillResult.failure(f"I could not send that input: {exc}", str(exc))
        return SkillResult.failure("What should I type, or which keys should I press?", "missing input")


__all__ = [
    "ClipboardSkill",
    "EmptyRecycleBinSkill",
    "PowerActionSkill",
    "SetBrightnessSkill",
    "SetVolumeSkill",
    "SetWallpaperSkill",
    "ToggleWifiSkill",
    "TypeTextSkill",
]