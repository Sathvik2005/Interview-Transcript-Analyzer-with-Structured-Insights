from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, Dict, List

import httpx

from app.core.config import settings
from app.core.prompt import PROMPT
from app.schemas import AnalysisResponse

logger = logging.getLogger(__name__)


def build_prompt(transcript: str) -> str:
    return PROMPT.format(transcript=transcript.strip())


def _validate_api_key(api_key: str, env_name: str) -> None:
    if not api_key or api_key.startswith("PASTE_"):
        raise RuntimeError(
            f"{env_name} is not configured. Add a real key in environment variables before analyzing."
        )


def extract_json_text(text: str) -> str:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response did not contain JSON")
    return cleaned[start : end + 1]


def normalize_response(payload: Dict[str, Any]) -> AnalysisResponse:
    topics = payload.get("topics_covered", [])
    if not isinstance(topics, list):
        topics = [topics]
    topics = [str(topic).strip() for topic in topics if str(topic).strip()]

    profile = payload.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    normalized = {
        "topics_covered": topics[:7],
        "profile": {
            "role": str(profile.get("role", "")).strip() or "Not enough evidence",
            "level": str(profile.get("level", "")).strip() or "Not enough evidence",
            "justification": str(profile.get("justification", "")).strip() or "Not enough evidence",
        },
        "candidate_summary": str(payload.get("candidate_summary", "")).strip() or "Not enough evidence",
    }
    return AnalysisResponse.model_validate(normalized)


async def _call_gemini(prompt: str, model: str) -> str:
    _validate_api_key(settings.gemini_api_key, "GEMINI_API_KEY")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={settings.gemini_api_key}"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
    }

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise ValueError(f"Gemini response missing candidates: {data}")
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    if not text.strip():
        raise ValueError(f"Gemini response missing text: {data}")
    return text


async def _call_chat_completions(url: str, api_key: str, model: str, prompt: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only valid JSON that matches the requested schema."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    choices = data.get("choices", [])
    if not choices:
        raise ValueError(f"Model response missing choices: {data}")
    message = choices[0].get("message", {})
    text = message.get("content", "")
    if not text.strip():
        raise ValueError(f"Model response missing text: {data}")
    return text


async def _attempt_with_retries(call_coro, max_attempts: int = 3, base_delay: float = 0.8):
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await call_coro()
        except httpx.HTTPStatusError as e:
            # For 4xx, don't retry except for 429
            status = getattr(e.response, "status_code", None)
            if status and 400 <= status < 500 and status != 429:
                logger.debug("Non-retryable HTTP error: %s", e)
                raise
            last_exc = e
        except (httpx.RequestError, asyncio.TimeoutError) as e:
            last_exc = e

        delay = base_delay * (2 ** (attempt - 1))
        logger.info("Attempt %s failed, retrying in %.1fs...", attempt, delay)
        await asyncio.sleep(delay)

    raise last_exc or RuntimeError("Unknown error during LLM request")


async def analyze_transcript(transcript: str, provider: str | None = None, model: str | None = None) -> AnalysisResponse:
    requested = (provider or settings.llm_provider).lower().strip()
    prompt = build_prompt(transcript)

    # Define preferred provider order. If a specific provider is requested, try it first.
    providers: List[str] = []
    order = ["gemini", "groq", "openai"]
    if requested in order:
        providers = [requested] + [p for p in order if p != requested]
    else:
        providers = order

    errors: Dict[str, str] = {}
    last_exception: Exception | None = None

    for prov in providers:
        try:
            if prov == "gemini":
                try:
                    _validate_api_key(settings.gemini_api_key, "GEMINI_API_KEY")
                except Exception as e:
                    errors[prov] = str(e)
                    logger.debug("Gemini key validation failed: %s", e)
                    raise
                active_model = model or settings.gemini_model

                async def call():
                    return await _call_gemini(prompt, active_model)

                raw = await _attempt_with_retries(call)
            elif prov == "groq":
                try:
                    _validate_api_key(settings.groq_api_key, "GROQ_API_KEY")
                except Exception as e:
                    errors[prov] = str(e)
                    logger.debug("Groq key validation failed: %s", e)
                    raise
                active_model = model or settings.groq_model

                async def call():
                    return await _call_chat_completions(
                        "https://api.groq.com/openai/v1/chat/completions",
                        settings.groq_api_key,
                        active_model,
                        prompt,
                    )

                raw = await _attempt_with_retries(call)
            elif prov == "openai":
                try:
                    _validate_api_key(settings.openai_api_key, "OPENAI_API_KEY")
                except Exception as e:
                    errors[prov] = str(e)
                    logger.debug("OpenAI key validation failed: %s", e)
                    raise
                active_model = model or settings.openai_model

                async def call():
                    return await _call_chat_completions(
                        "https://api.openai.com/v1/chat/completions",
                        settings.openai_api_key,
                        active_model,
                        prompt,
                    )

                raw = await _attempt_with_retries(call)
            else:
                continue

            # If we got here, parse and return
            parsed = json.loads(extract_json_text(raw))
            return normalize_response(parsed)

        except Exception as exc:  # try next provider
            last_exception = exc
            errors[prov] = str(exc)
            logger.warning("Provider %s failed: %s", prov, exc)
            # continue to next provider

    # All providers failed
    summary = ", ".join(f"{p}: {errors.get(p)}" for p in order if p in errors)
    logger.error("All providers failed: %s", summary)
    raise RuntimeError(f"All providers failed. Details: {summary}")
