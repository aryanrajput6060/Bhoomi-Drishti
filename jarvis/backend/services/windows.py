"""Native Windows window management and synthetic input (pure ctypes).

Everything here talks straight to ``user32`` / ``kernel32`` so JARVIS needs no
third-party automation package to enumerate windows, focus or close them, move
the mouse, type text, send hotkeys or drive the media keys.
"""

from __future__ import annotations

import ctypes
import logging
import time
from ctypes import wintypes
from dataclasses import dataclass

from config import IS_WINDOWS

log = logging.getLogger("jarvis.winapi")

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
SW_HIDE, SW_SHOWNORMAL, SW_SHOWMINIMIZED, SW_SHOWMAXIMIZED, SW_RESTORE = 0, 1, 2, 3, 9
WM_CLOSE, GW_OWNER = 0x0010, 4
PROCESS_TERMINATE = 0x0001

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
INPUT_KEYBOARD, INPUT_MOUSE = 1, 0
MOUSEEVENTF_MOVE, MOUSEEVENTF_ABSOLUTE = 0x0001, 0x8000
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP = 0x0008, 0x0010
MOUSEEVENTF_WHEEL = 0x0800
WHEEL_DELTA = 120

#: Named virtual key codes accepted by :func:`press_keys` / :func:`hotkey`.
VK_CODES: dict[str, int] = {
    "backspace": 0x08, "tab": 0x09, "enter": 0x0D, "return": 0x0D, "shift": 0x10,
    "ctrl": 0x11, "control": 0x11, "alt": 0x12, "pause": 0x13, "capslock": 0x14,
    "esc": 0x1B, "escape": 0x1B, "space": 0x20, "pageup": 0x21, "pagedown": 0x22,
    "end": 0x23, "home": 0x24, "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28,
    "insert": 0x2D, "delete": 0x2E, "del": 0x2E, "win": 0x5B, "windows": 0x5B,
    "apps": 0x5D, "multiply": 0x6A, "add": 0x6B, "subtract": 0x6D, "decimal": 0x6E,
    "divide": 0x6F, "numlock": 0x90, "scrolllock": 0x91, "printscreen": 0x2C,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75,
    "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "media_next": 0xB0, "media_prev": 0xB1, "media_stop": 0xB2, "media_play": 0xB3,
    "volume_mute": 0xAD, "volume_down": 0xAE, "volume_up": 0xAF,
}


class WinApiError(RuntimeError):
    """Raised when a Windows call fails or is unavailable."""


def require_windows() -> None:
    if not IS_WINDOWS:
        raise WinApiError("This capability requires Windows.")


# --------------------------------------------------------------------------- #
# ctypes structures
# --------------------------------------------------------------------------- #
if IS_WINDOWS:  # pragma: no branch
    _ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", _ULONG_PTR)]

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", _ULONG_PTR)]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]

    class _INPUTUNION(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("union", _INPUTUNION)]

else:  # pragma: no cover - keeps the module importable on non-Windows hosts
    KEYBDINPUT = MOUSEINPUT = HARDWAREINPUT = _INPUTUNION = INPUT = object  # type: ignore[assignment]


@dataclass(slots=True)
class WindowInfo:
    """A visible top-level window."""

    hwnd: int
    title: str
    pid: int
    process: str = ""
    minimized: bool = False
    foreground: bool = False

    def as_dict(self) -> dict:
        return {
            "hwnd": self.hwnd,
            "title": self.title,
            "pid": self.pid,
            "process": self.process,
            "minimized": self.minimized,
            "foreground": self.foreground,
        }

# --------------------------------------------------------------------------- #
# Window enumeration
# --------------------------------------------------------------------------- #
_ENUM_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def _process_name(pid: int) -> str:
    """Best-effort image name for a process id (used for friendly labels)."""
    try:
        import psutil

        return psutil.Process(pid).name()
    except Exception:
        return ""


def enumerate_windows(*, include_hidden: bool = False) -> list[WindowInfo]:
    """Every top-level window with a title, newest process names resolved."""
    require_windows()
    user32 = ctypes.windll.user32
    foreground = user32.GetForegroundWindow()
    windows: list[WindowInfo] = []

    def callback(hwnd: int, _lparam: int) -> bool:
        if not include_hidden and not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value.strip()
        if not title:
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        windows.append(
            WindowInfo(
                hwnd=int(hwnd),
                title=title,
                pid=int(pid.value),
                process=_process_name(int(pid.value)),
                minimized=bool(user32.IsIconic(hwnd)),
                foreground=(int(hwnd) == int(foreground)),
            )
        )
        return True

    user32.EnumWindows(_ENUM_PROC(callback), 0)
    return windows


