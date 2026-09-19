"""Web skills: search, page reading, weather and news — all real network calls.

Search works **without any API key** by parsing DuckDuckGo's HTML endpoint, and
automatically upgrades to Tavily / Serper / Brave when a key is configured.
Page reading fetches the URL and strips boilerplate down to readable text, and
optionally summarises it with the configured LLM.
"""

from __future__ import annotations

import asyncio
import html
import logging
import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import httpx

from config import settings
from skills.base import Param, Skill, SkillContext, SkillResult
from skills.registry import register

log = logging.getLogger("jarvis.skills.web")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 JARVIS/1.0"
)
HTTP_TIMEOUT = 20.0


class _TextExtractor(HTMLParser):
    """Very small readability pass: keeps visible prose, drops markup noise."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "head", "nav", "footer", "form", "iframe", "template"}
    BLOCK_TAGS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "section", "article", "pre"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.links: list[tuple[str, str]] = []
        self.title = ""
        self._in_title = False
        self._href: str | None = None
        self._link_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self._in_title = True
        if tag == "a":
            self._href = attributes.get("href")
            self._link_text = []
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag == "title":
            self._in_title = False
        if tag == "a" and self._href:
            label = " ".join(self._link_text).strip()
            if label:
                self.links.append((label, self._href))
            self._href = None
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title = (self.title + " " + text).strip()
        if self._href is not None:
            self._link_text.append(text)
        self.parts.append(text + " ")

    def text(self, *, limit: int = 20000) -> str:
        joined = "".join(self.parts)
        joined = re.sub(r"[ \t\u00a0]+", " ", joined)
        joined = re.sub(r"\n\s*\n\s*\n+", "\n\n", joined)
        return joined.strip()[:limit]


def extract_readable(html_text: str) -> dict[str, Any]:
    parser = _TextExtractor()
    try:
        parser.feed(html_text)
    except Exception as exc:  # malformed markup
        log.debug("html parse issue: %s", exc)
    return {"title": html.unescape(parser.title), "text": parser.text(), "links": parser.links[:40]}


async def fetch_page(url: str, *, timeout: float = HTTP_TIMEOUT) -> dict[str, Any]:
    """Download a page and return its readable text."""
    if not url.lower().startswith(("http://", "https://")):
        url = f"https://{url}"
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        raw = response.text
    if "html" not in content_type and "xml" not in content_type:
        return {"url": url, "content_type": content_type, "title": url, "text": raw[:20000], "links": []}
    extracted = extract_readable(raw)
    extracted.update({"url": str(response.url), "content_type": content_type, "status": response.status_code})
    return extracted

_DDG_RESULT = re.compile(
    r'<a[^>]+class="result__a"[^>]*href="(?P<url>[^"]+)"[^>]*>(?P<title>.*?)</a>.*?'
    r'(?:class="result__snippet"[^>]*>(?P<snippet>.*?)</a>)?',
    re.DOTALL | re.IGNORECASE,
)
_TAG = re.compile(r"<[^>]+>")


def _strip_tags(value: str) -> str:
    return html.unescape(_TAG.sub("", value or "")).strip()


def _clean_ddg_url(url: str) -> str:
    """DuckDuckGo wraps outbound links in /l/?uddg=<encoded>."""
    if "duckduckgo.com/l/" in url or url.startswith("/l/"):
        params = parse_qs(urlparse(url).query)
        if "uddg" in params:
            return unquote(params["uddg"][0])
    return url


async def _search_duckduckgo(query: str, limit: int) -> list[dict[str, Any]]:
    """Keyless search by parsing DuckDuckGo's HTML endpoint."""
    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True,
                                 headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get(f"https://html.duckduckgo.com/html/?q={quote_plus(query)}")
        response.raise_for_status()
        page = response.text

    for match in _DDG_RESULT.finditer(page):
        url = _clean_ddg_url(html.unescape(match.group("url")))
        title = _strip_tags(match.group("title"))
        snippet = _strip_tags(match.group("snippet") or "")
        if not url.startswith("http") or not title:
            continue
        results.append({"title": title, "url": url, "snippet": snippet, "source": "duckduckgo"})
        if len(results) >= limit:
            break
    if results:
        return results

    # Fallback: the Instant Answer API also needs no key.
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        instant = await client.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
        )
        payload = instant.json() if instant.status_code == 200 else {}
    if payload.get("AbstractText"):
        results.append({
            "title": payload.get("Heading") or query,
            "url": payload.get("AbstractURL") or f"https://duckduckgo.com/?q={quote_plus(query)}",
            "snippet": payload["AbstractText"],
            "source": "duckduckgo-instant",
        })
    for topic in (payload.get("RelatedTopics") or [])[:limit]:
        if topic.get("Text") and topic.get("FirstURL"):
            results.append({
                "title": topic["Text"][:120],
                "url": topic["FirstURL"],
                "snippet": topic["Text"],
                "source": "duckduckgo-instant",
            })
    return results[:limit]


