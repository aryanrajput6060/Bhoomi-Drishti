"""Screen reading and computer vision.

Three independent capabilities, all real:

* **screenshot** — capture the desktop to a PNG (PowerShell + System.Drawing).
* **read the screen** — OCR through the built-in Windows OCR engine
  (``Windows.Media.Ocr``), with UI Automation as a precise fallback that returns
  the exact accessibility strings of the focused window.
* **vision** — when a vision-capable LLM is configured, the screenshot is sent to
  it for a description; otherwise JARVIS says plainly that vision is unavailable
  rather than inventing an answer.

Because OCR returns per-word bounding boxes, JARVIS can also *locate* text on
screen and click it.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import SCREENSHOT_DIR
from services import ps
from services import windows as win
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.screen")


def capture_screen(*, monitor: int = 0, path: Path | None = None, label: str = "screen") -> dict[str, Any]:
    """Save a screenshot to disk and return its metadata."""
    target = path or SCREENSHOT_DIR / f"{label}_{datetime.now():%Y%m%d_%H%M%S}.png"
    payload = ps.run_json_sync("screenshot.ps1", {"Path": str(target), "Monitor": int(monitor)}, timeout=90, default={})
    if not payload or not payload.get("path"):
        raise RuntimeError("The screenshot helper produced no image")
    return payload


def ocr_image(path: str | Path, *, language: str = "") -> dict[str, Any]:
    """Run the Windows OCR engine over an image file."""
    payload = ps.run_json_sync("ocr.ps1", {"Path": str(path), "Language": language}, timeout=180, default={})
    if not payload:
        raise RuntimeError("Windows OCR returned no result")
    return payload


def read_focused_window_text(*, title_like: str = "", max_elements: int = 400) -> dict[str, Any]:
    """Read on-screen text through UI Automation (exact strings, no OCR errors)."""
    payload = ps.run_json_sync(
        "ui_text.ps1", {"TitleLike": title_like, "MaxElements": int(max_elements)}, timeout=180, default={}
    )
    if payload is None:
        raise RuntimeError("UI Automation is unavailable")
    return payload


def find_text_on_screen(needle: str, *, language: str = "") -> dict[str, Any]:
    """Locate a word on screen via OCR and return its centre point."""
    shot = capture_screen(label="ocr_lookup")
    result = ocr_image(shot["path"], language=language)
    wanted = needle.strip().lower()
    for line in result.get("lines") or []:
        for word in line.get("words") or []:
            if word["text"].strip().lower().strip(".,:;") == wanted or wanted in word["text"].strip().lower():
                return {
                    "found": True,
                    "text": word["text"],
                    "x": int(word["x"] + word["w"] / 2),
                    "y": int(word["y"] + word["h"] / 2),
                    "screenshot": shot["path"],
                    "line": line.get("text", ""),
                }
    return {"found": False, "text": needle, "screenshot": shot["path"], "line": ""}

@register
class ScreenshotSkill(Skill):
    name = "take_screenshot"
    description = "Capture the screen and save it as an image file."
    category = "screen"
    examples = ("take a screenshot", "screenshot the second monitor")
    params = (
        Param("monitor", "integer", "0 = all displays, 1 = primary, 2+ = display index", default=1),
        Param("open_after", "boolean", "Open the image after capturing", default=False),
    )
    patterns = (
        r"\b(?:take|capture|grab)(?: a| an| the)? ?(?:screen ?)?(?:shot|screenshot|screen capture|screen grab)\b",
        r"\bscreenshot(?: of)?(?: the)? (?P<monitor>primary|second|all|main)?(?: monitor| screen)?\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        monitor = int(kwargs.get("monitor") or 1)
        text = (ctx.raw_text or "").lower()
        if "all" in text:
            monitor = 0
        elif "second" in text:
            monitor = 2
        try:
            payload = await asyncio.to_thread(capture_screen, monitor=monitor)
        except Exception as exc:
            return SkillResult.failure(f"I could not capture the screen: {exc}", str(exc))

        if kwargs.get("open_after"):
            try:
                import os

                os.startfile(payload["path"])  # type: ignore[attr-defined]
            except Exception as exc:
                log.debug("could not open screenshot: %s", exc)

        return SkillResult.success(
            f"Screenshot saved as {Path(payload['path']).name} ({payload['width']}x{payload['height']}).",
            data=payload,
            display={"kind": "screenshot", **payload},
        )

@register
class ReadScreenSkill(Skill):
    name = "read_screen"
    description = ("Read the text currently visible on screen (Windows OCR, or UI Automation for a specific window), "
                   "and describe the screen with a vision model when one is configured.")
    category = "screen"
    examples = ("what's on my screen", "read the screen", "read this window", "describe my screen")
    params = (
        Param("mode", "string", "auto | ocr | window | vision", enum=["auto", "ocr", "window", "vision"], default="auto"),
        Param("window", "string", "Window title to read through UI Automation"),
        Param("question", "string", "Question to ask about the screen when vision is available"),
    )
    patterns = (
        r"\b(?:what(?:'s| is) on my screen|read (?:my|the) screen|read the screen|what does my screen say|"
        r"describe my screen|describe the screen|read what(?:'s| is) on screen)\b",
        r"\bread (?:this|the current|the active) window(?: text)?\b",
        r"\b(?:read|extract) (?:the )?text (?:from|on) (?:my|the) screen\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        text = (ctx.raw_text or "").lower()
        mode = str(kwargs.get("mode") or "auto")
        window_title = str(kwargs.get("window") or "")
        if "vision" in text or "describe" in text:
            mode = "vision"
        elif "window" in text:
            mode = "window"

        if mode == "vision":
            return await _describe_with_vision(kwargs.get("question") or "Describe what is on my screen.")

        if mode == "window" or window_title:
            try:
                payload = await asyncio.to_thread(read_focused_window_text, title_like=window_title)
            except Exception as exc:
                return SkillResult.failure(f"I could not read that window: {exc}", str(exc))
            lines = [
                (element.get("value") or element.get("name") or "").strip()
                for element in payload.get("elements", [])
            ]
            body = "\n".join(line for line in lines if line)
            windows = [item.get("title") for item in payload.get("windows", [])]
            if not body:
                return SkillResult.failure("That window exposed no readable text.", "no text")
            return SkillResult.success(
                f"Reading {windows[0] if windows else 'the window'}: {body[:900]}",
                data={"mode": "uia", "windows": windows, "text": body, "elements": payload.get("elements", [])},
                display={"kind": "screen-text", "mode": "uia", "windows": windows, "text": body[:6000]},
            )

        try:
            shot = await asyncio.to_thread(capture_screen, label="read")
            result = await asyncio.to_thread(ocr_image, shot["path"], language=kwargs.get("language") or "")
        except Exception as exc:
            return SkillResult.failure(f"I could not read the screen: {exc}", str(exc))

        body = (result.get("text") or "").strip()
        if not body:
            return SkillResult.failure("I captured the screen but found no readable text.", "no text recognised")
        words = sum(len(line.get("words") or []) for line in result.get("lines") or [])
        return SkillResult.success(
            f"I read {words} words from your screen. {body[:900]}",
            data={"mode": "ocr", "text": body, "screenshot": shot["path"],
                  "language": result.get("language", ""), "lines": result.get("lines", [])},
            display={"kind": "screen-text", "mode": "ocr", "text": body[:6000],
                     "screenshot": shot["path"], "language": result.get("language", "")},
        )


async def _describe_with_vision(question: str) -> SkillResult:
    """Send a screenshot to the configured vision model."""
    try:
        from brain.llm import llm
    except Exception as exc:  # pragma: no cover
        return SkillResult.failure(f"Vision is unavailable: {exc}", str(exc))

    if not llm.vision_available:
        return SkillResult.failure(
            "I cannot look at the screen yet — no vision-capable model is configured. Set JARVIS_VISION_MODEL "
            "(and an API key) in .env, or ask me to read the screen with OCR instead.",
            "vision not configured",
        )
    try:
        shot = await asyncio.to_thread(capture_screen, label="vision")
        description = await llm.describe_image(shot["path"], question)
    except Exception as exc:
        return SkillResult.failure(f"The vision request failed: {exc}", str(exc))

    return SkillResult.success(
        description,
        data={"mode": "vision", "screenshot": shot["path"], "question": question},
        display={"kind": "screen-vision", "text": description, "screenshot": shot["path"], "question": question},
    )

@register
class ClickTextSkill(Skill):
    name = "click_text"
    description = "Find text on screen with OCR and click it."
    category = "screen"
    dangerous = True
    requires_confirmation = True
    examples = ("click on Submit", "click the Sign in button")
    params = (
        Param("text", "string", "Visible text to click", required=True),
        Param("double", "boolean", "Double-click instead of single click", default=False),
    )
    patterns = (
        r"^(?:please\s+)?click(?: on)?\s+(?:the\s+)?(?:button\s+)?[\"']?(?P<text>[^\"']{1,40})[\"']?(?:\s+button)?$",
    )
    confirm_template = "Shall I click '{text}' on screen?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        needle = str(kwargs.get("text") or "").strip().strip("\"'")
        if not needle:
            return SkillResult.failure("What should I click?", "missing text")
        try:
            located = await asyncio.to_thread(find_text_on_screen, needle)
        except Exception as exc:
            return SkillResult.failure(f"I could not search the screen: {exc}", str(exc))
        if not located.get("found"):
            return SkillResult.failure(f"I could not find '{needle}' anywhere on screen.", "text not found")
        try:
            await asyncio.to_thread(win.mouse_click, located["x"], located["y"], double=bool(kwargs.get("double")))
        except Exception as exc:
            return SkillResult.failure(f"I found '{needle}' but could not click it: {exc}", str(exc))
        return SkillResult.success(
            f"Clicked '{located['text']}' at {located['x']}, {located['y']}.",
            data=located,
            display={"kind": "screen-click", **located},
        )


__all__ = [
    "ClickTextSkill",
    "ReadScreenSkill",
    "ScreenshotSkill",
    "capture_screen",
    "find_text_on_screen",
    "ocr_image",
    "read_focused_window_text",
]