def find_windows(query: str, *, limit: int = 10) -> list[WindowInfo]:
    """Windows whose title or image name contains ``query`` (case-insensitive)."""
    needle = (query or "").strip().lower()
    if not needle:
        windows = enumerate_windows()
    else:
        windows = [
            window
            for window in enumerate_windows()
            if needle in window.title.lower() or needle in window.process.lower()
        ]
    # Foreground first, then the shortest title (usually the real app window).
    windows.sort(key=lambda item: (not item.foreground, len(item.title)))
    return windows[:limit]


def foreground_window() -> WindowInfo | None:
    require_windows()
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    for window in enumerate_windows(include_hidden=True):
        if window.hwnd == int(hwnd):
            return window
    return None


# --------------------------------------------------------------------------- #
# Window actions
# --------------------------------------------------------------------------- #
def focus_window(hwnd: int) -> bool:
    """Bring a window to the foreground, working around the foreground lock."""
    require_windows()
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)

    # Attaching our input queue to the target thread allows SetForegroundWindow
    # to succeed even when another process currently owns the foreground.
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    current_thread = kernel32.GetCurrentThreadId()
    attached = False
    if target_thread and target_thread != current_thread:
        attached = bool(user32.AttachThreadInput(current_thread, target_thread, True))
    try:
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
        user32.SetActiveWindow(hwnd)
    finally:
        if attached:
            user32.AttachThreadInput(current_thread, target_thread, False)
    time.sleep(0.12)
    return int(user32.GetForegroundWindow()) == int(hwnd)


def show_window(hwnd: int, command: int = SW_RESTORE) -> bool:
    require_windows()
    return bool(ctypes.windll.user32.ShowWindow(hwnd, command))


def close_window(hwnd: int, *, force: bool = False) -> bool:
    """Ask a window to close (WM_CLOSE); terminate its process when ``force``."""
    require_windows()
    user32 = ctypes.windll.user32
    if not force:
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        return True
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid.value)
    if not handle:
        return False
    try:
        return bool(ctypes.windll.kernel32.TerminateProcess(handle, 0))
    finally:
        ctypes.windll.kernel32.CloseHandle(handle)


def minimize_all() -> None:
    """Show the desktop (same as Win+D)."""
    press_keys("win+d")


def set_wallpaper(path: str) -> None:
    """Set the desktop wallpaper from an image file."""
    require_windows()
    SPI_SETDESKWALLPAPER, SPIF_UPDATEINIFILE, SPIF_SENDCHANGE = 0x0014, 0x01, 0x02
    result = ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, str(path), SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    if not result:
        raise WinApiError("Windows refused the wallpaper change.")


def lock_workstation() -> None:
    require_windows()
    if not ctypes.windll.user32.LockWorkStation():
        raise WinApiError("Could not lock the workstation.")


# --------------------------------------------------------------------------- #
# Screens & cursor
# --------------------------------------------------------------------------- #
def screen_size() -> tuple[int, int]:
    require_windows()
    user32 = ctypes.windll.user32
    try:
        user32.SetProcessDPIAware()
    except Exception:
        pass
    return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))


def cursor_position() -> tuple[int, int]:
    require_windows()
    point = wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
    return int(point.x), int(point.y)

# --------------------------------------------------------------------------- #
# Synthetic input
# --------------------------------------------------------------------------- #
def _send_inputs(inputs: list[INPUT]) -> None:
    require_windows()
    count = len(inputs)
    if count == 0:
        return
    array = (INPUT * count)(*inputs)
    sent = ctypes.windll.user32.SendInput(count, ctypes.byref(array), ctypes.sizeof(INPUT))
    if sent != count:
        raise WinApiError(f"SendInput delivered {sent}/{count} events")


def _keyboard_input(vk: int = 0, scan: int = 0, flags: int = 0) -> INPUT:
    return INPUT(type=INPUT_KEYBOARD, union=_INPUTUNION(ki=KEYBDINPUT(wVk=vk, wScan=scan, dwFlags=flags,
                                                                  time=0, dwExtraInfo=0)))


def _key_tokens(combo: str) -> list[int]:
    """Turn ``"ctrl+shift+s"`` into virtual key codes."""
    tokens: list[int] = []
    for raw in str(combo).replace(" ", "").split("+"):
        if not raw:
            continue
        lowered = raw.lower()
        if lowered in VK_CODES:
            tokens.append(VK_CODES[lowered])
        elif len(raw) == 1:
            code = ctypes.windll.user32.VkKeyScanW(ord(raw))
            if code == -1:
                raise WinApiError(f"Cannot map key '{raw}'")
            tokens.append(code & 0xFF)
        else:
            raise WinApiError(f"Unknown key name '{raw}'")
    return tokens


