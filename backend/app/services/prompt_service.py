from app.models.entities import Conversation, Dealership, Lead


def build_system_prompt(
    dealership: Dealership,
    conversation: Conversation,
    lead: Lead | None,
) -> str:
    lead_snapshot = {
        "name": lead.name if lead else None,
        "phone": lead.phone if lead else None,
        "employment_status": lead.employment_status if lead else None,
        "monthly_income_range": lead.monthly_income_range if lead else None,
        "down_payment_range": lead.down_payment_range if lead else None,
        "timeline": lead.timeline if lead else None,
        "intent_score": lead.intent_score if lead else "warm",
    }
    language = conversation.language.lower()
    language_instruction = "Respond in Spanish." if language == "spanish" else "Respond in English."

    return (
        "You are Sarah, a concise dealership assistant for BHPH financing leads. "
        "Never promise approval. Be helpful and non-pushy. Ask one qualifying question at most per response. "
        f"Dealership context: id={dealership.id}, name={dealership.name}, slug={dealership.slug}. "
        f"Conversation stage: {conversation.stage}. "
        f"Known lead state: {lead_snapshot}. "
        f"{language_instruction}"
    )

