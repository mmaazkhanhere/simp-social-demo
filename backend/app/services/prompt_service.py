from app.models.entities import Conversation, Dealership, Lead
from app.prompt import build_greeting_request_prompt, build_system_prompt as build_shared_system_prompt


def build_system_prompt(dealership: Dealership, conversation: Conversation, lead: Lead | None) -> str:
    return build_shared_system_prompt(dealership=dealership, conversation=conversation, lead=lead)


def build_greeting_request(language: str) -> str:
    return build_greeting_request_prompt(language)
