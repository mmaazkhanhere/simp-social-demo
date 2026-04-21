import json
import re
from collections.abc import Sequence
from typing import TypeVar

import httpx
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel

from app.core.config import settings

INTERNAL_LEAD_FIELDS = {
    "name",
    "phone",
    "employment_status",
    "monthly_income_range",
    "down_payment_range",
    "timeline",
    "intent_score",
}


class LLMServiceError(RuntimeError):
    pass


StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


def _ensure_llm_is_configured() -> None:
    if not settings.groq_api_key:
        raise LLMServiceError("LLM is not configured. Set GROQ_API_KEY before sending or generating messages.")


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


def _build_chat_groq(temperature: float = 0.0) -> ChatGroq:
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=temperature,
        max_tokens=250,
    )


def sanitize_customer_reply(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    safe_lines: list[str] = []

    for line in lines:
        normalized = line.lower()
        normalized_compact = re.sub(r"[*_`\\s]+", "", normalized)

        if normalized_compact.startswith("updated:"):
            continue

        if normalized.startswith("-"):
            field_name = normalized[1:].split(":", 1)[0].strip()
            if field_name in INTERNAL_LEAD_FIELDS:
                continue

        safe_lines.append(line)

    sanitized = "\n".join(safe_lines).strip()
    return sanitized or "Thanks for sharing that."


def generate_assistant_reply(system_prompt: str, history: Sequence[dict[str, str]], language: str) -> str:
    _ensure_llm_is_configured()

    try:
        return sanitize_customer_reply(_request_completion(system_prompt=system_prompt, history=history))
    except httpx.HTTPStatusError as exc:
        raise LLMServiceError(f"LLM request failed with status {exc.response.status_code}.") from exc
    except httpx.HTTPError as exc:
        raise LLMServiceError("LLM request failed due to a network error.") from exc


def generate_assistant_greeting(system_prompt: str, greeting_request: str, language: str, assistant_name: str) -> str:
    _ensure_llm_is_configured()

    try:
        return sanitize_customer_reply(
            _request_completion(
                system_prompt=system_prompt,
                history=[{"role": "user", "content": greeting_request}],
            )
        )
    except httpx.HTTPStatusError as exc:
        raise LLMServiceError(f"LLM greeting request failed with status {exc.response.status_code}.") from exc
    except httpx.HTTPError as exc:
        raise LLMServiceError("LLM greeting request failed due to a network error.") from exc


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


def generate_structured_model(
    system_prompt: str,
    request_text: str,
    schema: type[StructuredModel],
) -> StructuredModel | None:
    if not settings.groq_api_key:
        return None

    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", request_text),
            ]
        )
        structured_llm = _build_chat_groq().with_structured_output(schema)
        result = (prompt | structured_llm).invoke({})
        return result if isinstance(result, schema) else None
    except Exception:
        return None