async def _search_tavily(query: str, limit: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": settings.tavily_api_key, "query": query, "max_results": limit,
                  "include_answer": True, "search_depth": "basic"},
        )
        response.raise_for_status()
        payload = response.json()
    results = [
        {"title": item.get("title", ""), "url": item.get("url", ""), "snippet": item.get("content", ""),
         "source": "tavily"}
        for item in payload.get("results", [])
    ]
    if payload.get("answer"):
        results.insert(0, {"title": "Direct answer", "url": "", "snippet": payload["answer"], "source": "tavily"})
    return results[:limit]

async def _search_serper(query: str, limit: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "num": limit},
        )
        response.raise_for_status()
        payload = response.json()
    results = [
        {"title": item.get("title", ""), "url": item.get("link", ""), "snippet": item.get("snippet", ""),
         "source": "serper"}
        for item in payload.get("organic", [])
    ]
    answer = (payload.get("answerBox") or {}).get("answer")
    if answer:
        results.insert(0, {"title": "Direct answer", "url": "", "snippet": answer, "source": "serper"})
    return results[:limit]


async def _search_brave(query: str, limit: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": settings.brave_api_key, "Accept": "application/json"},
            params={"q": query, "count": limit},
        )
        response.raise_for_status()
        payload = response.json()
    return [
        {"title": item.get("title", ""), "url": item.get("url", ""),
         "snippet": _strip_tags(item.get("description", "")), "source": "brave"}
        for item in ((payload.get("web") or {}).get("results") or [])
    ][:limit]


async def search_web(query: str, *, limit: int = 6) -> dict[str, Any]:
    """Search the web, preferring a configured API key then DuckDuckGo."""
    query = (query or "").strip()
    if not query:
        return {"query": query, "results": [], "provider": "none", "error": "empty query"}

    preference = (settings.search_provider or "auto").lower()
    attempts: list[tuple[str, Any]] = []
    if preference in {"tavily", "auto"} and settings.tavily_api_key:
        attempts.append(("tavily", _search_tavily))
    if preference in {"serper", "auto"} and settings.serper_api_key:
        attempts.append(("serper", _search_serper))
    if preference in {"brave", "auto"} and settings.brave_api_key:
        attempts.append(("brave", _search_brave))
    if preference in {"duckduckgo", "auto"} or not attempts:
        attempts.append(("duckduckgo", _search_duckduckgo))

    errors: list[str] = []
    for name, handler in attempts:
        try:
            results = await handler(query, limit)
            if results:
                return {"query": query, "provider": name, "results": results[:limit], "error": ""}
            errors.append(f"{name}: no results")
        except Exception as exc:
            log.warning("search provider %s failed: %s", name, exc)
            errors.append(f"{name}: {exc}")
    return {"query": query, "provider": "none", "results": [], "error": "; ".join(errors)}


async def wikipedia_summary(topic: str, *, sentences: int = 4) -> dict[str, Any]:
    """Fetch a clean factual summary from the Wikipedia APIs."""
    title = (topic or "").strip()
    if not title:
        return {"found": False, "topic": title, "text": "", "url": ""}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        search = await client.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": title, "format": "json", "srlimit": 1},
        )
        hits = ((search.json().get("query") or {}).get("search") or []) if search.status_code == 200 else []
        if not hits:
            return {"found": False, "topic": title, "text": "", "url": ""}
        page_title = hits[0]["title"]
        summary = await client.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(page_title.replace(' ', '_'))}"
        )
        if summary.status_code != 200:
            return {"found": False, "topic": page_title, "text": "", "url": ""}
        payload = summary.json()

    extract = payload.get("extract", "") or ""
    if sentences and extract:
        extract = " ".join(re.split(r"(?<=[.!?])\s+", extract)[:sentences])
    return {
        "found": bool(extract),
        "topic": payload.get("title", page_title),
        "text": extract,
        "url": ((payload.get("content_urls") or {}).get("desktop") or {}).get("page", ""),
    }

