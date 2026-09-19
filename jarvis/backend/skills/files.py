"""File and folder skills.

Every path is validated by :data:`services.safety.path_guard` first, so JARVIS
can only touch the operator's own folders. Destructive actions (delete, move,
overwrite) require confirmation, and deletions go to the recycle bin rather than
being unlinked outright.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import re
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from services import ps
from services.safety import SafetyError, path_guard
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.files")

TEXT_SUFFIXES = {
    ".txt", ".md", ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".csv", ".log", ".html", ".css", ".xml", ".sh", ".ps1", ".bat", ".java", ".c", ".cpp", ".h", ".go",
    ".rs", ".rb", ".php", ".sql", ".env", ".gitignore", ".rst",
}
MAX_READ_BYTES = 200_000


def _human(path: Path) -> str:
    return str(path)


def describe_entry(entry: Path, *, base: Path | None = None) -> dict[str, Any]:
    try:
        stat = entry.stat()
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
    except OSError:
        size, modified = 0, ""
    return {
        "name": entry.name,
        "path": str(entry),
        "relative": str(entry.relative_to(base)) if base and entry != base else entry.name,
        "is_dir": entry.is_dir(),
        "size": size,
        "size_text": _size_text(size) if entry.is_file() else "",
        "modified": modified,
        "suffix": entry.suffix.lower(),
    }


def _size_text(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def list_directory(path: str | Path, *, pattern: str = "*", limit: int = 200) -> dict[str, Any]:
    target = path_guard.resolve(path, action="read", must_exist=True)
    if not target.is_dir():
        raise SafetyError(f"{target} is a file, not a folder.")
    entries = sorted(target.glob(pattern or "*"), key=lambda item: (not item.is_dir(), item.name.lower()))
    return {
        "path": _human(target),
        "count": len(entries),
        "truncated": len(entries) > limit,
        "entries": [describe_entry(entry, base=target) for entry in entries[:limit]],
    }


def search_files(
    root: str | Path,
    *,
    name_pattern: str = "",
    contains: str = "",
    limit: int = 60,
    max_depth: int = 6,
) -> dict[str, Any]:
    base = path_guard.resolve(root, action="read", must_exist=True)
    if not base.is_dir():
        raise SafetyError(f"{base} is not a folder.")
    matches: list[dict[str, Any]] = []
    needle = contains.lower()
    glob_pattern = f"**/{name_pattern}" if name_pattern else "**/*"

    for candidate in base.glob(glob_pattern):
        if len(matches) >= limit:
            break
        try:
            depth = len(candidate.relative_to(base).parts)
        except ValueError:
            continue
        if depth > max_depth or candidate.is_dir():
            continue
        if candidate.suffix.lower() not in TEXT_SUFFIXES and needle:
            continue
        if needle:
            try:
                if candidate.stat().st_size > MAX_READ_BYTES:
                    continue
                content = candidate.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if needle not in content.lower():
                continue
            snippet = ""
            position = content.lower().find(needle)
            if position >= 0:
                snippet = content[max(0, position - 60) : position + 120].replace("\n", " ")
            item = describe_entry(candidate, base=base)
            item["snippet"] = snippet.strip()
            matches.append(item)
        else:
            matches.append(describe_entry(candidate, base=base))
    return {"root": _human(base), "count": len(matches), "truncated": len(matches) >= limit, "items": matches}

def read_text_file(path: str | Path, *, max_bytes: int = MAX_READ_BYTES) -> dict[str, Any]:
    target = path_guard.resolve(path, action="read", must_exist=True)
    if target.is_dir():
        raise SafetyError(f"{target} is a folder.")
    raw = target.read_bytes()
    truncated = len(raw) > max_bytes
    text = raw[:max_bytes].decode("utf-8", errors="replace")
    return {
        "path": _human(target),
        "name": target.name,
        "size": len(raw),
        "lines": text.count("\n") + 1,
        "truncated": truncated,
        "text": text,
    }


def write_text_file(path: str | Path, content: str, *, append: bool = False) -> dict[str, Any]:
    target = path_guard.resolve(path, action="append" if append else "write")
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with target.open(mode, encoding="utf-8") as handle:
        handle.write(content or "")
    return {"path": _human(target), "bytes": len((content or "").encode("utf-8")), "appended": append}


def make_directory(path: str | Path) -> dict[str, Any]:
    target = path_guard.resolve(path, action="mkdir")
    target.mkdir(parents=True, exist_ok=True)
    return {"path": _human(target)}


def move_path(source: str | Path, destination: str | Path) -> dict[str, Any]:
    src = path_guard.resolve(source, action="read", must_exist=True)
    dest = path_guard.resolve(destination, action="move")
    if dest.is_dir():
        dest = dest / src.name
    shutil.move(str(src), str(dest))
    return {"source": _human(src), "destination": _human(dest)}


def copy_path(source: str | Path, destination: str | Path) -> dict[str, Any]:
    src = path_guard.resolve(source, action="read", must_exist=True)
    dest = path_guard.resolve(destination, action="copy")
    if src.is_dir():
        if dest.exists() and dest.is_dir():
            dest = dest / src.name
        shutil.copytree(str(src), str(dest), dirs_exist_ok=False)
    else:
        if dest.is_dir():
            dest = dest / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dest))
    return {"source": _human(src), "destination": _human(dest)}


def delete_to_recycle_bin(path: str | Path) -> dict[str, Any]:
    """Send a file/folder to the recycle bin (recoverable, unlike a hard delete)."""
    target = path_guard.resolve(path, action="delete", must_exist=True)
    script = (
        "Add-Type -AssemblyName Microsoft.VisualBasic; "
        f"$p = '{str(target).replace(chr(39), chr(39) * 2)}'; "
        "if (Test-Path -LiteralPath $p -PathType Container) { "
        "[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory($p, 'OnlyErrorDialogs', 'SendToRecycleBin') } "
        "else { [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($p, 'OnlyErrorDialogs', 'SendToRecycleBin') }; "
        "'deleted'"
    )
    output = ps.run_code_sync(script, timeout=90, check=False)
    if "deleted" not in (output or ""):
        raise SafetyError(f"Windows refused to delete '{target}': {output.strip()}")
    return {"path": _human(target), "method": "recycle-bin"}


def zip_path(source: str | Path, destination: str | Path | None = None) -> dict[str, Any]:
    src = path_guard.resolve(source, action="read", must_exist=True)
    target = Path(destination) if destination else src.with_suffix(".zip")
    resolved = path_guard.resolve(str(target), action="zip")
    archive = shutil.make_archive(str(resolved.with_suffix("")), "zip", root_dir=str(src if src.is_dir() else src.parent),
                                  base_dir=src.name if src.is_dir() else None)
    return {"source": _human(src), "archive": archive, "bytes": Path(archive).stat().st_size}


def file_info(path: str | Path, *, hash_file: bool = False) -> dict[str, Any]:
    target = path_guard.resolve(path, action="read", must_exist=True)
    stat = target.stat()
    info: dict[str, Any] = {
        "path": _human(target),
        "name": target.name,
        "is_dir": target.is_dir(),
        "size": stat.st_size,
        "size_text": _size_text(stat.st_size),
        "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "suffix": target.suffix.lower(),
        "sensitive": path_guard.is_sensitive(target),
    }
    if hash_file and target.is_file() and stat.st_size < 200 * 1024 * 1024:
        digest = hashlib.sha256()
        with target.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        info["sha256"] = digest.hexdigest()
    return info


def recent_files(directory: str | Path, *, hours: int = 48, limit: int = 25) -> list[dict[str, Any]]:
    base = path_guard.resolve(directory, action="read", must_exist=True)
    cutoff = time.time() - hours * 3600
    found: list[dict[str, Any]] = []
    for entry in base.rglob("*"):
        try:
            if entry.is_file() and entry.stat().st_mtime >= cutoff:
                found.append(describe_entry(entry, base=base))
        except OSError:
            continue
        if len(found) >= limit * 3:
            break
    found.sort(key=lambda item: item["modified"], reverse=True)
    return found[:limit]


def open_in_explorer(path: str | Path) -> None:
    target = path_guard.resolve(path, action="read", must_exist=True)
    subprocess.Popen(["explorer.exe", str(target)], close_fds=True)

@register
class ListFilesSkill(Skill):
    name = "list_files"
    description = "List the contents of a folder (defaults to the home folder)."
    category = "files"
    examples = ("list my downloads folder", "what's in my documents")
    params = (
        Param("path", "string", "Folder to list (supports ~, Downloads, Documents …)"),
        Param("pattern", "string", "Glob filter such as '*.pdf'"),
    )
    patterns = (
        r"\b(?:list|show|what(?:'s| is)|whats) (?:are |is )?(?:the )?(?:files|contents|folders|items) in (?P<path>[^?]+)$",
        r"\b(?:list|show) (?P<path>(?:my |the )?(?:downloads|documents|desktop|pictures|music|videos)[^?]*)$",
        r"^browse (?P<path>.+)$",
    )
    friendly_paths = {
        "downloads": "~/Downloads", "documents": "~/Documents", "desktop": "~/Desktop",
        "pictures": "~/Pictures", "music": "~/Music", "videos": "~/Videos", "home": "~",
    }

    def _friendly(self, raw: str) -> str:
        cleaned = (raw or "").strip().strip("?").strip()
        cleaned = re.sub(r"^(?:my|the)\s+", "", cleaned).strip()
        for name, target in self.friendly_paths.items():
            if cleaned.lower() == name:
                return target
        return cleaned or "~"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        raw = str(kwargs.get("path") or "~")
        resolved = self._friendly(raw)
        try:
            payload = await asyncio.to_thread(list_directory, resolved, pattern=str(kwargs.get("pattern") or "*"))
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not read that folder: {exc}", str(exc))

        files = [item for item in payload["entries"] if not item["is_dir"]]
        folders = [item for item in payload["entries"] if item["is_dir"]]
        preview = ", ".join(item["name"] for item in payload["entries"][:10])
        speech = (
            f"{payload['path']} contains {len(folders)} folder(s) and {len(files)} file(s). First entries: {preview}."
            if payload["entries"]
            else f"{payload['path']} is empty."
        )
        return SkillResult.success(
            speech,
            data=payload,
            display={"kind": "files", **payload},
        )


@register
class ReadFileSkill(Skill):
    name = "read_file"
    description = "Read the contents of a text file."
    category = "files"
    examples = ("read notes.txt", "show me the contents of config.json")
    params = (Param("path", "string", "File to read", required=True),)
    patterns = (
        r"\b(?:read|open|show(?: me)?(?: the)?(?: contents of)?|cat)\s+(?P<path>[^\s].*\.(?:txt|md|json|py|js|ts|tsx|csv|log|yaml|yml|toml|ini|cfg|xml|html|css|sh|ps1|bat|java|c|cpp|h|go|rs|rb|php|sql))\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        try:
            payload = await asyncio.to_thread(read_text_file, kwargs.get("path"))
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not read that file: {exc}", str(exc))

        text = payload["text"]
        summary = text if len(text) <= 700 else text[:700] + " …"
        return SkillResult.success(
            f"{payload['name']} is {_size_text(payload['size'])} and {payload['lines']} lines. {summary}",
            data=payload,
            display={"kind": "file-read", "name": payload["name"], "path": payload["path"], "text": text[:6000],
                     "truncated": payload["truncated"]},
        )


@register
class WriteFileSkill(Skill):
    name = "write_file"
    description = "Create a file or append text to it."
    category = "files"
    dangerous = True
    requires_confirmation = True
    examples = ("write hello to notes.txt", "append this to todo.md: buy milk")
    params = (
        Param("path", "string", "File to write", required=True),
        Param("content", "string", "Text content", required=True),
        Param("append", "boolean", "Append instead of overwriting", default=False),
    )
    patterns = (
        r"^(?:write|save)\s+(?P<content>.+?)\s+(?:to|into)\s+(?P<path>[^\s]+)$",
        r"^append\s+(?P<content>.+?)\s+(?:to|into)\s+(?P<path>[^\s]+)$",
    )
    confirm_template = "Shall I write to {path}?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        append = bool(kwargs.get("append")) or (ctx.raw_text or "").strip().lower().startswith("append")
        try:
            payload = await asyncio.to_thread(
                write_text_file, kwargs.get("path"), str(kwargs.get("content") or ""), append=append
            )
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not write that file: {exc}", str(exc))
        verb = "appended to" if append else "written to"
        return SkillResult.success(
            f"{payload['bytes']} bytes {verb} {Path(payload['path']).name}.",
            data=payload,
            display={"kind": "file-write", **payload},
        )

@register
class SearchFilesSkill(Skill):
    name = "search_files"
    description = "Find files by name, or search inside text files for a phrase."
    category = "files"
    examples = ("search my documents for budget", "find all pdf files in downloads")
    params = (
        Param("root", "string", "Folder to search in", default="~"),
        Param("name_pattern", "string", "Glob such as '*.pdf'"),
        Param("contains", "string", "Text to look for inside files"),
        Param("limit", "integer", "Maximum matches", default=40),
    )
    patterns = (
        r"\b(?:search|find|look for)\b[^.]*?(?:for|named|called)\s+(?P<needle>[^?]+)$",
        r"\bfind all (?P<name_pattern>\*?\.[a-z0-9]{1,5}) files(?: in (?P<root>.+))?$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        root = str(kwargs.get("root") or "~")
        name_pattern = str(kwargs.get("name_pattern") or "")
        contains = str(kwargs.get("contains") or kwargs.get("needle") or "").strip()

        # "find all *.pdf files" -> glob, "search for budget" -> content search.
        if contains and re.fullmatch(r"\*?\.[a-z0-9]{1,5}", contains, re.IGNORECASE):
            name_pattern, contains = contains, ""
        elif contains and name_pattern:
            if name_pattern.startswith("*."):
                contains = ""

        try:
            payload = await asyncio.to_thread(
                search_files, root, name_pattern=name_pattern, contains=contains,
                limit=int(kwargs.get("limit") or 40),
            )
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"The search failed: {exc}", str(exc))

        if not payload["items"]:
            return SkillResult.success(f"I found no matches in {payload['root']}.", data=payload,
                                       display={"kind": "files-search", **payload})
        names = ", ".join(item["relative"] for item in payload["items"][:8])
        return SkillResult.success(
            f"Found {payload['count']} match(es) in {payload['root']}: {names}.",
            data=payload,
            display={"kind": "files-search", **payload},
        )


@register
class DeletePathSkill(Skill):
    name = "delete_path"
    description = "Delete a file or folder by moving it to the recycle bin (recoverable)."
    category = "files"
    dangerous = True
    requires_confirmation = True
    examples = ("delete old_notes.txt",)
    params = (Param("path", "string", "File or folder to delete", required=True),)
    patterns = (r"^(?:delete|remove|trash)\s+(?:the (?:file|folder) )?(?P<path>.+)$",)
    confirm_template = "Shall I delete {path}? It will go to the recycle bin."

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        try:
            payload = await asyncio.to_thread(delete_to_recycle_bin, kwargs.get("path"))
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not delete that: {exc}", str(exc))
        return SkillResult.success(
            f"Deleted {Path(payload['path']).name} — it is in the recycle bin if you need it back.",
            data=payload,
            display={"kind": "file-delete", **payload},
        )


@register
class MoveCopySkill(Skill):
    name = "move_path"
    description = "Move or copy a file or folder to another location."
    category = "files"
    dangerous = True
    requires_confirmation = True
    examples = ("move report.pdf to my documents", "copy notes.txt to the desktop")
    params = (
        Param("source", "string", "File or folder to move/copy", required=True),
        Param("destination", "string", "Target folder or path", required=True),
        Param("copy", "boolean", "Copy instead of move", default=False),
    )
    patterns = (r"^(?P<verb>move|copy)\s+(?P<source>.+?)\s+(?:to|into)\s+(?P<destination>.+)$",)
    confirm_template = "Shall I move {source} to {destination}?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        verb = (ctx.raw_text or "").strip().split(" ")[0].lower()
        copy = bool(kwargs.get("copy")) or verb == "copy"
        friendly = {"my documents": "~/Documents", "the documents": "~/Documents", "documents": "~/Documents",
                    "my downloads": "~/Downloads", "downloads": "~/Downloads", "my desktop": "~/Desktop",
                    "desktop": "~/Desktop", "the desktop": "~/Desktop", "pictures": "~/Pictures",
                    "music": "~/Music", "videos": "~/Videos"}
        destination = str(kwargs.get("destination") or "").strip().rstrip(".")
        destination = friendly.get(destination.lower(), destination)
        try:
            payload = await asyncio.to_thread(copy_path if copy else move_path, kwargs.get("source"), destination)
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not {'copy' if copy else 'move'} that: {exc}", str(exc))
        return SkillResult.success(
            f"{'Copied' if copy else 'Moved'} {Path(payload['source']).name} to {payload['destination']}.",
            data=payload,
            display={"kind": "file-move", "action": "copy" if copy else "move", **payload},
        )

@register
class FileInfoSkill(Skill):
    name = "file_info"
    description = "Show size, timestamps and optionally the SHA-256 hash of a file."
    category = "files"
    examples = ("how big is report.pdf", "info about notes.txt")
    params = (
        Param("path", "string", "File or folder to inspect", required=True),
        Param("hash", "boolean", "Compute the SHA-256 hash", default=False),
    )
    patterns = (r"\b(?:how (?:big|large) is|size of|info(?:rmation)? (?:about|on)|details of)\s+(?P<path>.+)$",)

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        try:
            payload = await asyncio.to_thread(file_info, kwargs.get("path"), hash_file=bool(kwargs.get("hash")))
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not inspect that path: {exc}", str(exc))
        speech = (
            f"{payload['name']} is {'a folder' if payload['is_dir'] else payload['size_text']}, "
            f"last modified {payload['modified']}."
        )
        if payload.get("sha256"):
            speech += f" SHA-256 begins {payload['sha256'][:16]}."
        return SkillResult.success(speech, data=payload, display={"kind": "file-info", **payload})


@register
class MakeDirectorySkill(Skill):
    name = "make_directory"
    description = "Create a new folder (including any missing parents)."
    category = "files"
    examples = ("create a folder called Projects",)
    params = (Param("path", "string", "Folder path to create", required=True),)
    patterns = (r"^(?:create|make|new)\s+(?:a\s+)?(?:new\s+)?(?:folder|directory)\s+(?:called |named )?(?P<path>.+)$",)

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        try:
            payload = await asyncio.to_thread(make_directory, kwargs.get("path"))
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not create that folder: {exc}", str(exc))
        return SkillResult.success(f"Created {payload['path']}.", data=payload,
                                   display={"kind": "file-mkdir", **payload})


@register
class ZipPathSkill(Skill):
    name = "zip_path"
    description = "Compress a file or folder into a ZIP archive."
    category = "files"
    dangerous = True
    requires_confirmation = True
    examples = ("zip my reports folder",)
    params = (
        Param("source", "string", "File or folder to compress", required=True),
        Param("destination", "string", "Destination .zip path"),
    )
    patterns = (r"^(?:zip|compress|archive)\s+(?P<source>.+)$",)
    confirm_template = "Shall I create a ZIP archive of {source}?"

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        try:
            payload = await asyncio.to_thread(zip_path, kwargs.get("source"), kwargs.get("destination"))
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not create the archive: {exc}", str(exc))
        return SkillResult.success(
            f"Created {Path(payload['archive']).name} ({_size_text(payload['bytes'])}).",
            data=payload,
            display={"kind": "file-zip", **payload},
        )


@register
class OpenFolderSkill(Skill):
    name = "open_folder"
    description = "Open a folder in File Explorer."
    category = "files"
    examples = ("open my downloads folder", "open the folder C:/Users/me/projects")
    params = (Param("path", "string", "Folder to open", default="~"),)
    patterns = (
        r"^(?:open|show)(?: me)? (?:the )?folder (?P<path>.+)$",
        r"^open (?:my )?(?P<path>downloads|documents|desktop|pictures|music|videos)(?: folder)?$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        raw = str(kwargs.get("path") or "~").strip().rstrip(".")
        friendly = {
            "downloads": "~/Downloads", "documents": "~/Documents", "desktop": "~/Desktop",
            "pictures": "~/Pictures", "music": "~/Music", "videos": "~/Videos",
        }
        target = friendly.get(raw.lower(), raw)
        try:
            await asyncio.to_thread(open_in_explorer, target)
        except SafetyError as exc:
            return SkillResult.failure(str(exc), "path rejected")
        except Exception as exc:
            return SkillResult.failure(f"I could not open that folder: {exc}", str(exc))
        return SkillResult.success(f"Opened {raw}.", data={"path": target}, display={"kind": "file-open", "path": target})


__all__ = [
    "DeletePathSkill",
    "FileInfoSkill",
    "ListFilesSkill",
    "MakeDirectorySkill",
    "MoveCopySkill",
    "OpenFolderSkill",
    "ReadFileSkill",
    "SearchFilesSkill",
    "WriteFileSkill",
    "ZipPathSkill",
    "copy_path",
    "delete_to_recycle_bin",
    "file_info",
    "list_directory",
    "make_directory",
    "move_path",
    "open_in_explorer",
    "read_text_file",
    "recent_files",
    "search_files",
    "write_text_file",
    "zip_path",
]