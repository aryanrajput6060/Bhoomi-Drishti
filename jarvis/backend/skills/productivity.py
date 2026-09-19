"""Productivity skills: tasks, reminders, timers and notes.

All state lives in SQLite through SQLAlchemy, so to-dos and notes survive
restarts. Reminders are handed to :mod:`services.scheduler`, which speaks them
when they come due.
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from typing import Any

from db import session_scope
from models import Note, Task
from services.scheduler import scheduler
from services.timeparse import humanize_when, parse_repeat, parse_when
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.productivity")

PRIORITY_WORDS = {
    "urgent": 1, "critical": 1, "high": 1, "important": 1, "asap": 1,
    "normal": 2, "medium": 2, "low": 3, "someday": 3, "whenever": 3,
}
PRIORITY_LABELS = {1: "high", 2: "normal", 3: "low"}


def create_task(title: str, *, notes: str = "", priority: int = 2, project: str = "",
                due_at: datetime | None = None) -> dict[str, Any]:
    with session_scope() as session:
        task = Task(title=title.strip(), notes=notes, priority=int(priority), project=project, due_at=due_at)
        session.add(task)
        session.flush()
        return task.as_dict()


def list_tasks(*, status: str = "open", limit: int = 100, project: str = "") -> list[dict[str, Any]]:
    with session_scope() as session:
        query = session.query(Task)
        if status in {"open", "done"}:
            query = query.filter(Task.status == status)
        if project:
            query = query.filter(Task.project == project)
        tasks = query.order_by(Task.priority, Task.due_at.is_(None), Task.due_at, Task.id).limit(limit).all()
        return [task.as_dict() for task in tasks]


def complete_task(reference: str) -> dict[str, Any] | None:
    """Mark a task done by id or title fragment."""
    with session_scope() as session:
        task = _find_task(session, reference)
        if task is None:
            return None
        task.status = "done"
        task.completed_at = datetime.now()
        return task.as_dict()


def delete_task(reference: str) -> bool:
    with session_scope() as session:
        task = _find_task(session, reference)
        if task is None:
            return False
        session.delete(task)
        return True


def _find_task(session: Any, reference: str) -> Task | None:
    raw = str(reference or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        return session.get(Task, int(raw))
    pattern = f"%{raw}%"
    return (
        session.query(Task)
        .filter(Task.title.ilike(pattern), Task.status == "open")
        .order_by(Task.priority, Task.id)
        .first()
    )


def create_note(title: str, content: str, *, tags: str = "", pinned: bool = False) -> dict[str, Any]:
    with session_scope() as session:
        note = Note(title=(title or "Untitled note").strip()[:200], content=content or "", tags=tags, pinned=pinned)
        session.add(note)
        session.flush()
        return note.as_dict()


def list_notes(*, limit: int = 100, query: str = "") -> list[dict[str, Any]]:
    with session_scope() as session:
        statement = session.query(Note)
        if query:
            pattern = f"%{query}%"
            statement = statement.filter(Note.title.ilike(pattern) | Note.content.ilike(pattern) | Note.tags.ilike(pattern))
        notes = statement.order_by(Note.pinned.desc(), Note.updated_at.desc()).limit(limit).all()
        return [note.as_dict() for note in notes]


def read_note(reference: str) -> dict[str, Any] | None:
    with session_scope() as session:
        note = _find_note(session, reference)
        return note.as_dict() if note else None


def update_note(reference: str, *, content: str | None = None, title: str | None = None,
                tags: str | None = None, pinned: bool | None = None) -> dict[str, Any] | None:
    with session_scope() as session:
        note = _find_note(session, reference)
        if note is None:
            return None
        if content is not None:
            note.content = content
        if title is not None:
            note.title = title[:200]
        if tags is not None:
            note.tags = tags
        if pinned is not None:
            note.pinned = bool(pinned)
        session.flush()
        return note.as_dict()


def delete_note(reference: str) -> bool:
    with session_scope() as session:
        note = _find_note(session, reference)
        if note is None:
            return False
        session.delete(note)
        return True


def _find_note(session: Any, reference: str) -> Note | None:
    raw = str(reference or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        return session.get(Note, int(raw))
    return session.query(Note).filter(Note.title.ilike(f"%{raw}%")).order_by(Note.updated_at.desc()).first()


def task_summary() -> dict[str, Any]:
    with session_scope() as session:
        open_tasks = session.query(Task).filter(Task.status == "open").all()
        overdue = [
            task.as_dict()
            for task in open_tasks
            if task.due_at is not None and task.due_at < datetime.now()
        ]
        high = [task.as_dict() for task in open_tasks if task.priority == 1]
    return {"open": len(open_tasks), "overdue": overdue, "high_priority": high}

@register
class AddTaskSkill(Skill):
    name = "add_task"
    description = "Add a task to the to-do list, optionally with a due date and priority."
    category = "productivity"
    examples = ("add a task to review the report", "add high priority task call the bank tomorrow")
    params = (
        Param("title", "string", "What the task is", required=True),
        Param("priority", "integer", "1 high, 2 normal, 3 low", default=2),
        Param("project", "string", "Project the task belongs to"),
        Param("due", "string", "Natural-language due date such as 'tomorrow at 5pm'"),
    )
    patterns = (
        r"^(?:please\s+)?(?:add|create|new)(?:\s+(?P<priority_word>urgent|high|critical|important|normal|medium|low))?"
        r"\s+(?:task|to-?do)\s*(?:to\s+|:)?\s*(?P<title>.+)$",
        r"^(?:remind me to|i need to)\s+(?P<title>.+?)(?:\s+by\s+(?P<due>.+))?$",
        r"^(?:add|put)\s+(?P<title>.+?)\s+(?:to|on) (?:my |the )?(?:task list|to-?do list)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        title = str(kwargs.get("title") or "").strip().strip(".!")
        if not title:
            return SkillResult.failure("What is the task?", "missing title")
        if re.fullmatch(r"(?:the )?(?:tests?|test suite)", title, re.IGNORECASE):
            return SkillResult.skip("That is a test-run request.", data={"title": title})

        lowered = ctx.raw_text.lower()
        priority = int(kwargs.get("priority") or 2)
        for word, value in PRIORITY_WORDS.items():
            if word in lowered:
                priority = value
                break
        if kwargs.get("priority_word"):
            priority = PRIORITY_WORDS.get(str(kwargs["priority_word"]).lower(), priority)

        due_text = str(kwargs.get("due") or "")
        due_at = parse_when(due_text) if due_text else parse_when(ctx.raw_text)
        task = await asyncio.to_thread(
            create_task, title, priority=priority, project=str(kwargs.get("project") or ""), due_at=due_at
        )
        when = f", due {humanize_when(due_at)}" if due_at else ""
        return SkillResult.success(
            f"Task added: {title} — {PRIORITY_LABELS.get(priority, 'normal')} priority{when}.",
            data=task,
            display={"kind": "task", "action": "created", "task": task},
        )


@register
class ListTasksSkill(Skill):
    name = "list_tasks"
    description = "List open tasks, or everything that has been completed."
    category = "productivity"
    examples = ("what's on my to-do list", "show completed tasks")
    params = (
        Param("status", "string", "open | done | all", enum=["open", "done", "all"], default="open"),
        Param("limit", "integer", "Maximum tasks to show", default=10),
    )
    patterns = (
        r"\b(?:what(?:'s| is) (?:on )?my (?:to-?do|task) list|list (?:my )?(?:tasks|to-?dos)|show (?:my )?tasks|"
        r"what are my tasks)\b",
        r"\b(?:open|pending|outstanding) tasks\b",
        r"\b(?:completed|done|finished) tasks\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        text = (ctx.raw_text or "").lower()
        status = str(kwargs.get("status") or "open")
        if re.search(r"\b(?:completed|done|finished)\b", text):
            status = "done"
        elif re.search(r"\ball tasks\b", text):
            status = "all"

        tasks = await asyncio.to_thread(list_tasks, status=status, limit=int(kwargs.get("limit") or 10))
        summary = await asyncio.to_thread(task_summary)
        if not tasks:
            message = "You have no tasks recorded." if status == "all" else f"Your {status} task list is empty."
            return SkillResult.success(message, data={"tasks": [], "summary": summary},
                                       display={"kind": "tasks", "status": status, "tasks": [], "summary": summary})

        spoken = "; ".join(
            f"{index}. {task['title']}"
            + (f" (due {task['due_at'][:16].replace('T', ' ')})" if task.get("due_at") else "")
            for index, task in enumerate(tasks[:5], start=1)
        )
        extra = f" {summary['open']} open in total." if status == "done" else ""
        return SkillResult.success(
            f"Here are your {status} tasks: {spoken}.{extra}",
            data={"tasks": tasks, "summary": summary},
            display={"kind": "tasks", "status": status, "tasks": tasks, "summary": summary},
        )

@register
class CompleteTaskSkill(Skill):
    name = "complete_task"
    description = "Mark a task as done."
    category = "productivity"
    examples = ("mark review the report as done", "complete task 3")
    params = (Param("reference", "string", "Task id or part of its title", required=True),)
    patterns = (
        r"^(?:mark|complete|finish|check off)\s+(?:the )?task\s+(?P<reference>.+?)\s+(?:as )?(?:done|complete|finished)$",
        r"^(?:complete|finish|check off|done with)\s+(?:the )?task\s+(?P<reference>.+)$",
        r"^(?:complete|finish)\s+(?P<reference>.+)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        reference = str(kwargs.get("reference") or "").strip().strip(".!")
        if not reference:
            return SkillResult.failure("Which task should I complete?", "missing reference")
        task = await asyncio.to_thread(complete_task, reference)
        if task is None:
            return SkillResult.failure(f"I could not find an open task matching '{reference}'.", "task not found")
        return SkillResult.success(f"Completed: {task['title']}.", data=task,
                                   display={"kind": "task", "action": "completed", "task": task})


@register
class DeleteTaskSkill(Skill):
    name = "delete_task"
    description = "Delete a task permanently."
    category = "productivity"
    dangerous = True
    requires_confirmation = True
    examples = ("delete the task buy milk",)
    params = (Param("reference", "string", "Task id or part of its title", required=True),)
    patterns = (r"^(?:delete|remove|drop)\s+(?:the )?task\s+(?P<reference>.+)$",)
    confirm_template = "Shall I delete the task '{reference}'?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        reference = str(kwargs.get("reference") or "").strip()
        if not reference:
            return SkillResult.failure("Which task should I delete?", "missing reference")
        removed = await asyncio.to_thread(delete_task, reference)
        if not removed:
            return SkillResult.failure(f"No task matches '{reference}'.", "task not found")
        return SkillResult.success(f"Deleted the task '{reference}'.", data={"reference": reference},
                                   display={"kind": "task", "action": "deleted", "reference": reference})

@register
class AddReminderSkill(Skill):
    name = "add_reminder"
    description = "Set a reminder that JARVIS announces at the right time (repeating reminders supported)."
    category = "productivity"
    examples = ("remind me to call mom at 6pm", "remind me to stretch in 20 minutes")
    params = (
        Param("title", "string", "What to be reminded about", required=True),
        Param("when", "string", "Natural-language time, e.g. 'in 10 minutes', 'tomorrow at 9'"),
        Param("repeat", "string", "none | daily | weekdays | weekly | monthly", default="none"),
    )
    patterns = (
        r"^(?:please\s+)?remind me to\s+(?P<title>.+?)(?:\s+in\s+(?P<when_in>\d+(?:\s+\w+)?)|(?:\s+at\s+)(?P<when_at>.+)|(?:\s+by\s+)(?P<when_by>.+))?$",
        r"^(?:please\s+)?(?:set|create|add) (?:a )?reminder(?: to| for)?\s+(?P<title>.+?)(?:\s+(?:at|in|by|on)\s+(?P<when_at>.+))?$",
        r"^(?:please\s+)?remind me (?:in|after)\s+(?P<when_delay>\d+\s*\w+)\s+to\s+(?P<title>.+)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        title = str(kwargs.get("title") or "").strip().strip(".!")
        if not title:
            return SkillResult.failure("What should I remind you about?", "missing title")

        composed = " ".join(
            str(kwargs[key])
            for key in ("when", "when_in", "when_at", "when_by", "when_delay")
            if kwargs.get(key)
        )
        moment = parse_when(composed) or parse_when(ctx.raw_text)
        if moment is None:
            return SkillResult.failure(
                f"When should I remind you about '{title}'? For example: 'remind me to {title} in 15 minutes'.",
                "missing time",
            )

        repeat = str(kwargs.get("repeat") or "none")
        if repeat == "none":
            repeat = parse_repeat(ctx.raw_text)
        reminder = await asyncio.to_thread(scheduler.add_reminder, title, moment, repeat=repeat)
        repeat_note = "" if repeat == "none" else f", repeating {repeat}"
        return SkillResult.success(
            f"Reminder set: {title} — {humanize_when(moment)}{repeat_note}.",
            data=reminder,
            display={"kind": "reminder", "action": "created", "reminder": reminder},
        )


@register
class ListRemindersSkill(Skill):
    name = "list_reminders"
    description = "List upcoming reminders."
    category = "productivity"
    examples = ("what reminders do I have",)
    patterns = (
        r"\b(?:what|which|list|show)(?: are)?(?: my)?(?: upcoming)? reminders\b",
        r"\bmy reminders\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        upcoming = await asyncio.to_thread(scheduler.list_reminders, active_only=True)
        if not upcoming:
            return SkillResult.success("You have no reminders scheduled.", data={"reminders": []},
                                       display={"kind": "reminders", "reminders": []})
        spoken = "; ".join(f"{item['title']} at {item['fire_at'][:16].replace('T', ' ')}" for item in upcoming[:5])
        return SkillResult.success(
            f"You have {len(upcoming)} reminder(s): {spoken}.",
            data={"reminders": upcoming},
            display={"kind": "reminders", "reminders": upcoming},
        )

@register
class CancelReminderSkill(Skill):
    name = "cancel_reminder"
    description = "Cancel a scheduled reminder by id or title."
    category = "productivity"
    dangerous = True
    requires_confirmation = True
    examples = ("cancel my reminder about the standup",)
    params = (Param("reference", "string", "Reminder id or part of its title", required=True),)
    patterns = (r"^(?:cancel|delete|remove)\s+(?:the )?reminder\s+(?:about |for |to )?(?P<reference>.+)$",)
    confirm_template = "Shall I cancel the reminder '{reference}'?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        reference = str(kwargs.get("reference") or "").strip().strip(".!")
        if not reference:
            return SkillResult.failure("Which reminder should I cancel?", "missing reference")
        upcoming = await asyncio.to_thread(scheduler.list_reminders, active_only=True)
        match = None
        if reference.isdigit():
            match = next((item for item in upcoming if int(item["id"]) == int(reference)), None)
        if match is None:
            lowered = reference.lower()
            match = next((item for item in upcoming if lowered in (item["title"] or "").lower()), None)
        if match is None:
            return SkillResult.failure(f"I found no active reminder matching '{reference}'.", "not found")
        removed = await asyncio.to_thread(scheduler.cancel, int(match["id"]))
        if not removed:
            return SkillResult.failure("I could not cancel that reminder.", "cancel failed")
        return SkillResult.success(f"Cancelled the reminder '{match['title']}'.", data=match,
                                   display={"kind": "reminder", "action": "cancelled", "reminder": match})


@register
class SetTimerSkill(Skill):
    name = "set_timer"
    description = "Start a countdown timer that speaks when it finishes."
    category = "productivity"
    examples = ("set a timer for 10 minutes", "timer for 90 seconds")
    params = (
        Param("duration", "string", "Duration such as '10 minutes' or '90 seconds'", required=True),
        Param("label", "string", "What the timer is for"),
    )
    patterns = (
        r"^(?:set|start)(?: a)? timer for\s+(?P<duration>\d+\s*(?:seconds?|minutes?|hours?)(?:\s+and\s+\d+\s*\w+)?)$",
        r"^timer for\s+(?P<duration>\d+\s*(?:seconds?|minutes?|hours?))$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        duration_text = str(kwargs.get("duration") or "").strip()
        composed = " ".join(part for part in (ctx.raw_text, duration_text) if part)
        moment = parse_when(f"in {duration_text}") or parse_when(composed)
        if moment is None:
            return SkillResult.failure("How long should the timer run?", "missing duration")
        seconds = max(1.0, (moment - datetime.now()).total_seconds())
        label = str(kwargs.get("label") or "").strip() or f"Timer for {duration_text}"
        reminder = await asyncio.to_thread(scheduler.add_timer, seconds, label)
        minutes, remainder = divmod(int(seconds), 60)
        pretty = f"{minutes} minute(s) and {remainder} second(s)" if minutes else f"{remainder} seconds"
        return SkillResult.success(
            f"Timer started for {pretty}. I will tell you when it is done.",
            data=reminder,
            display={"kind": "timer", "action": "started", "reminder": reminder, "seconds": seconds},
        )

@register
class CreateNoteSkill(Skill):
    name = "create_note"
    description = "Save a note with a title and content."
    category = "productivity"
    examples = ("take a note: the server password rotates on Monday", "note that the client prefers email")
    params = (
        Param("content", "string", "Body of the note", required=True),
        Param("title", "string", "Note title"),
        Param("tags", "string", "Comma-separated tags"),
    )
    patterns = (
        r"^(?:take|make|create|write)(?: a)? note(?:\s*(?:that|:|-)\s*)?(?P<content>.+)$",
        r"^(?:note|note down|jot down)(?:\s*(?:that|:|-)\s*)(?P<content>.+)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        content = str(kwargs.get("content") or "").strip()
        if not content:
            return SkillResult.failure("What should the note say?", "missing content")
        title = str(kwargs.get("title") or "").strip() or (content[:60] + ("…" if len(content) > 60 else ""))
        note = await asyncio.to_thread(create_note, title, content, tags=str(kwargs.get("tags") or ""))
        return SkillResult.success(f"Noted: {title}.", data=note,
                                   display={"kind": "note", "action": "created", "note": note})


@register
class ListNotesSkill(Skill):
    name = "list_notes"
    description = "List or search saved notes."
    category = "productivity"
    examples = ("list my notes", "search my notes for password")
    params = (
        Param("query", "string", "Search text (title, body or tags)"),
        Param("limit", "integer", "Maximum notes to show", default=10),
    )
    patterns = (
        r"\b(?:list|show)(?: me)?(?: my| all| the)? notes\b(?:\s+(?:about|for|with)\s+(?P<query>.+))?",
        r"\bsearch (?:my |the )?notes(?: for)?\s+(?P<query>.+)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        query = str(kwargs.get("query") or "").strip()
        notes = await asyncio.to_thread(list_notes, limit=int(kwargs.get("limit") or 10), query=query)
        if not notes:
            message = f"I found no notes matching '{query}'." if query else "You have no notes saved yet."
            return SkillResult.success(message, data={"notes": []}, display={"kind": "notes", "notes": []})
        listed = "; ".join(item["title"] for item in notes[:6])
        return SkillResult.success(
            f"You have {len(notes)} note(s): {listed}.",
            data={"notes": notes},
            display={"kind": "notes", "notes": notes, "query": query},
        )


@register
class ReadNoteSkill(Skill):
    name = "read_note"
    description = "Read a saved note by title or id."
    category = "productivity"
    examples = ("read my note about the server",)
    params = (Param("reference", "string", "Note id or part of its title", required=True),)
    patterns = (r"^(?:read|open|show)(?: me)?(?: my| the)? note(?:s)?(?: about| titled| called)?\s+(?P<reference>.+)$",)

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        reference = str(kwargs.get("reference") or "").strip()
        note = await asyncio.to_thread(read_note, reference)
        if note is None:
            return SkillResult.failure(f"I could not find a note matching '{reference}'.", "note not found")
        return SkillResult.success(
            f"{note['title']}: {note['content'][:800]}",
            data=note,
            display={"kind": "note", "action": "read", "note": note},
        )

@register
class UpdateNoteSkill(Skill):
    name = "update_note"
    description = "Append to, or overwrite, an existing note."
    category = "productivity"
    dangerous = True
    requires_confirmation = True
    examples = ("append to my note about the server: port 8443",)
    params = (
        Param("reference", "string", "Note id or part of its title", required=True),
        Param("content", "string", "New text", required=True),
        Param("append", "boolean", "Append instead of replacing", default=True),
    )
    patterns = (
        r"^(?:append|add)\s+(?P<content>.+?)\s+(?:to|into) (?:my |the )?note\s+(?:about |titled |called )?(?P<reference>.+)$",
    )
    confirm_template = "Shall I update the note '{reference}'?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        reference = str(kwargs.get("reference") or "").strip()
        content = str(kwargs.get("content") or "").strip()
        existing = await asyncio.to_thread(read_note, reference)
        if existing is None:
            return SkillResult.failure(f"I could not find a note matching '{reference}'.", "note not found")
        new_content = f"{existing['content']}\n{content}" if kwargs.get("append", True) else content
        updated = await asyncio.to_thread(update_note, reference, content=new_content)
        return SkillResult.success(f"Updated the note '{updated['title']}'.", data=updated,
                                   display={"kind": "note", "action": "updated", "note": updated})


@register
class DeleteNoteSkill(Skill):
    name = "delete_note"
    description = "Delete a saved note."
    category = "productivity"
    dangerous = True
    requires_confirmation = True
    examples = ("delete the note about the server",)
    params = (Param("reference", "string", "Note id or part of its title", required=True),)
    patterns = (r"^(?:delete|remove)\s+(?:the )?note\s+(?:about |titled |called )?(?P<reference>.+)$",)
    confirm_template = "Shall I delete the note '{reference}'?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        reference = str(kwargs.get("reference") or "").strip()
        removed = await asyncio.to_thread(delete_note, reference)
        if not removed:
            return SkillResult.failure(f"I could not find a note matching '{reference}'.", "note not found")
        return SkillResult.success(f"Deleted the note '{reference}'.", data={"reference": reference},
                                   display={"kind": "note", "action": "deleted", "reference": reference})


__all__ = [
    "AddReminderSkill",
    "AddTaskSkill",
    "CancelReminderSkill",
    "CompleteTaskSkill",
    "CreateNoteSkill",
    "DeleteNoteSkill",
    "DeleteTaskSkill",
    "ListNotesSkill",
    "ListRemindersSkill",
    "ListTasksSkill",
    "PRIORITY_LABELS",
    "ReadNoteSkill",
    "SetTimerSkill",
    "UpdateNoteSkill",
    "complete_task",
    "create_note",
    "create_task",
    "delete_note",
    "delete_task",
    "list_notes",
    "list_tasks",
    "read_note",
    "task_summary",
    "update_note",
]