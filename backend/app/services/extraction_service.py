from typing import Any, Literal

from pydantic import BaseModel, Field

from app.services.llm_service import generate_structured_model, generate_structured_output

LEAD_UPDATE_FIELDS = (
    "name",
    "phone",
    "employment_status",
    "monthly_income_range",
    "down_payment_range",
    "timeline",
)

TIMELINE_VALUES = {
    "today": "this_week",
    "this week": "this_week",
    "within few days": "within_few_days",
    "within a few days": "within_few_days",
    "in a few days": "within_few_days",
    "few days": "within_few_days",
    "next week": "next_week",
    "this month": "this_month",
    "next month": "next_month",
    "this_week": "this_week",
    "within_few_days": "within_few_days",
    "next_week": "next_week",
    "this_month": "this_month",
    "next_month": "next_month",
}

EMPLOYMENT_VALUES = {
    "full time": "full time",
    "full-time": "full time",
    "full_time": "full time",
    "part time": "part time",
    "part-time": "part time",
    "part_time": "part time",
    "self employed": "self employed",
    "self-employed": "self employed",
    "self_employed": "self employed",
    "unemployed": "unemployed",
}


class LeadExtractionResult(BaseModel):
    name: str | None = Field(default=None, description="Customer name if explicitly stated.")
    phone: str | None = Field(default=None, description="Customer phone number digits if explicitly stated.")
    employment_status: str | None = Field(default=None, description="Employment status if stated.")
    monthly_income_range: str | None = Field(default=None, description="Monthly income amount as digits only if stated.")
    down_payment_range: str | None = Field(default=None, description="Down payment amount as digits only if stated.")
    timeline: str | None = Field(default=None, description="Normalized buying timeline if stated.")


class LeadExtractionEnvelope(BaseModel):
    updates: LeadExtractionResult = Field(default_factory=LeadExtractionResult)
    confidence: Literal["high", "medium", "low"] = "low"


def _empty_updates() -> dict[str, str | None]:
    return {field_name: None for field_name in LEAD_UPDATE_FIELDS}


def _normalize_name(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip(" .,!?") or None


def _normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    digits = "".join(char for char in value if char.isdigit())
    return digits or None


def _normalize_amount(value: str | None) -> str | None:
    if not value:
        return None
    digits = "".join(char for char in value if char.isdigit())
    return digits or None


def _normalize_employment_status(value: str | None) -> str | None:
    if not value:
        return None
    return EMPLOYMENT_VALUES.get(value.strip().lower())


def _normalize_timeline(value: str | None) -> str | None:
    if not value:
        return None
    return TIMELINE_VALUES.get(value.strip().lower())


def _coerce_extraction_result(payload: Any) -> LeadExtractionResult | None:
    if isinstance(payload, LeadExtractionEnvelope):
        return payload.updates
    if isinstance(payload, LeadExtractionResult):
        return payload
    if not isinstance(payload, dict):
        return None

    candidate = payload.get("updates") if isinstance(payload.get("updates"), dict) else payload
    try:
        return LeadExtractionResult.model_validate(candidate)
    except Exception:
        return None


def build_extraction_system_prompt() -> str:
    return (
        "You extract structured lead qualification data from a SINGLE customer message "
        "for a Buy Here Pay Here (BHPH) dealership.\n\n"

        "Rules:\n"
        "- Extract ONLY information explicitly stated in the message\n"
        "- If the message corrects previous info, return the corrected value\n"
        "- Do NOT infer, guess, or assume missing data\n"
        "- If a field is not present, return null\n"
        "- Ignore assistant messages and context outside this message\n"
        "- Ignore intent score and any internal CRM labels\n\n"

        "Output format:\n"
        "Return a valid JSON object with EXACTLY these fields:\n"
        "{\n"
        '  "name": string | null,\n'
        '  "phone": string | null,\n'
        '  "employment_status": string | null,\n'
        '  "monthly_income_range": string | null,\n'
        '  "down_payment_range": string | null,\n'
        '  "timeline": string | null\n'
        "}\n\n"

        "Normalization rules:\n"
        "- name: return only the person's name (no extra text)\n"
        "- phone: digits only (remove spaces, dashes, symbols)\n"
        "- employment_status: one of [full_time, part_time, self_employed, unemployed]\n"
        "- monthly_income_range: digits only, monthly amount (e.g. 3000)\n"
        "- down_payment_range: digits only (e.g. 1500)\n"
        "- timeline: one of [this_week, within_few_days, next_week, this_month, next_month]\n\n"

        "Examples:\n"
        "Message: 'I make about 3k a month'\n"
        '{ "monthly_income_range": "3000", ... }\n\n'
        "Message: 'actually I make closer to 4k'\n"
        '{ "monthly_income_range": "4000", ... }\n\n'
        "Message: 'I work full time and can put down 1000'\n"
        '{ "employment_status": "full_time", "down_payment_range": "1000", ... }'
    )


def build_extraction_request(message: str) -> str:
    return (
        "Extract structured lead data from this single customer message.\n"
        "Return ONLY a JSON object. No explanation.\n"
        "Return null for any field not explicitly present.\n\n"
        f"Message: {message}"
    )


def extract_lead_updates(message: str) -> dict[str, str | None]:
    structured = generate_structured_model(
        system_prompt=build_extraction_system_prompt(),
        request_text=build_extraction_request(message),
        schema=LeadExtractionResult,
    )
    updates = _coerce_extraction_result(structured)

    if not updates:
        raw_output = generate_structured_output(
            system_prompt=build_extraction_system_prompt(),
            request_text=build_extraction_request(message),
        )
        updates = _coerce_extraction_result(raw_output)

    if not updates:
        return _empty_updates()

    return {
        "name": _normalize_name(updates.name),
        "phone": _normalize_phone(updates.phone),
        "employment_status": _normalize_employment_status(updates.employment_status),
        "monthly_income_range": _normalize_amount(updates.monthly_income_range),
        "down_payment_range": _normalize_amount(updates.down_payment_range),
        "timeline": _normalize_timeline(updates.timeline),
    }