#: WMO weather interpretation codes used by Open-Meteo.
WMO_CODES: dict[int, str] = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast", 45: "fog",
    51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
    61: "slight rain", 63: "moderate rain", 65: "heavy rain",
    71: "slight snow", 73: "moderate snow", 75: "heavy snow",
    80: "light rain showers", 81: "rain showers", 82: "violent rain showers",
    85: "snow showers", 86: "heavy snow showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "thunderstorm with heavy hail",
}


async def geocode(place: str) -> dict[str, Any]:
    """Coordinates for a place name, using the free Open-Meteo geocoder."""
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 1, "language": "en", "format": "json"},
        )
        response.raise_for_status()
        payload = response.json()
    results = payload.get("results") or []
    if not results:
        raise LookupError(f"I could not find a place called '{place}'.")
    top = results[0]
    return {
        "name": top.get("name"),
        "country": top.get("country", ""),
        "admin": top.get("admin1", ""),
        "latitude": top.get("latitude"),
        "longitude": top.get("longitude"),
        "timezone": top.get("timezone", "auto"),
    }


async def get_weather(place: str = "") -> dict[str, Any]:
    """Current conditions plus a three-day outlook (Open-Meteo, no API key)."""
    if place:
        location = await geocode(place)
    elif settings.default_city:
        location = await geocode(settings.default_city)
    elif settings.weather_latitude and settings.weather_longitude:
        location = {"name": "your configured location", "country": "", "admin": "",
                    "latitude": float(settings.weather_latitude), "longitude": float(settings.weather_longitude),
                    "timezone": "auto"}
    else:
        raise LookupError(
            "I do not know which city to check. Name a city, or set JARVIS_DEFAULT_CITY "
            "(or JARVIS_WEATHER_LAT / JARVIS_WEATHER_LON) in .env."
        )

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset",
                "timezone": "auto",
                "forecast_days": 3,
            },
        )
        response.raise_for_status()
        payload = response.json()

    current = payload.get("current") or {}
    daily = payload.get("daily") or {}
    codes = daily.get("weather_code") or []
    days = [
        {
            "date": day,
            "condition": WMO_CODES.get(codes[index], "unknown") if index < len(codes) else "unknown",
            "max": (daily.get("temperature_2m_max") or [None])[index],
            "min": (daily.get("temperature_2m_min") or [None])[index],
            "rain_chance": (daily.get("precipitation_probability_max") or [None])[index],
        }
        for index, day in enumerate((daily.get("time") or [])[:3])
    ]
    return {
        "location": location,
        "current": {
            "temperature": current.get("temperature_2m"),
            "feels_like": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "wind": current.get("wind_speed_10m"),
            "precipitation": current.get("precipitation"),
            "condition": WMO_CODES.get(current.get("weather_code"), "unknown"),
        },
        "daily": days,
        "sunrise": (daily.get("sunrise") or [None])[0],
        "sunset": (daily.get("sunset") or [None])[0],
    }

async def news_headlines(*, topic: str = "", limit: int = 6) -> list[dict[str, Any]]:
    """Top headlines from the Google News RSS feed (no API key needed)."""
    suffix = f"&q={quote_plus(topic)}" if topic else ""
    url = f"https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en{suffix}"
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True,
                                 headers={"User-Agent": USER_AGENT}) as client:
        response = await client.get(url)
        response.raise_for_status()
        xml = response.text

    items: list[dict[str, Any]] = []
    for match in re.finditer(r"<item>(.*?)</item>", xml, re.DOTALL):
        block = match.group(1)
        title = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block, re.DOTALL)
        link = re.search(r"<link>(.*?)</link>", block, re.DOTALL)
        source = re.search(r"<source[^>]*>(.*?)</source>", block, re.DOTALL)
        published = re.search(r"<pubDate>(.*?)</pubDate>", block, re.DOTALL)
        if not title:
            continue
        items.append({
            "title": html.unescape(_strip_tags(title.group(1))),
            "url": link.group(1).strip() if link else "",
            "source": _strip_tags(source.group(1)) if source else "",
            "published": published.group(1).strip() if published else "",
        })
        if len(items) >= limit:
            break
    return items


