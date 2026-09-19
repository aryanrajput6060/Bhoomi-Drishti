from __future__ import annotations

import re
from typing import Any, Dict, List

from .tools import (
    add_conversation,
    add_task,
    command_action,
    create_note,
    list_directory,
    open_application,
    set_reminder,
    web_search,
)


class JarvisBrain:
    """Intent parser and execution orchestrator for the JARVIS assistant."""

    def handle_request(self, user_input: str) -> Dict[str, Any]:
        text = (user_input or "").strip()
        if not text:
            return {"intent": "none", "response": "I did not receive a request."}

        add_conversation("user", text)

        lower = text.lower()

        if re.search(r"\b(open|launch|start)\b.*\b(notepad|calculator|paint|command prompt|explorer)\b", lower):
            app = re.search(r"\b(notepad|calculator|paint|command prompt|explorer)\b", lower).group(1) if False else None
            app_name = self._extract_application(lower)
            result = open_application(app_name)
            response = f"Opening {app_name}." if result.get("ok") else result.get("message", "I couldn't open that application.")
            return {"intent": "open_application", "target": app_name, "response": response, "tool_result": result}

        if re.search(r"\b(remind|reminder)\b", lower):
            content = re.sub(r"\b(remind me|reminder to|remind)\b", "", lower, flags=re.IGNORECASE).strip()
            if not content:
                content = text
            minutes = self._extract_minutes(lower)
            result = set_reminder(content, minutes)
            return {"intent": "set_reminder", "content": content, "minutes": minutes, "response": f"Reminder set for {minutes} minutes from now.", "tool_result": result}

        if re.search(r"\b(note|notes|write|take a note|remember)\b", lower):
            content = self._extract_note_content(text)
            title = "Quick Note"
            result = create_note(title, content)
            return {"intent": "create_note", "content": content, "title": title, "response": "I saved your note.", "tool_result": result}

        if re.search(r"\b(task|todo|to-do|plan)\b", lower):
            title = self._extract_task_title(text)
            result = add_task(title)
            return {"intent": "create_task", "title": title, "response": f"Task added: {title}", "tool_result": result}

        if re.search(r"\b(list|show|view)\s+(files|folder|directory)\b", lower):
            path = self._extract_path(text) or "."
            result = list_directory(path)
            return {"intent": "list_files", "path": path, "response": "Here are the files and folders I found.", "tool_result": result}

        if re.search(r"\b(search|find|look up)\b", lower):
            query = re.sub(r"\b(search|find|look up|for)\b", "", lower, flags=re.IGNORECASE).strip()
            result = web_search(query or text)
            return {"intent": "web_search", "query": query or text, "response": "I found a few likely matches online.", "tool_result": result}

        if re.search(r"\b(run|execute|open command prompt|terminal)\b", lower):
            command = self._extract_command(text)
            result = command_action(command)
            return {"intent": "run_command", "command": command, "response": result.get("output", "Command completed."), "tool_result": result}

        if re.search(r"\b(status|system|cpu|memory|performance)\b", lower):
            from .tools import get_system_status

            result = get_system_status()
            return {"intent": "system_status", "response": f"CPU usage is {result['cpu_percent']}% and memory usage is {result['memory_percent']}%.", "tool_result": result}

        default = "I can help with notes, reminders, searches, files, commands, and app launches."
        return {"intent": "chat", "response": default}

    @staticmethod
    def _extract_application(text: str) -> str:
        for candidate in ["notepad", "calculator", "paint", "command prompt", "explorer"]:
            if candidate in text:
                return candidate
        return "notepad"

    @staticmethod
    def _extract_minutes(text: str) -> int:
        match = re.search(r"(\d+)\s*(minute|min|minutes|mins)", text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 15

    @staticmethod
    def _extract_note_content(text: str) -> str:
        match = re.search(r"(?:note|notes|write|remember)\s*[:\-]?\s*(.*)", text, flags=re.IGNORECASE)
        if match and match.group(1).strip():
            return match.group(1).strip()
        return text

    @staticmethod
    def _extract_task_title(text: str) -> str:
        task = re.sub(r"\b(task|todo|to-do|plan)\b", "", text, flags=re.IGNORECASE)
        return task.strip() or "New Task"

    @staticmethod
    def _extract_command(text: str) -> str:
        match = re.search(r"(?:run|execute)\s+(.*)", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "dir"

    @staticmethod
    def _extract_path(text: str) -> str:
        match = re.search(r"(?:in|at|path)\s+([A-Za-z]:\\[^\n]+|\.[A-Za-z0-9_./\\-]+|~/[A-Za-z0-9_./\\-]+)", text)
        if match:
            return match.group(1)
        return None
