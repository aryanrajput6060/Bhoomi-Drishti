"""LLM client: OpenAI-compatible reasoning for JARVIS (part 1: config)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from config import settings

log = logging.getLogger("jarvis.llm")

HTTP_TIMEOUT = 90.0


class LLMError(RuntimeError):
    """Raised when the language model cannot be reached or refuses."""


@dataclass(slots=True)
class LLMMessage:
    role: str
    content: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    tool_call_id: str = ""
    name: str = ""

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"role": self.role, "content": self.content or ""}
        if self.tool_calls:
            payload["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            payload["tool_call_id"] = self.tool_call_id
        if self.name:
            payload["name"] = self.name
        return payload


def _provider_defaults(provider: str) -> tuple[str, str]:
    provider = (provider or "auto").lower()
    if provider == "ollama":
        return "http://localhost:11434/v1", "llama3.1"
    if provider == "lmstudio":
        return "http://localhost:1234/v1", "local-model"
    if provider == "anthropic":
        return "https://api.anthropic.com/v1", "claude-3-5-sonnet-latest"
    if provider == "gemini":
        return "https://generativelanguage.googleapis.com/v1beta/openai", "gemini-2.0-flash"
    if provider == "groq":
        return "https://api.groq.com/openai/v1", "llama-3.3-70b-versatile"
    if provider == "together":
        return "https://api.together.xyz/v1", "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    if provider == "openrouter":
        return "https://openrouter.ai/api/v1", "openai/gpt-4o-mini"
    if provider == "deepseek":
        return "https://api.deepseek.com/v1", "deepseek-chat"
    return "https://api.openai.com/v1", "gpt-4o-mini"


def resolve_endpoint() -> tuple[str, str, str]:
    provider = (settings.llm_provider or "auto").lower()
    default_base, default_model = _provider_defaults(provider)
    base_url = settings.llm_base_url or default_base
    model = settings.llm_model or default_model
    return base_url.rstrip("/"), model, settings.llm_api_key


def configured() -> bool:
    provider = (settings.llm_provider or "auto").lower()
    if provider == "none":
        return False
    if provider in {"ollama", "lmstudio"}:
        return True
    if settings.llm_base_url and provider in {"auto"}:
        return True
    return bool(settings.llm_api_key)

async def chat(
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    temperature: float | None = None,
    max_tokens: int = 1200,
    model: str | None = None,
) -> dict[str, Any]:
    """Call /chat/completions and return the raw assistant message dict."""
    import time as _time

    if not configured():
        raise LLMError("No language model is configured. Set LLM_API_KEY in jarvis/.env.")
    base_url, default_model, api_key = resolve_endpoint()
    body: dict[str, Any] = {
        "model": model or default_model,
        "messages": messages,
        "temperature": settings.llm_temperature if temperature is None else temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    started = _time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(f"{base_url}/chat/completions", json=body, headers=headers)
    except Exception as exc:
        raise LLMError(f"Could not reach the language model at {base_url}: {exc}") from exc
    latency = (_time.monotonic() - started) * 1000.0
    if response.status_code >= 400:
        raise LLMError(f"Language model refused (HTTP {response.status_code}): {response.text[:600]}")
    try:
        payload = response.json()
        message = payload["choices"][0]["message"]
    except Exception as exc:
        raise LLMError(f"Language model returned an unreadable response: {exc}") from exc
    message["_jarvis_latency_ms"] = round(latency, 1)
    message["_jarvis_model"] = body["model"]
    return message


async def simple_reply(system: str, user: str, *, max_tokens: int = 600) -> str:
    message = await chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=max_tokens,
    )
    content = message.get("content") or ""
    return content.strip() if isinstance(content, str) else ""


async def describe_image(image_data_url: str, prompt: str = "Describe what is on screen in detail.") -> str:
    if not configured():
        raise LLMError("No vision model is configured.")
    base_url, default_model, api_key = resolve_endpoint()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    body = {
        "model": settings.vision_model or default_model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_data_url}}]}],
        "max_tokens": 800,
    }
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(f"{base_url}/chat/completions", json=body, headers=headers)
    except Exception as exc:
        raise LLMError(f"Could not reach the vision model: {exc}") from exc
    if response.status_code >= 400:
        raise LLMError(f"Vision model refused (HTTP {response.status_code}): {response.text[:400]}")
    try:
        return response.json()["choices"][0]["message"].get("content", "").strip()
    except Exception as exc:
        raise LLMError(f"Vision model returned an unreadable response: {exc}") from exc


__all__ = ["HTTP_TIMEOUT", "LLMError", "LLMMessage", "chat", "configured",
           "describe_image", "resolve_endpoint", "simple_reply"]