@register
class WebSearchSkill(Skill):
    name = "web_search"
    description = "Search the web and report the most relevant results."
    category = "web"
    examples = ("search for the latest ISRO launch", "google python asyncio tutorial")
    params = (
        Param("query", "string", "What to search for", required=True),
        Param("limit", "integer", "Number of results", default=5),
    )
    patterns = (
        r"^(?:please\s+)?(?:search|google|look up|find information about|search the web for|search for)\s+(?P<query>.+)$",
        r"^(?:what|who|when|where|why|how)\b.*\b(?:online|on the internet|on the web)\b(?P<query>.*)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        query = str(kwargs.get("query") or "").strip()
        if not query:
            return SkillResult.failure("What should I search for?", "missing query")
        payload = await search_web(query, limit=int(kwargs.get("limit") or 5))
        results = payload["results"]
        if not results:
            return SkillResult.failure(
                f"My web search for '{query}' returned nothing ({payload.get('error') or 'no results'}).",
                payload.get("error") or "no results",
            )

        top = results[0]
        summary = top["snippet"] or top["title"]
        others = "; ".join(f"{item['title']}" for item in results[1:4])
        speech = f"Top result for '{query}': {top['title']}. {summary[:300]}"
        if others:
            speech += f" Also relevant: {others}."
        return SkillResult.success(
            speech,
            data=payload,
            display={"kind": "search", "query": query, "provider": payload["provider"], "results": results},
        )


@register
class ReadPageSkill(Skill):
    name = "read_webpage"
    description = "Fetch a web page and read (or summarise) its main text."
    category = "web"
    examples = ("read https://example.com/article", "summarise this page https://news.ycombinator.com")
    params = (
        Param("url", "string", "Page URL to read", required=True),
        Param("summarize", "boolean", "Summarise with the LLM when available", default=True),
    )
    patterns = (
        r"\b(?:read|summari[sz]e|fetch|open|what does)\s+(?:the\s+)?(?:page|article|website|link|url)?\s*(?P<url>https?://\S+|\S+\.(?:com|org|net|io|dev|in|edu|gov)(?:/\S*)?)\b",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        url = str(kwargs.get("url") or "").strip().rstrip(".")
        if not url:
            return SkillResult.failure("Which page should I read?", "missing url")
        try:
            page = await fetch_page(url)
        except Exception as exc:
            return SkillResult.failure(f"I could not fetch {url}: {exc}", str(exc))

        text = page.get("text", "")
        if not text:
            return SkillResult.failure(f"{url} contained no readable text.", "empty page")

        summary = ""
        if kwargs.get("summarize", True):
            try:
                from brain.llm import llm

                if llm.available:
                    prompt = (
                        f"Summarise this web page in at most four sentences for a spoken reply.\n\n"
                        f"Title: {page.get('title')}\nURL: {page.get('url')}\n\n{text[:12000]}"
                    )
                    summary = (await llm.complete(prompt, system="You summarise web pages concisely.")).strip()
            except Exception as exc:
                log.debug("page summarisation unavailable: %s", exc)

        body = summary or text[:1200]
        return SkillResult.success(
            f"{page.get('title') or url}: {body}",
            data={"url": page.get("url", url), "title": page.get("title", ""), "text": text[:20000], "summary": summary},
            display={"kind": "webpage", "url": page.get("url", url), "title": page.get("title", ""),
                     "summary": summary, "text": text[:8000], "links": page.get("links", [])[:20]},
        )

@register
class WeatherSkill(Skill):
    name = "weather"
    description = "Report current weather and the three-day outlook for a city."
    category = "web"
    examples = ("what's the weather in Bengaluru", "weather forecast")
    params = (
        Param("city", "string", "City name (defaults to JARVIS_DEFAULT_CITY)"),
        Param("days", "integer", "Forecast days to mention", default=2),
    )
    patterns = (
        r"\b(?:what(?:'s| is) )?(?:the )?weather(?: like)?(?: in| for| at)\s+(?P<city>[a-z\s,.-]+?)\s*\??$",
        r"\b(?:what(?:'s| is) )?(?:the )?weather(?: forecast| report)?(?: today| now)?\??$",
        r"\b(?:forecast|temperature) (?:in|for)\s+(?P<city>[a-z\s,.-]+?)\s*\??$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        city = str(kwargs.get("city") or "").strip().title()
        try:
            report = await get_weather(city)
        except LookupError as exc:
            return SkillResult.failure(str(exc), "no location")
        except Exception as exc:
            return SkillResult.failure(f"I could not reach the weather service: {exc}", str(exc))

        current = report["current"]
        place = report["location"]["name"]
        days = report["daily"][: max(1, int(kwargs.get("days") or 2))]
        outlook = "; ".join(
            f"{day['date']}: {day['condition']}, {day['min']}–{day['max']} degrees"
            + (f", {day['rain_chance']}% chance of rain" if day.get("rain_chance") is not None else "")
            for day in days
        )
        speech = (
            f"In {place} it is {current['temperature']} degrees with {current['condition']}, "
            f"feeling like {current['feels_like']}. Humidity {current['humidity']} percent, wind {current['wind']} km/h. "
            f"Outlook — {outlook}."
        )
        return SkillResult.success(
            speech,
            data=report,
            display={"kind": "weather", "place": place, "current": current, "daily": days,
                     "sunrise": report.get("sunrise"), "sunset": report.get("sunset")},
        )


@register
class NewsSkill(Skill):
    name = "news"
    description = "Read out the latest news headlines."
    category = "web"
    examples = ("what's the news", "news about space")
    params = (
        Param("topic", "string", "Optional topic filter"),
        Param("limit", "integer", "Number of headlines", default=5),
    )
    patterns = (
        r"\b(?:what(?:'s| is) (?:the )?news|latest news|news headlines|headlines)\b(?:\s+(?:about|on)\s+(?P<topic>.+))?",
        r"\bnews about (?P<topic>.+)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        topic = str(kwargs.get("topic") or "").strip()
        try:
            headlines = await news_headlines(topic=topic, limit=int(kwargs.get("limit") or 5))
        except Exception as exc:
            return SkillResult.failure(f"I could not fetch the news: {exc}", str(exc))
        if not headlines:
            return SkillResult.failure("The news feed returned no headlines.", "empty feed")
        spoken = ". ".join(item["title"] for item in headlines[:4])
        return SkillResult.success(
            f"Here are the top headlines{' about ' + topic if topic else ''}: {spoken}.",
            data={"topic": topic, "headlines": headlines},
            display={"kind": "news", "topic": topic, "headlines": headlines},
        )

@register
class WikipediaSkill(Skill):
    name = "wikipedia"
    description = "Look up a factual summary of a topic from Wikipedia."
    category = "web"
    examples = ("who is Marie Curie", "tell me about the James Webb telescope")
    params = (Param("topic", "string", "Topic to look up", required=True),)
    patterns = (
        r"\b(?:who|what) (?:is|are|was|were)\s+(?P<topic>[a-z0-9][^?]{1,60})$",
        r"\b(?:tell me about|look up|explain)\s+(?P<topic>[a-z0-9][^?]{1,60})$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        topic = str(kwargs.get("topic") or "").strip()
        if not topic:
            return SkillResult.failure("What should I look up?", "missing topic")
        try:
            payload = await wikipedia_summary(topic)
        except Exception as exc:
            return SkillResult.failure(f"I could not reach Wikipedia: {exc}", str(exc))
        if not payload["found"]:
            return SkillResult.failure(f"I could not find a Wikipedia entry for '{topic}'.", "no article")
        return SkillResult.success(payload["text"], data=payload, display={"kind": "wikipedia", **payload})


@register
class OpenUrlSkill(Skill):
    name = "open_url"
    description = "Open a website in the default browser."
    category = "web"
    examples = ("open youtube.com", "go to github.com")
    params = (Param("url", "string", "Website to open", required=True),)
    patterns = (
        r"^(?:open|go to|navigate to|visit)\s+(?P<url>(?:https?://)?(?:www\.)?[a-z0-9-]+\.(?:com|org|net|io|dev|in|gov|edu|co|ai)(?:/\S*)?)$",
    )

    async def run(self, ctx: SkillContext, **kwargs: Any) -> SkillResult:
        import webbrowser

        url = str(kwargs.get("url") or "").strip()
        if not url:
            return SkillResult.failure("Which website should I open?", "missing url")
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        try:
            opened = await asyncio.to_thread(webbrowser.open, url)
        except Exception as exc:
            return SkillResult.failure(f"I could not open {url}: {exc}", str(exc))
        if opened is False:
            return SkillResult.failure("The system could not launch a browser for that link.", "browser refused")
        return SkillResult.success(f"Opening {url} in your browser.", data={"url": url},
                                   display={"kind": "webpage-open", "url": url})


__all__ = [
    "NewsSkill",
    "OpenUrlSkill",
    "ReadPageSkill",
    "WeatherSkill",
    "WebSearchSkill",
    "WikipediaSkill",
    "WMO_CODES",
    "extract_readable",
    "fetch_page",
    "geocode",
    "get_weather",
    "news_headlines",
    "search_web",
    "wikipedia_summary",
]