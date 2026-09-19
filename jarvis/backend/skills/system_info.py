"""System telemetry: hardware status, processes, storage and network.

Backed by ``psutil`` (CPU, memory, disk, battery, network, processes) with WMI
fallbacks for the few values psutil does not expose on Windows.
"""

from __future__ import annotations

import asyncio
import logging
import platform
import re
import socket
import time
from datetime import datetime, timedelta
from typing import Any

from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.system_info")

try:
    import psutil
except Exception:  # pragma: no cover - psutil is a hard requirement
    psutil = None  # type: ignore[assignment]


def format_bytes(value: float | int | None) -> str:
    """Human readable byte size."""
    if not value:
        return "0 B"
    size = float(value)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"


def format_uptime(seconds: int) -> str:
    delta = timedelta(seconds=max(0, int(seconds)))
    days, remainder = divmod(int(delta.total_seconds()), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60
    parts: list[str] = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes and not days:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    return ", ".join(parts) or "less than a minute"


def collect_system_snapshot(*, with_processes: bool = False) -> dict[str, Any]:
    """A single consistent snapshot of machine health."""
    if psutil is None:
        raise RuntimeError("psutil is required for system telemetry (pip install psutil)")

    cpu_percent = psutil.cpu_percent(interval=0.4)
    per_cpu = psutil.cpu_percent(interval=None, percpu=True)
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    disks: list[dict[str, Any]] = []
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except (PermissionError, OSError):
            continue
        disks.append(
            {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "percent": usage.percent,
            }
        )

    battery: dict[str, Any] | None = None
    try:
        info = psutil.sensors_battery()
        if info is not None:
            battery = {
                "percent": round(info.percent, 1),
                "plugged": bool(info.power_plugged),
                "seconds_left": int(info.secsleft) if info.secsleft and info.secsleft > 0 else None,
            }
    except Exception:
        battery = None

    try:
        frequency = psutil.cpu_freq()
        cpu_ghz = round(frequency.current / 1000, 2) if frequency else None
    except Exception:
        cpu_ghz = None

    boot = datetime.fromtimestamp(psutil.boot_time())
    uptime_seconds = int((datetime.now() - boot).total_seconds())

    snapshot: dict[str, Any] = {
        "hostname": socket.gethostname(),
        "platform": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "cpu": {
            "percent": round(cpu_percent, 1),
            "cores_logical": psutil.cpu_count(logical=True),
            "cores_physical": psutil.cpu_count(logical=False),
            "per_core": [round(value, 1) for value in per_cpu],
            "ghz": cpu_ghz,
            "name": cpu_name(),
        },
        "memory": {
            "total": memory.total,
            "used": memory.used,
            "available": memory.available,
            "percent": memory.percent,
            "text": f"{format_bytes(memory.used)} of {format_bytes(memory.total)}",
        },
        "swap": {"total": swap.total, "used": swap.used, "percent": swap.percent},
        "disks": disks,
        "battery": battery,
        "boot_time": boot.isoformat(),
        "uptime_seconds": uptime_seconds,
        "uptime_text": format_uptime(uptime_seconds),
        "temperature_c": cpu_temperature(),
    }
    if with_processes:
        snapshot["processes"] = top_processes(limit=10)
    return snapshot

def cpu_name() -> str:
    """Marketing name of the processor (WMI, cached for the process lifetime)."""
    cached = getattr(cpu_name, "_cached", None)
    if cached is not None:
        return str(cached)
    value = ""
    try:
        from services import ps

        value = ps.run_code_sync(
            "Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name",
            timeout=25,
            check=False,
        ).strip()
    except Exception as exc:
        log.debug("cpu name lookup failed: %s", exc)
    cpu_name._cached = value or platform.processor() or "unknown CPU"  # type: ignore[attr-defined]
    return str(cpu_name._cached)  # type: ignore[attr-defined]


def cpu_temperature() -> float | None:
    """Best-effort CPU temperature via WMI; returns None when unavailable."""
    try:
        from services import ps

        payload = ps.run_code_sync(
            "$t = Get-CimInstance -Namespace root/WMI -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction Stop |"
            " Select-Object -First 1 -ExpandProperty CurrentTemperature;"
            " [math]::Round(($t / 10) - 273.15, 1)",
            timeout=25,
            check=False,
        ).strip()
        return float(payload) if payload else None
    except Exception:
        return None


def top_processes(limit: int = 10, *, sort_by: str = "cpu") -> list[dict[str, Any]]:
    """The busiest processes, sampled briefly so CPU percentages are meaningful."""
    if psutil is None:
        return []
    for process in psutil.process_iter(["pid"]):
        try:
            process.cpu_percent(None)
        except Exception:
            continue
    time.sleep(0.4)

    rows: list[dict[str, Any]] = []
    for process in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
        try:
            info = process.info
            rows.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "?",
                    "cpu": round(float(info.get("cpu_percent") or 0.0), 1),
                    "memory": round(float(info.get("memory_percent") or 0.0), 2),
                    "status": info.get("status") or "",
                }
            )
        except Exception:
            continue
    rows.sort(key=lambda item: item["cpu"] if sort_by == "cpu" else item["memory"], reverse=True)
    return rows[:limit]

