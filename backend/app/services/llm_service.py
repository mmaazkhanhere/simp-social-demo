import json
import re
from collections.abc import Sequence

import httpx

from app.core.config import settings


def _fallback_reply(language: str) -> str:
    if language.lower() == "spanish":
        return (
            "Claro, te ayudo con eso. Para orientarte mejor, "
            "actualmente estas trabajando y en que rango de ingreso mensual estas?"
        )
    return (
        "Absolutely, I can help with that. To guide you properly, "
        "are you currently employed and what monthly income range are you in?"
    )


def _fallback_greeting(language: str, assistant_name: str) -> str:
    if language.lower() == "spanish":
        return (
            f"Hola, soy {assistant_name}. Estoy aqui para ayudarte con financiamiento BHPH. "
            "Para comenzar, estas trabajando actualmente?"
        )
    return (
        f"Hi, I am {assistant_name}. I can help with BHPH financing. "
        "To get started, are you currently employed?"
    )


def _request_completion(system_prompt: str, history: Sequence[dict[str, str]]) -> str:
    payload = {
        "model": settings.groq_model,
        "messages": [{"role": "system", "content": system_prompt}, *history],
        "temperature": 0.4,
        "max_tokens": 250,
    }
    headers = {"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"}
    with httpx.Client(timeout=20.0) as client:
        response = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def generate_assistant_reply(system_prompt: str, history: Sequence[dict[str, str]], language: str) -> str:
    if not settings.groq_api_key:
        return _fallback_reply(language)

    try:
        return _request_completion(system_prompt=system_prompt, history=history)
    except Exception:
        return _fallback_reply(language)


def generate_assistant_greeting(system_prompt: str, greeting_request: str, language: str, assistant_name: str) -> str:
    if not settings.groq_api_key:
        return _fallback_greeting(language, assistant_name)

    try:
        greeting = _request_completion(
            system_prompt=system_prompt,
            history=[{"role": "user", "content": greeting_request}],
        )
        return greeting or _fallback_greeting(language, assistant_name)
    except Exception:
        return _fallback_greeting(language, assistant_name)


def generate_structured_output(system_prompt: str, request_text: str) -> dict | None:
    if not settings.groq_api_key:
        return None

    try:
        output = _request_completion(
            system_prompt=system_prompt,
            history=[{"role": "user", "content": request_text}],
        )
        try:
            parsed = json.loads(output)
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", output, re.DOTALL)
            if not match:
                return None
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None
