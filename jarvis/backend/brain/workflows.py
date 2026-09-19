"""Multi-step workflow helpers (split 'and then' requests into steps)."""

from __future__ import annotations

import re

_SPLIT = re.compile(r"\s+(?:and then|then|after that|followed by|and also)\s+", re.IGNORECASE)


def split_steps(text: str) -> list[str]:
    parts = [p.strip(" ,.") for p in _SPLIT.split(text or "") if p.strip(" ,.")]
    return parts if len(parts) > 1 else [text.strip()]
