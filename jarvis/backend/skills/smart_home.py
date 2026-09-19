"""Smart-home and IoT control.

Two integration paths, both real:

* **Home Assistant** — full REST API support (list entities, read state, call any
  service: lights, switches, climate, covers, media players …).
* **Generic webhook** — POST a JSON payload to any URL, for devices or setups
  that expose nothing else (IFTTT, n8n, custom ESP32 firmware, etc.).

When neither is configured the skill says so explicitly instead of pretending.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from config import settings
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.smarthome")

HTTP_TIMEOUT = 20.0

DOMAIN_ALIASES = {
    "light": "light", "lights": "light", "lamp": "light", "lamps": "light",
    "switch": "switch", "switches": "switch", "plug": "switch", "socket": "switch",
    "fan": "fan", "cover": "cover", "blind": "cover", "blinds": "cover", "curtain": "cover",
    "climate": "climate", "thermostat": "climate", "ac": "climate", "heater": "climate",
    "media_player": "media_player", "speaker": "media_player", "tv": "media_player",
    "lock": "lock", "vacuum": "vacuum", "scene": "scene", "script": "script",
}


def home_assistant_configured() -> bool:
    return bool(settings.home_assistant_url and settings.home_assistant_token)


def _ha_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.home_assistant_token}",
        "Content-Type": "application/json",
    }


def _ha_base() -> str:
    return settings.home_assistant_url.rstrip("/")


async def ha_states() -> list[dict[str, Any]]:
    """Every entity Home Assistant knows about."""
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.get(f"{_ha_base()}/api/states", headers=_ha_headers())
        response.raise_for_status()
        payload = response.json()
    return [
        {
            "entity_id": item.get("entity_id", ""),
            "state": item.get("state", ""),
            "name": (item.get("attributes") or {}).get("friendly_name", item.get("entity_id", "")),
            "domain": item.get("entity_id", "").split(".")[0],
            "brightness": (item.get("attributes") or {}).get("brightness"),
        }
        for item in payload
    ]


async def ha_call_service(domain: str, service: str, entity_id: str = "", **data: Any) -> dict[str, Any]:
    """Call any Home Assistant service."""
    body: dict[str, Any] = {k: v for k, v in data.items() if v is not None}
    if entity_id:
        body["entity_id"] = entity_id
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.post(
            f"{_ha_base()}/api/services/{domain}/{service}", headers=_ha_headers(), json=body
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Home Assistant returned {response.status_code}: {response.text[:200]}")
        try:
            return {"ok": True, "result": response.json()}
        except Exception:
            return {"ok": True, "result": []}


def find_entities(states: list[dict[str, Any]], query: str, *, domain: str = "") -> list[dict[str, Any]]:
    """Fuzzy-match an entity by friendly name or id."""
    needle = (query or "").strip().lower()
    candidates = [item for item in states if not domain or item["domain"] == domain]
    if not needle:
        return candidates[:20]

    exact, starts, contains = [], [], []
    for item in candidates:
        name = (item["name"] or "").lower()
        entity = item["entity_id"].lower().split(".", 1)[-1]
        if needle in {name, entity}:
            exact.append(item)
        elif name.startswith(needle) or entity.startswith(needle):
            starts.append(item)
        elif needle in name or needle in entity:
            contains.append(item)
    return (exact or starts or contains)[:20]


async def post_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    """Send a JSON payload to the configured webhook."""
    if not settings.webhook_url:
        raise RuntimeError("No webhook URL is configured (set JARVIS_WEBHOOK_URL in .env).")
    body = dict(payload)
    if settings.webhook_secret:
        body["secret"] = settings.webhook_secret
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.post(settings.webhook_url, json=body)
        return {"ok": response.status_code < 400, "status": response.status_code, "body": response.text[:500]}

@register
class ListSmartDevicesSkill(Skill):
    name = "list_devices"
    description = "List the smart-home devices available through the configured integration."
    category = "smart_home"
    examples = ("list my smart devices", "what devices are available")
    patterns = (
        r"\blist (?:my |the )?(?:smart )?(?:devices|lights|switches|entities)\b",
        r"\bwhat (?:smart )?devices (?:do i have|are available)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        if not home_assistant_configured():
            return SkillResult.failure(
                "Smart-home control is not configured. Set JARVIS_HA_URL and JARVIS_HA_TOKEN (Home Assistant) "
                "or JARVIS_WEBHOOK_URL in .env, then restart JARVIS.",
                "smart home not configured",
            )
        try:
            states = await ha_states()
        except Exception as exc:
            return SkillResult.failure(f"I could not reach Home Assistant: {exc}", str(exc))

        controlled = [
            item for item in states
            if item["domain"] in {"light", "switch", "fan", "cover", "climate", "media_player",
                                  "lock", "vacuum", "scene", "script"}
        ]
        names = ", ".join(item["name"] for item in controlled[:12])
        return SkillResult.success(
            f"Home Assistant exposes {len(states)} entities, {len(controlled)} of them controllable. {names}",
            data={"total": len(states), "controllable": controlled[:60]},
            display={"kind": "smart-home", "total": len(states), "devices": controlled[:60]},
        )


@register
class WebhookTriggerSkill(Skill):
    name = "trigger_webhook"
    description = "Send a JSON event to the configured automation webhook (IFTTT, n8n, custom devices)."
    category = "smart_home"
    examples = ("trigger the movie night automation",)
    params = (
        Param("event", "string", "Event name to send", required=True),
        Param("payload", "string", "Extra JSON payload as a string"),
    )
    patterns = (r"^trigger (?:the )?(?P<event>.+?) (?:automation|webhook|routine)$",)

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        event = str(kwargs.get("event") or "").strip()
        if not settings.webhook_url:
            return SkillResult.failure(
                "No automation webhook is configured (set JARVIS_WEBHOOK_URL in .env).",
                "webhook not configured",
            )
        payload: dict[str, Any] = {"event": event, "source": "jarvis", "spoken": ctx.raw_text}
        if kwargs.get("payload"):
            payload["data"] = kwargs["payload"]
        try:
            result = await post_webhook(payload)
        except Exception as exc:
            return SkillResult.failure(f"I could not trigger that automation: {exc}", str(exc))
        if not result.get("ok"):
            return SkillResult.failure(f"The webhook returned status {result.get('status')}.", "webhook failed")
        return SkillResult.success(f"Triggered the {event} automation.", data=result,
                                   display={"kind": "webhook", "event": event, "result": result})

@register
class ControlSmartDeviceSkill(Skill):
    name = "home_assistant"
    description = ("Turn smart-home devices on or off, or call any Home Assistant service "
                   "(lights, switches, climate, covers, media players).")
    category = "smart_home"
    examples = ("turn on the desk lamp", "turn off all the lights", "set the bedroom lamp to 40 percent")
    params = (
        Param("action", "string", "on | off | toggle | brightness", required=True),
        Param("device", "string", "Device name or entity id"),
        Param("value", "integer", "Brightness percentage or temperature"),
        Param("domain", "string", "Home Assistant domain (light, switch, climate …)"),
    )
    patterns = (
        r"\bturn (?P<action>on|off|up) (?:the |my |all )?(?P<device>[a-z0-9][^,]{1,50}?)(?:\s+(?:light|lamp|fan|plug|socket|switch))?$",
        r"\b(?:switch|set) (?P<action>on|off) (?:the |my )?(?P<device>.+)$",
        r"\btoggle (?:the |my )?(?P<device>.+)$",
        r"\bset (?:the |my )?(?P<device>[a-z0-9][^,]{1,40}?) (?:brightness )?to (?P<value>\d{1,3})(?:\s*%)?$",
        r"\bdim (?:the |my )?(?P<device>.+?)(?:\s+to (?P<value>\d{1,3}))?$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        if not home_assistant_configured():
            return SkillResult.failure(
                "Smart-home control is not configured. Set JARVIS_HA_URL and JARVIS_HA_TOKEN in .env first.",
                "smart home not configured",
            )

        action = str(kwargs.get("action") or "toggle").lower()
        device = str(kwargs.get("device") or "").strip()
        value = kwargs.get("value")
        text = (ctx.raw_text or "").lower()
        if "toggle" in text:
            action = "toggle"
        elif action == "up":
            action = "on"
        if "dim" in text and value is None:
            action, value = "brightness", 30

        try:
            states = await ha_states()
        except Exception as exc:
            return SkillResult.failure(f"I could not reach Home Assistant: {exc}", str(exc))

        hints = [alias for alias in DOMAIN_ALIASES if alias in text]
        domain_hint = DOMAIN_ALIASES.get(hints[0], "") if hints else str(kwargs.get("domain") or "")
        matches = find_entities(states, device, domain=domain_hint) if device else []
        if not matches and domain_hint:
            matches = find_entities(states, "", domain=domain_hint)
        if not matches:
            return SkillResult.failure(f"I could not find a smart device called '{device}'.", "device not found")

        entity_ids = [item["entity_id"] for item in matches] if (len(matches) > 1 and "all" in text) \
            else [matches[0]["entity_id"]]
        target_domain = matches[0]["domain"]
        label = matches[0]["name"] if len(entity_ids) == 1 else f"{len(entity_ids)} devices"

        try:
            if action == "on":
                result = await ha_call_service(target_domain, "turn_on", ",".join(entity_ids))
            elif action == "off":
                result = await ha_call_service(target_domain, "turn_off", ",".join(entity_ids))
            elif action == "toggle":
                result = await ha_call_service(target_domain, "toggle", ",".join(entity_ids))
            elif action == "brightness" and value is not None:
                level = max(0, min(100, int(value)))
                if target_domain == "climate":
                    result = await ha_call_service(target_domain, "set_temperature", ",".join(entity_ids),
                                                   temperature=float(value))
                    label = f"{label} to {value} degrees"
                else:
                    result = await ha_call_service(target_domain, "turn_on", ",".join(entity_ids),
                                                   brightness=int(round(level / 100 * 255)))
                    label = f"{label} to {level} percent brightness"
            else:
                return SkillResult.failure("What should I do with that device?", "unknown action")
        except Exception as exc:
            return SkillResult.failure(f"Home Assistant rejected the command: {exc}", str(exc))

        verb = {"on": "Turned on", "off": "Turned off", "toggle": "Toggled", "brightness": "Set"}.get(
            action, "Updated"
        )
        return SkillResult.success(
            f"{verb} {label}.",
            data={"entities": entity_ids, "action": action, "result": result},
            display={"kind": "smart-home", "action": action, "entities": entity_ids, "message": f"{verb} {label}"},
        )


__all__ = [
    "ControlSmartDeviceSkill",
    "ListSmartDevicesSkill",
    "WebhookTriggerSkill",
    "DOMAIN_ALIASES",
    "find_entities",
    "ha_call_service",
    "ha_states",
    "home_assistant_configured",
    "post_webhook",
]