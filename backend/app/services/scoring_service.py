from collections.abc import Sequence
from dataclasses import dataclass

from app.models.entities import Lead, LeadScore
from app.prompt import (
    build_intent_classifier_request,
    build_intent_classifier_system_prompt,
    build_lead_snapshot,
)
from app.services.llm_service import generate_structured_output


@dataclass
class IntentClassification:
    intent_score: str
    is_willing: bool


def _filled_fields_count(lead: Lead | None) -> int:
    if not lead:
        return 0
    fields = [
        lead.employment_status,
        lead.monthly_income_range,
        lead.down_payment_range,
        lead.timeline,
    ]
    return len([field for field in fields if field])



def _heuristic_willingness(text: str) -> bool:
    return any(
        token in text
        for token in [
            "apply",
            "application",
            "ready",
            "start now",
            "move forward",
            "submit",
            "prequalify",
            "pre-qualify",
            "go ahead",
            "proceed",
            "complete application",
            "completed application",
            "done with application",
        ]
    )



def _fallback_classification(lead: Lead | None, latest_user_message: str) -> IntentClassification:
    text = latest_user_message.lower()
    filled = _filled_fields_count(lead)
    willingness = _heuristic_willingness(text)
    deflection = any(token in text for token in ["just looking", "not now", "later", "busy", "not interested"])

    if lead and lead.intent_score == LeadScore.HOT.value and not deflection:
        return IntentClassification(intent_score=LeadScore.HOT.value, is_willing=willingness or True)

    if willingness and filled >= 3:
        return IntentClassification(intent_score=LeadScore.HOT.value, is_willing=True)
    if willingness:
        return IntentClassification(intent_score=LeadScore.WARM.value, is_willing=True)
    if deflection and filled <= 1:
        return IntentClassification(intent_score=LeadScore.COLD.value, is_willing=False)
    return IntentClassification(intent_score=LeadScore.WARM.value, is_willing=False)



def classify_intent(
    lead: Lead | None,
    latest_user_message: str,
    history: Sequence[dict[str, str]],
    language: str,
) -> IntentClassification:
    fallback = _fallback_classification(lead, latest_user_message)

    system_prompt = build_intent_classifier_system_prompt(language)
    lead_snapshot = build_lead_snapshot(lead)
    request_text = build_intent_classifier_request(
        latest_user_message=latest_user_message,
        lead_snapshot=lead_snapshot,
        history=list(history),
    )
    structured = generate_structured_output(system_prompt=system_prompt, request_text=request_text)
    if not structured:
        return fallback

    intent_score = str(structured.get("intent_score", "")).strip().lower()
    if intent_score not in {LeadScore.HOT.value, LeadScore.WARM.value, LeadScore.COLD.value}:
        return fallback

    willing_raw = structured.get("is_willing", fallback.is_willing)
    if isinstance(willing_raw, bool):
        is_willing = willing_raw
    elif isinstance(willing_raw, str):
        is_willing = willing_raw.strip().lower() in {"true", "yes", "1"}
    else:
        is_willing = fallback.is_willing

    is_willing = is_willing or _heuristic_willingness(latest_user_message.lower())
    if is_willing and intent_score == LeadScore.COLD.value:
        intent_score = LeadScore.WARM.value

    if lead and lead.intent_score == LeadScore.HOT.value and intent_score != LeadScore.COLD.value:
        intent_score = LeadScore.HOT.value

    return IntentClassification(intent_score=intent_score, is_willing=is_willing)



def compute_score(
    lead: Lead | None,
    latest_user_message: str,
    history: Sequence[dict[str, str]],
    language: str,
) -> IntentClassification:
    return classify_intent(
        lead=lead,
        latest_user_message=latest_user_message,
        history=history,
        language=language,
    )



def is_application_ready(lead: Lead, willingness: bool) -> bool:
    filled = _filled_fields_count(lead)
    return lead.intent_score == LeadScore.HOT.value and filled >= 3 and willingness