@register
class SystemReportSkill(Skill):
    name = "system_report"
    description = "Report CPU, memory, disk, battery, temperature and uptime for this machine."
    category = "system"
    examples = ("system status", "how much RAM is free", "battery level")
    params = (Param("with_processes", "boolean", "Include the busiest processes", default=False),)
    patterns = (
        r"\b(?:system (?:status|report|health|info|information|check)|how(?:'s| is) (?:the )?system|"
        r"machine status|computer status)\b",
        r"\b(?:cpu|processor) (?:usage|load|status)\b",
        r"\b(?:memory|ram) (?:usage|status)\b|\bhow much (?:memory|ram) (?:is )?(?:free|used|left)\b",
        r"\b(?:disk|storage|drive) (?:space|usage|status)\b|\bhow much (?:disk|storage) (?:space )?(?:is )?(?:free|left)\b",
        r"\bbattery (?:level|status|percentage)\b|\bhow much battery\b",
        r"\b(?:uptime|how long has (?:this|the) (?:machine|computer) been (?:on|running))\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        text = (ctx.raw_text or "").lower()
        try:
            snapshot = await asyncio.to_thread(
                collect_system_snapshot, with_processes=bool(kwargs.get("with_processes"))
            )
        except Exception as exc:
            return SkillResult.failure(f"I could not read system telemetry: {exc}", str(exc))

        cpu, memory = snapshot["cpu"], snapshot["memory"]
        battery = snapshot.get("battery")

        if re.search(r"\bbattery\b", text) and battery:
            state = "plugged in" if battery["plugged"] else "on battery"
            left = f", roughly {battery['seconds_left'] // 60} minutes remaining" if battery.get("seconds_left") else ""
            speech = f"Battery is at {battery['percent']} percent, {state}{left}."
        elif re.search(r"\b(?:ram|memory)\b", text):
            speech = (
                f"Memory is {memory['percent']} percent used — {memory['text']} "
                f"({format_bytes(memory['available'])} available)."
            )
        elif re.search(r"\b(?:disk|storage|drive)\b", text):
            largest = max(snapshot["disks"], key=lambda disk: disk["total"], default=None)
            speech = (
                f"{largest['device']} is {largest['percent']} percent used — "
                f"{format_bytes(largest['used'])} of {format_bytes(largest['total'])}."
                if largest
                else "I could not read any disk information."
            )
        elif re.search(r"\b(?:cpu|processor)\b", text):
            speech = f"CPU is at {cpu['percent']} percent across {cpu['cores_logical']} logical cores."
        elif re.search(r"\buptime\b", text) or "how long" in text:
            speech = f"This machine has been running for {snapshot['uptime_text']}."
        else:
            segments = [f"CPU {cpu['percent']} percent", f"memory {memory['percent']} percent"]
            if snapshot["disks"]:
                segments.append(f"disk {snapshot['disks'][0]['percent']} percent")
            if battery:
                segments.append(f"battery {battery['percent']} percent")
            if snapshot.get("temperature_c"):
                segments.append(f"CPU temperature {snapshot['temperature_c']} degrees")
            speech = (
                f"{snapshot['hostname']} is running {snapshot['platform']}. "
                + ", ".join(segments)
                + f". Uptime {snapshot['uptime_text']}."
            )

        return SkillResult.success(
            speech,
            data=snapshot,
            display={
                "kind": "system",
                "hostname": snapshot["hostname"],
                "platform": snapshot["platform"],
                "cpu": {"percent": cpu["percent"], "name": cpu["name"], "cores": cpu["cores_logical"]},
                "memory": {"percent": memory["percent"], "text": memory["text"], "total": format_bytes(memory["total"])},
                "disks": [
                    {
                        "device": disk["device"],
                        "percent": disk["percent"],
                        "text": f"{format_bytes(disk['used'])} / {format_bytes(disk['total'])}",
                    }
                    for disk in snapshot["disks"][:4]
                ],
                "battery": battery,
                "uptime": snapshot["uptime_text"],
                "uptime_seconds": snapshot["uptime_seconds"],
                "temperature_c": snapshot.get("temperature_c"),
                "processes": (snapshot.get("processes") or [])[:5],
            },
        )

@register
class ListProcessesSkill(Skill):
    name = "list_processes"
    description = "Show the processes using the most CPU or memory right now."
    category = "system"
    examples = ("what's using the most CPU", "top processes by memory")
    params = (
        Param("sort_by", "string", "cpu | memory", enum=["cpu", "memory"], default="cpu"),
        Param("limit", "integer", "How many rows to return", default=8),
    )
    patterns = (
        r"\b(?:what(?:'s| is) (?:using|eating|taking) (?:the )?(?:most )?(?:cpu|memory|ram|resources))\b",
        r"\b(?:top|list|show) (?:the )?(?:processes|tasks)\b",
        r"\b(?:high cpu|memory hogs)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        text = (ctx.raw_text or "").lower()
        sort_by = "memory" if ("memory" in text or "ram" in text or kwargs.get("sort_by") == "memory") else "cpu"
        rows = await asyncio.to_thread(top_processes, int(kwargs.get("limit") or 8), sort_by=sort_by)
        if not rows:
            return SkillResult.failure("I could not read the process list.", "psutil unavailable")
        leading = rows[0]
        listed = ", ".join(f"{row['name']} {row[sort_by]}" for row in rows[:5])
        return SkillResult.success(
            f"Sorted by {sort_by}: the heaviest is {leading['name']} at {leading[sort_by]} "
            f"{'percent of memory' if sort_by == 'memory' else 'percent CPU'}. Top five: {listed}.",
            data={"sort_by": sort_by, "processes": rows},
            display={"kind": "processes", "sort_by": sort_by, "items": rows},
        )


@register
class NetworkInfoSkill(Skill):
    name = "network_info"
    description = "Report hostname, local IP addresses, the active Wi-Fi network and signal strength."
    category = "system"
    examples = ("network status", "what wifi am I on", "what's my IP")
    patterns = (
        r"\b(?:network (?:status|info|information)|connection status)\b",
        r"\b(?:what (?:wi-?fi|network) am i (?:on|connected to)|wi-?fi status|current (?:wi-?fi|ssid))\b",
        r"\b(?:my |what(?:'s| is) my )?(?:local )?ip(?:\s+address)?\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        addresses: list[str] = []
        try:
            import psutil as _psutil

            for name, entries in _psutil.net_if_addrs().items():
                for entry in entries:
                    if entry.family.name == "AF_INET" and not entry.address.startswith("127."):
                        addresses.append(f"{name}: {entry.address}")
        except Exception as exc:
            log.debug("network address lookup failed: %s", exc)

        wifi: dict[str, Any] = {}
        try:
            wifi = await ps.run_json("wifi.ps1", {"Action": "status"}, timeout=90, default={}) or {}
        except Exception as exc:
            log.debug("wifi query failed: %s", exc)

        parts = [f"Host {socket.gethostname()}"]
        if wifi.get("ssid"):
            parts.append(f"connected to Wi-Fi '{wifi['ssid']}' with {wifi.get('signal')} percent signal")
        elif wifi.get("adapter"):
            parts.append(f"the Wi-Fi adapter '{wifi['adapter']}' is {wifi.get('status')}")
        if addresses:
            parts.append("local addresses: " + "; ".join(addresses[:3]))
        speech = ". ".join(parts) + "."

        return SkillResult.success(
            speech,
            data={"hostname": socket.gethostname(), "addresses": addresses, "wifi": wifi},
            display={"kind": "network", "hostname": socket.gethostname(), "addresses": addresses, "wifi": wifi},
        )


__all__ = [
    "ListProcessesSkill",
    "NetworkInfoSkill",
    "SystemReportSkill",
    "collect_system_snapshot",
    "cpu_name",
    "cpu_temperature",
    "format_bytes",
    "format_uptime",
    "top_processes",
]