"""Media playback control and Now-Playing information.

Uses the Windows ``GlobalSystemMediaTransportControlsSession`` API (the same one
behind the volume flyout) so JARVIS can report the actual track and control
whatever app is playing — Spotify, a browser tab, Groove, VLC — with hardware
media keys as a fallback.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from services import ps
from services import windows as win
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.media")


async def media_session(action: str = "info") -> dict[str, Any]:
    """Query or control the current media session."""
    try:
        payload = await ps.run_json("media.ps1", {"Action": action}, timeout=90, default={})
        return payload or {}
    except Exception as exc:
        log.debug("media session query failed: %s", exc)
        return {"ok": False, "message": str(exc)}


@register
class NowPlayingSkill(Skill):
    name = "now_playing"
    description = "Report what media is currently playing."
    category = "media"
    examples = ("what's playing", "what song is this")
    patterns = (
        r"\bwhat(?:'s| is) (?:playing|this song|the song|currently playing)\b",
        r"\b(?:now playing|current (?:song|track|media))\b",
        r"\bwhat song is (?:this|playing)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        info = await media_session("info")
        if not info.get("ok"):
            return SkillResult.success(
                info.get("message") or "Nothing is playing right now.",
                data=info,
                display={"kind": "media", "playing": False},
            )
        title = info.get("title") or "unknown title"
        artist = info.get("artist") or "unknown artist"
        state = "playing" if info.get("playing") else "paused"
        return SkillResult.success(
            f"{title} by {artist} is {state}.",
            data=info,
            display={"kind": "media", **info},
        )


@register
class MediaControlSkill(Skill):
    name = "media_control"
    description = "Play, pause, stop, skip tracks or adjust media playback."
    category = "media"
    examples = ("pause the music", "next track", "play music")
    params = (
        Param("action", "string", "play | pause | toggle | next | previous | stop",
              required=True, enum=["play", "pause", "toggle", "next", "previous", "stop"]),
    )
    patterns = (
        r"\b(?P<action>pause|resume|play|stop) (?:the )?(?:music|song|track|video|playback|media)\b",
        r"\b(?P<action>next|previous|skip) (?:the )?(?:track|song)\b",
        r"^(?:play|pause|resume)(?: music)?$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        action = str(kwargs.get("action") or "toggle").lower()
        text = (ctx.raw_text or "").lower()
        if action == "resume":
            action = "play"

        # "skip" alone means next; "skip back" means previous.
        if action in {"next", "previous"} and "back" in text:
            action = "previous"

        result = await media_session(action)
        if result.get("ok"):
            verb = {
                "play": "Playing",
                "pause": "Paused",
                "toggle": "Toggled playback",
                "next": "Skipped to the next track",
                "previous": "Went back a track",
                "stop": "Stopped",
            }[action if action != "resume" else "play"]
            title = result.get("title")
            suffix = f": {title} by {result.get('artist')}" if action in {"next", "previous", "play"} and title else ""
            return SkillResult.success(f"{verb}{suffix}.", data=result, display={"kind": "media", **result})

        # Fallback: plain hardware media keys always work.
        try:
            await asyncio.to_thread(win.media_key, "next" if action == "next" else
                                    "previous" if action == "previous" else "play_pause")
        except Exception as exc:
            return SkillResult.failure(f"I could not control playback: {exc}", str(exc))
        return SkillResult.success(
            f"Sent the {action} key.",
            data={"fallback": True, "action": action},
            display={"kind": "media", "action": action, "fallback": True},
        )


__all__ = ["MediaControlSkill", "NowPlayingSkill", "media_session"]