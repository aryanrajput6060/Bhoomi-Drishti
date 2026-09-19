from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

import psutil
import requests
from bs4 import BeautifulSoup

from .database import SessionLocal
from .models import Conversation, Note, Reminder, Task


ALLOWED_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "command prompt": "cmd.exe",
    "paint": "mspaint.exe",
    "explorer": "explorer.exe",
}


def add_conversation(role: str, content: str) -> None:
    db = SessionLocal()
    db.add(Conversation(role=role, content=content))
    db.commit()
    db.close()


def list_directory(path: str) -> Dict[str, Any]:
    root = Path(path).expanduser()
    if not root.exists():
        return {"ok": False, "message": f"Path does not exist: {path}"}
    items = [
        {"name": item.name, "is_dir": item.is_dir(), "path": str(item)}
        for item in sorted(root.iterdir(), key=lambda i: (not i.is_dir(), i.name.lower()))
    ]
    return {"ok": True, "path": str(root), "items": items}


def create_note(title: str, content: str) -> Dict[str, Any]:
    db = SessionLocal()
    db.add(Note(title=title, content=content))
    db.commit()
    db.close()
    return {"ok": True, "title": title, "content": content}


def add_task(title: str, description: str = "") -> Dict[str, Any]:
    db = SessionLocal()
    db.add(Task(title=title, description=description))
    db.commit()
    db.close()
    return {"ok": True, "title": title, "description": description}


def set_reminder(content: str, minutes_from_now: int = 0) -> Dict[str, Any]:
    db = SessionLocal()
    due_at = datetime.utcnow() + timedelta(minutes=minutes_from_now)
    db.add(Reminder(content=content, due_at=due_at))
    db.commit()
    db.close()
    return {"ok": True, "content": content, "due_at": due_at.isoformat()}


def open_application(app_name: str) -> Dict[str, Any]:
    key = app_name.strip().lower()
    if key not in ALLOWED_APPS:
        return {"ok": False, "message": f"Application '{app_name}' is not allowed or not recognized."}

    bin_path = shutil.which(ALLOWED_APPS[key])
    if bin_path is None:
        bin_path = ALLOWED_APPS[key]

    try:
        subprocess.Popen([bin_path], shell=False)
        return {"ok": True, "app": app_name, "path": bin_path}
    except Exception as exc:  # pragma: no cover - OS-specific path failure
        return {"ok": False, "message": f"Failed to launch: {exc}"}


def capture_screen(output_path: str = "screen_capture.png") -> Dict[str, Any]:
    try:
        import pyautogui

        screenshot = pyautogui.screenshot()
        screenshot.save(output_path)
        return {"ok": True, "path": os.path.abspath(output_path), "message": "Screenshot captured successfully."}
    except Exception as exc:  # pragma: no cover - optional dependency
        return {"ok": False, "message": f"Screen capture is unavailable: {exc}"}


def get_system_status() -> Dict[str, Any]:
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        "ok": True,
        "platform": platform.platform(),
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / (1024 ** 3), 2),
        "disk_percent": disk.percent,
        "uptime_seconds": time.time() - psutil.boot_time(),
    }


def web_search(query: str, limit: int = 5) -> Dict[str, Any]:
    url = "https://duckduckgo.com/html/?q=" + requests.utils.quote(query)
    response = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for item in soup.select(".result")[:limit]:
        title = item.select_one(".result__title")
        link = item.select_one("a.result__a")
        snippet = item.select_one(".result__snippet")
        if link and title:
            results.append({
                "title": title.get_text(" ", strip=True),
                "url": link.get("href"),
                "snippet": snippet.get_text(" ", strip=True) if snippet else "",
            })
    return {"ok": True, "query": query, "results": results}


def read_webpage(url: str) -> Dict[str, Any]:
    response = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    text = " ".join(soup.stripped_strings)
    snippet = text[:1800]
    return {"ok": True, "url": url, "summary": snippet}


def list_files(path: str) -> Dict[str, Any]:
    return list_directory(path)


def command_action(command: str) -> Dict[str, Any]:
    if command.strip() == "":
        return {"ok": False, "message": "Command is empty."}
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=20)
        output = result.stdout.strip() or result.stderr.strip() or "Command completed successfully."
        return {"ok": True, "command": command, "output": output[:4000]}
    except Exception as exc:  # pragma: no cover - execution can fail on Windows
        return {"ok": False, "message": str(exc)}