def press_keys(combo: str, *, hold_ms: int = 40) -> None:
    """Press a key or combination, e.g. ``"enter"``, ``"ctrl+shift+s"``, ``"win+d"``."""
    codes = _key_tokens(combo)
    if not codes:
        raise WinApiError("No keys given")
    downs = [_keyboard_input(vk=code) for code in codes]
    ups = [_keyboard_input(vk=code, flags=KEYEVENTF_KEYUP) for code in reversed(codes)]
    _send_inputs(downs)
    time.sleep(max(0.01, hold_ms / 1000.0))
    _send_inputs(ups)


def type_text(text: str, *, interval_ms: int = 8) -> int:
    """Type arbitrary Unicode text into the focused window."""
    written = 0
    for char in str(text):
        if char in "\r\n":
            _send_inputs([_keyboard_input(vk=VK_CODES["enter"]), _keyboard_input(vk=VK_CODES["enter"], flags=KEYEVENTF_KEYUP)])
            written += 1
            continue
        scan = ord(char)
        _send_inputs([
            _keyboard_input(scan=scan, flags=KEYEVENTF_UNICODE),
            _keyboard_input(scan=scan, flags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP),
        ])
        written += 1
        if interval_ms:
            time.sleep(interval_ms / 1000.0)
    return written


def media_key(name: str) -> None:
    """Send a hardware media key (play/pause, next track, volume …)."""
    mapping = {
        "play_pause": "media_play",
        "toggle": "media_play",
        "play": "media_play",
        "pause": "media_play",
        "next": "media_next",
        "previous": "media_prev",
        "prev": "media_prev",
        "stop": "media_stop",
        "volume_up": "volume_up",
        "volume_down": "volume_down",
        "mute": "volume_mute",
    }
    key = mapping.get(str(name).lower().replace(" ", "_"))
    if not key:
        raise WinApiError(f"Unknown media key '{name}'")
    press_keys(key, hold_ms=25)


def mouse_move(x: int, y: int) -> None:
    require_windows()
    ctypes.windll.user32.SetCursorPos(int(x), int(y))


def mouse_click(
    x: int | None = None,
    y: int | None = None,
    *,
    button: str = "left",
    double: bool = False,
) -> None:
    """Click (optionally at absolute screen coordinates)."""
    require_windows()
    if x is not None and y is not None:
        mouse_move(x, y)
        time.sleep(0.05)
    downs = {"left": MOUSEEVENTF_LEFTDOWN, "right": MOUSEEVENTF_RIGHTDOWN, "middle": 0x0020}
    ups = {"left": MOUSEEVENTF_LEFTUP, "right": MOUSEEVENTF_RIGHTUP, "middle": 0x0040}
    if button not in downs:
        raise WinApiError(f"Unknown mouse button '{button}'")
    presses = 2 if double else 1
    events: list[INPUT] = []
    for _ in range(presses):
        events.append(INPUT(type=INPUT_MOUSE, union=_INPUTUNION(mi=MOUSEINPUT(dwFlags=downs[button]))))
        events.append(INPUT(type=INPUT_MOUSE, union=_INPUTUNION(mi=MOUSEINPUT(dwFlags=ups[button]))))
    _send_inputs(events)


def mouse_scroll(clicks: int) -> None:
    """Scroll the wheel; positive scrolls up."""
    require_windows()
    amount = int(clicks) * WHEEL_DELTA
    _send_inputs([INPUT(type=INPUT_MOUSE, union=_INPUTUNION(mi=MOUSEINPUT(mouseData=amount & 0xFFFFFFFF,
                                                                      dwFlags=MOUSEEVENTF_WHEEL)))])


def clipboard_text() -> str:
    """Read clipboard text through PowerShell (reliable for all formats)."""
    from services import ps

    payload = ps.run_json_sync("clipboard.ps1", {"Json": True}, timeout=30, default={}) or {}
    return str(payload.get("text", ""))


def set_clipboard_text(text: str) -> None:
    from services import ps

    ps.run_script_sync("clipboard.ps1", {"Set": str(text)}, timeout=30)


__all__ = [
    "SW_RESTORE",
    "VK_CODES",
    "INPUT",
    "WinApiError",
    "WindowInfo",
    "clipboard_text",
    "close_window",
    "cursor_position",
    "enumerate_windows",
    "find_windows",
    "focus_window",
    "foreground_window",
    "lock_workstation",
    "media_key",
    "minimize_all",
    "mouse_click",
    "mouse_move",
    "mouse_scroll",
    "press_keys",
    "require_windows",
    "screen_size",
    "set_clipboard_text",
    "set_wallpaper",
    "show_window",
    "type_text",
]