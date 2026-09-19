"""Audit trail: every skill execution is written to SQLite for transparency."""

from __future__ import annotations

import logging
from typing import Any

from db import session_scope
from models import AuditEntry

log = logging.getLogger("jarvis.audit")

#: Keep the table bounded so the SQLite file never grows without limit.
MAX_ENTRIES = 5000


def record(
    skill: str,
    args: dict[str, Any] | None = None,
    *,
    ok: bool = True,
    risky: bool = False,
    confirmed: bool = False,
    duration_ms: float = 0.0,
    speech: str = "",
    error: str = "",
) -> None:
    """Persist one audited action. Never raises — auditing must not break a run."""
    try:
        with session_scope() as session:
            session.add(
                AuditEntry(
                    skill=skill[:80],
                    args={k: str(v)[:200] for k, v in (args or {}).items()},
                    ok=ok,
                    risky=risky,
                    confirmed=confirmed,
                    duration_ms=float(duration_ms or 0.0),
                    speech=(speech or "")[:2000],
                    error=(error or "")[:2000],
                )
            )
    except Exception as exc:  # pragma: no cover - defensive
        log.warning("audit write failed: %s", exc)


def recent(limit: int = 100, skill: str | None = None) -> list[dict[str, Any]]:
    """Most recent audit entries, newest first."""
    from sqlalchemy import select

    limit = max(1, min(int(limit or 100), 1000))
    with session_scope() as session:
        query = select(AuditEntry).order_by(AuditEntry.id.desc()).limit(limit)
        if skill:
            query = query.where(AuditEntry.skill == skill)
        return [row.as_dict() for row in session.scalars(query)]


def stats() -> dict[str, Any]:
    """Aggregate counts used by the HUD status panel."""
    from sqlalchemy import func, select

    with session_scope() as session:
        total = session.scalar(select(func.count(AuditEntry.id))) or 0
        failures = session.scalar(select(func.count(AuditEntry.id)).where(AuditEntry.ok.is_(False))) or 0
        risky = session.scalar(select(func.count(AuditEntry.id)).where(AuditEntry.risky.is_(True))) or 0
        top = session.execute(
            select(AuditEntry.skill, func.count(AuditEntry.id).label("uses"))
            .group_by(AuditEntry.skill)
            .order_by(func.count(AuditEntry.id).desc())
            .limit(5)
        ).all()
    return {
        "total": int(total),
        "failures": int(failures),
        "risky": int(risky),
        "top_skills": [{"skill": row[0], "uses": int(row[1])} for row in top],
    }


def prune(keep: int = MAX_ENTRIES) -> int:
    """Delete the oldest entries beyond ``keep``. Returns rows removed."""
    from sqlalchemy import delete, select

    with session_scope() as session:
        ids = list(session.scalars(select(AuditEntry.id).order_by(AuditEntry.id.desc()).offset(keep)))
        if not ids:
            return 0
        session.execute(delete(AuditEntry).where(AuditEntry.id.in_(ids)))
        return len(ids)


__all__ = ["MAX_ENTRIES", "prune", "recent", "record", "stats"]