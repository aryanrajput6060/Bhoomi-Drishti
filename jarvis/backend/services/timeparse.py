"""Natural-language date/time parsing for reminders, tasks and timers.

Pure-stdlib parsing of the phrasings people actually use out loud:
``"in 10 minutes"``, ``"at 7:30 pm"``, ``"tomorrow at 9"``, ``"next monday at 5"``,
``"tonight"``, ``"noon"``. Returns naive **local** datetimes, matching what the
UI displays and the scheduler runs against.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta

WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")

_WORD_NUMBERS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20,
    "thirty": 30, "forty": 40, "forty five": 45, "forty-five": 45, "half": 0.5, "quarter": 0.25,
}

_AMOUNT = r"(?:\d+(?:\.\d+)?|a|an|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|thirty|forty|forty[- ]five|half|quarter)"
_UNIT = r"(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?)"

_IN_RELATIVE = re.compile(rf"\bin\s+(?:about\s+)?(?P<amount>{_AMOUNT})\s*(?P<unit>{_UNIT})\b", re.IGNORECASE)
_FROM_NOW = re.compile(rf"\b(?P<amount>{_AMOUNT})\s*(?P<unit>{_UNIT})\s+from now\b", re.IGNORECASE)
_AT_TIME = re.compile(r"\bat\s+(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<meridiem>am|pm|a\.m\.|p\.m\.)?\b",
                      re.IGNORECASE)
_CLOCK_ONLY = re.compile(r"^(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<meridiem>am|pm)?$", re.IGNORECASE)
_MONTH_DAY = re.compile(
    r"\b(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>january|february|march|april|may|june|july|august|"
    r"september|october|november|december)\b",
    re.IGNORECASE,
)

MONTHS = {
    name: index
    for index, name in enumerate(
        ("january", "february", "march", "april", "may", "june", "july", "august", "september",
         "october", "november", "december"),
        start=1,
    )
}


def _amount(raw: str) -> float | None:
    raw = (raw or "").strip().lower()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return float(_WORD_NUMBERS.get(raw, 0)) or None


def _apply_meridiem(hour: int, minute: int, meridiem: str | None) -> tuple[int, int]:
    if meridiem:
        marker = meridiem.replace(".", "").lower()
        if marker == "pm" and hour < 12:
            hour += 12
        elif marker == "am" and hour == 12:
            hour = 0
    return hour, minute


def _relative_delta(amount: float, unit: str) -> timedelta:
    unit = unit.lower()
    if unit.startswith("sec"):
        return timedelta(seconds=amount)
    if unit.startswith("min"):
        return timedelta(minutes=amount)
    if unit.startswith(("hour", "hr")):
        return timedelta(hours=amount)
    if unit.startswith("week"):
        return timedelta(weeks=amount)
    return timedelta(days=amount)

def parse_when(text: str, *, now: datetime | None = None) -> datetime | None:
    """Parse a natural-language time expression. ``None`` when there is none."""
    if not text:
        return None
    value = text.strip().lower()
    current = now or datetime.now()

    # -- relative: "in 10 minutes" / "2 hours from now" ------------------ #
    for pattern in (_IN_RELATIVE, _FROM_NOW):
        match = pattern.search(value)
        if match:
            amount = _amount(match.group("amount"))
            if amount is not None:
                return current + _relative_delta(amount, match.group("unit"))

    # -- day anchors ------------------------------------------------------ #
    day_offset: int | None = None
    if re.search(r"\bday after tomorrow\b", value):
        day_offset = 2
    elif re.search(r"\btomorrow\b", value):
        day_offset = 1
    elif re.search(r"\bnext week\b", value):
        day_offset = 7

    explicit_date: datetime | None = None
    month_match = _MONTH_DAY.search(value)
    if month_match:
        month = MONTHS[month_match.group("month").lower()]
        day = int(month_match.group("day"))
        for year in (current.year, current.year + 1):
            try:
                candidate = datetime(year, month, day)
            except ValueError:
                break
            if candidate.date() >= current.date() or year == current.year + 1:
                explicit_date = candidate
                break

    weekday_index: int | None = None
    for index, name in enumerate(WEEKDAYS):
        if re.search(rf"\b(?:next\s+|this\s+|on\s+)?{name}\b", value):
            weekday_index = index
            break

    # -- clock time ------------------------------------------------------- #
    hour: int | None = None
    minute = 0
    time_match = _AT_TIME.search(value)
    if time_match:
        hour = int(time_match.group("hour"))
        minute = int(time_match.group("minute") or 0)
        hour, minute = _apply_meridiem(hour, minute, time_match.group("meridiem"))
    else:
        clock_match = _CLOCK_ONLY.match(value.strip(" ."))
        if clock_match:
            hour = int(clock_match.group("hour"))
            minute = int(clock_match.group("minute") or 0)
            hour, minute = _apply_meridiem(hour, minute, clock_match.group("meridiem"))

    if hour is None:
        if re.search(r"\bnoon\b", value):
            hour, minute = 12, 0
        elif re.search(r"\bmidnight\b", value):
            hour, minute = 0, 0
        elif re.search(r"\bmorning\b", value):
            hour, minute = 9, 0
        elif re.search(r"\bafternoon\b", value):
            hour, minute = 15, 0
        elif re.search(r"\bevening\b|\btonight\b", value):
            hour, minute = 20, 0

    default_hour = hour if hour is not None else 9
    result: datetime | None = None

    if explicit_date is not None:
        result = explicit_date.replace(hour=default_hour, minute=minute)
    elif day_offset is not None:
        result = (current + timedelta(days=day_offset)).replace(hour=default_hour, minute=minute)
    elif weekday_index is not None:
        ahead = (weekday_index - current.weekday()) % 7
        if ahead == 0 or re.search(rf"\bnext\s+{WEEKDAYS[weekday_index]}\b", value):
            ahead = ahead or 7
        result = (current + timedelta(days=ahead)).replace(hour=default_hour, minute=minute)
    elif hour is not None:
        result = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if result <= current:
            # "at 7" said in the evening means tomorrow morning.
            result += timedelta(days=1)

    if result is None:
        return None
    return result.replace(second=0, microsecond=0)


def parse_repeat(text: str) -> str:
    """Detect a recurrence rule in a spoken phrase."""
    value = (text or "").lower()
    if re.search(r"\bevery\s+(?:week)?day\b|\bdaily\b", value):
        return "daily"
    if re.search(r"\bweekdays?\b", value) and "every" in value:
        return "weekdays"
    if re.search(r"\bevery\s+week\b|\bweekly\b", value):
        return "weekly"
    if re.search(r"\bevery\s+month\b|\bmonthly\b", value):
        return "monthly"
    return "none"


def humanize_when(moment: datetime, *, now: datetime | None = None) -> str:
    """Friendly phrasing for confirmations ("in 10 minutes", "tomorrow at 9:00 AM")."""
    current = now or datetime.now()
    seconds = (moment - current).total_seconds()
    if 0 <= seconds < 90:
        return "in under a minute"
    if 0 <= seconds < 3600:
        minutes = int(seconds // 60)
        return f"in {minutes} minute{'s' if minutes != 1 else ''}"
    if moment.date() == current.date():
        if seconds < 86400:
            hours = seconds / 3600
            return f"in {hours:.1f} hours".replace(".0", "")
        return f"today at {moment.strftime('%I:%M %p').lstrip('0')}"
    if moment.date() == (current + timedelta(days=1)).date():
        return f"tomorrow at {moment.strftime('%I:%M %p').lstrip('0')}"
    return moment.strftime("%A %d %B at %I:%M %p").replace(" 0", " ")


__all__ = ["MONTHS", "WEEKDAYS", "humanize_when", "parse_repeat", "parse_when"]