from app.models.entities import Conversation, Dealership, Lead


def build_assistant_display_name(dealership_name: str) -> str:
    return f"{dealership_name} Assistant"


def build_lead_snapshot(lead: Lead | None) -> dict[str, str | None]:
    return {
        "name": lead.name if lead else None,
        "phone": lead.phone if lead else None,
        "employment_status": lead.employment_status if lead else None,
        "monthly_income_range": lead.monthly_income_range if lead else None,
        "down_payment_range": lead.down_payment_range if lead else None,
        "timeline": lead.timeline if lead else None,
        "intent_score": lead.intent_score if lead else "warm",
    }


def build_language_instruction(language: str) -> str:
    return "Respond in Spanish." if language.lower() == "spanish" else "Respond in English."


def build_system_prompt(
    dealership: Dealership,
    conversation: Conversation,
    lead: Lead | None,
) -> str:
    lead_snapshot = build_lead_snapshot(lead)
    assistant_name = build_assistant_display_name(dealership.name)
    language_instruction = build_language_instruction(conversation.language)
    return (
        f"You are {assistant_name}, a concise dealership assistant for BHPH financing leads. "
        "Never promise approval. Be helpful and non-pushy. Ask one qualifying question at most per response. "
        f"Dealership context: id={dealership.id}, name={dealership.name}, slug={dealership.slug}. "
        f"Conversation stage: {conversation.stage}. "
        f"Known lead state: {lead_snapshot}. "
        f"{language_instruction}"
    )


def build_greeting_request_prompt(language: str) -> str:
    if language.lower() == "spanish":
        return (
            "Escribe un saludo inicial corto para un nuevo cliente potencial. "
            "Menciona que puedes ayudar con financiamiento BHPH y haz una sola pregunta de calificacion."
        )
    return (
        "Write a short opening greeting for a new lead. "
        "Mention that you can help with BHPH financing and ask one qualifying question."
    )
