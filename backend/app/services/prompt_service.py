from app.models.entities import Conversation, Dealership, Lead
from app.prompt import (
    build_greeting_request_prompt,
    build_intent_classifier_request,
    build_intent_classifier_system_prompt,
    build_system_prompt as build_shared_system_prompt,
)


def build_system_prompt(dealership: Dealership, conversation: Conversation, lead: Lead | None) -> str:
    return build_shared_system_prompt(dealership=dealership, conversation=conversation, lead=lead)


def build_greeting_request(language: str) -> str:
    return build_greeting_request_prompt(language)


def build_intent_classifier_system(language: str) -> str:
    return build_intent_classifier_system_prompt(language)


def build_intent_classifier_input(
    latest_user_message: str,
    lead_snapshot: dict[str, str | None],
    history: list[dict[str, str]],
) -> str:
    return build_intent_classifier_request(
        latest_user_message=latest_user_message,
        lead_snapshot=lead_snapshot,
        history=history,
    )
