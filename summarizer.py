from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict


DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


PROMPT_TEMPLATE = """You are an expert hiring evaluator with experience in technical and non-technical interviews.

Analyze the transcript and produce a structured evaluation.

Rules:

- Use ONLY information explicitly supported by the transcript.
- Do NOT hallucinate or infer missing details.
- If something is unclear or not present, write "Not enough evidence".
- Be specific and avoid generic statements.
- If multiple domains appear, choose the dominant role/profile supported by the transcript.

Output format:

{{
  "topics_covered": [
    "Specific topic 1",
    "Specific topic 2",
    "Specific topic 3"
  ],
  "profile": {{
    "role": "Suggested role",
    "level": "Junior / Mid-level / Senior",
    "justification": "Explain why based on transcript evidence"
  }},
  "candidate_summary": "Write a 3–6 sentence paragraph covering background, strengths, concerns, and overall impression."
}}

Transcript:
{transcript}
"""


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value and value[0] in {'"', "'"} and value[-1:] == value[0]:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def read_transcript(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Transcript file not found: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_prompt(transcript: str) -> str:
    return PROMPT_TEMPLATE.format(transcript=transcript)


def extract_json_text(text: str) -> str:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model response did not contain JSON object")
    return cleaned[start : end + 1]


def normalize_response(data: Dict[str, Any]) -> Dict[str, Any]:
    topics = data.get("topics_covered", [])
    if not isinstance(topics, list):
        topics = [str(topics)]
    topics = [str(topic).strip() for topic in topics if str(topic).strip()]

    profile = data.get("profile", {})
    if not isinstance(profile, dict):
        profile = {}

    normalized = {
        "topics_covered": topics,
        "profile": {
            "role": str(profile.get("role", "")).strip() or "Not enough evidence",
            "level": str(profile.get("level", "")).strip() or "Not enough evidence",
            "justification": str(profile.get("justification", "")).strip() or "Not enough evidence",
        },
        "candidate_summary": str(data.get("candidate_summary", "")).strip() or "Not enough evidence",
    }
    return normalized


def call_gemini(prompt: str, api_key: str, model: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{urllib.parse.quote(model, safe='')}:generateContent?key={urllib.parse.quote(api_key, safe='')}"
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read().decode("utf-8")

    response_json = json.loads(body)
    candidates = response_json.get("candidates", [])
    if not candidates:
        raise ValueError(f"Gemini response missing candidates: {response_json}")
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    if not text.strip():
        raise ValueError(f"Gemini response missing text: {response_json}")
    return text


def call_groq(prompt: str, api_key: str, model: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
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
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read().decode("utf-8")

    response_json = json.loads(body)
    choices = response_json.get("choices", [])
    if not choices:
        raise ValueError(f"Groq response missing choices: {response_json}")
    message = choices[0].get("message", {})
    text = message.get("content", "")
    if not text.strip():
        raise ValueError(f"Groq response missing text: {response_json}")
    return text


def call_openai(prompt: str, api_key: str, model: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
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
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        body = response.read().decode("utf-8")

    response_json = json.loads(body)
    choices = response_json.get("choices", [])
    if not choices:
        raise ValueError(f"OpenAI response missing choices: {response_json}")
    message = choices[0].get("message", {})
    text = message.get("content", "")
    if not text.strip():
        raise ValueError(f"OpenAI response missing text: {response_json}")
    return text


def choose_provider(explicit_provider: str | None) -> str:
    if explicit_provider:
        return explicit_provider.lower().strip()
    if os.environ.get("GEMINI_API_KEY"):
        return "gemini"
    if os.environ.get("GROQ_API_KEY"):
        return "groq"
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    raise RuntimeError(
        "No API key found. Set GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY in your environment or .env file."
    )


def determine_model(provider: str, explicit_model: str | None) -> str:
    if explicit_model:
        return explicit_model
    if provider == "gemini":
        return os.environ.get("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    if provider == "groq":
        return os.environ.get("GROQ_MODEL", DEFAULT_GROQ_MODEL)
    if provider == "openai":
        return os.environ.get("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    raise ValueError(f"Unsupported provider: {provider}")


def call_provider(provider: str, model: str, prompt: str) -> str:
    if provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing")
        return call_gemini(prompt, api_key, model)
    if provider == "groq":
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is missing")
        return call_groq(prompt, api_key, model)
    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")
        return call_openai(prompt, api_key, model)
    raise ValueError(f"Unsupported provider: {provider}")


def summarize(transcript_path: Path, provider: str | None, model: str | None) -> Dict[str, Any]:
    transcript = read_transcript(transcript_path)
    prompt = build_prompt(transcript)
    active_provider = choose_provider(provider)
    active_model = determine_model(active_provider, model)
    raw_response = call_provider(active_provider, active_model, prompt)
    parsed = json.loads(extract_json_text(raw_response))
    return normalize_response(parsed)


def render_human(result: Dict[str, Any]) -> str:
    lines = ["Topics covered:"]
    for topic in result["topics_covered"]:
        lines.append(f"- {topic}")
    lines.append("")
    lines.append("Profile:")
    lines.append(f"Role: {result['profile']['role']}")
    lines.append(f"Level: {result['profile']['level']}")
    lines.append(f"Justification: {result['profile']['justification']}")
    lines.append("")
    lines.append("Candidate summary:")
    lines.append(result["candidate_summary"])
    return "\n".join(lines)


def main() -> int:
    load_env_file(Path(".env"))

    parser = argparse.ArgumentParser(description="Summarize an interview transcript using an LLM.")
    parser.add_argument("transcript", help="Path to the transcript text file")
    parser.add_argument(
        "--provider",
        choices=["gemini", "groq", "openai"],
        help="LLM provider to use. Defaults to the first provider with an available API key.",
    )
    parser.add_argument("--model", help="Override the model name for the selected provider")
    parser.add_argument("--output", help="Optional output file path. Prints to stdout if omitted.")
    parser.add_argument(
        "--human",
        action="store_true",
        help="Print a human-readable summary instead of pretty JSON.",
    )
    args = parser.parse_args()

    try:
        result = summarize(Path(args.transcript), args.provider, args.model)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP error: {exc.code} {exc.reason}\n{error_body}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.human:
        output = render_human(result)
    else:
        output = json.dumps(result, indent=2, ensure_ascii=True)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())