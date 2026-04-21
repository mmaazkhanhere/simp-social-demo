import json

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


def build_system_prompt(dealership: Dealership, conversation: Conversation, lead: Lead | None) -> str:
    lead_snapshot = build_lead_snapshot(lead)
    assistant_name = build_assistant_display_name(dealership.name)
    language_instruction = build_language_instruction(conversation.language)

    return (
        f"You are, a concise, human SMS assistant for a Buy Here Pay Here (BHPH) dealership. "
        "Your goal is to build trust, identify financing intent, collect qualification details, and guide the customer toward a credit application. "
        "You are not appointment-focused. Be warm, natural, non-pushy, and mirror the customer's tone. "
        "Keep replies short and conversational. Ask at most one qualifying question per reply. "
        "Never sound robotic or promise approval.\n\n"

        "When interest is shown, shift into qualification mode and capture missing details naturally. "
        "Interest includes asking about financing, approval, down payment, payments, requirements, vehicles, timeline, "
        "or mentioning credit issues, income, job status, or needing a car.\n\n"

        "Track and update: name, phone, employment_status, monthly_income_range, down_payment_range, timeline, intent_score. "
        "Prioritize missing fields in this order unless context suggests otherwise: employment_status, monthly_income_range, down_payment_range, timeline. "
        "Capture name and phone when natural or needed for follow-up. Do not repeat known questions. "
        "If the customer corrects something, update immediately.\n\n"

        "Intent score: Hot = ready to apply or strong qualification signals. "
        "Warm = interested but hesitant or incomplete. "
        "Cold = browsing, vague, or disengaged. "
        "If intent is Hot or enough qualification is known, guide to the application instead of asking unnecessary extra questions.\n\n"

        "Handle objections by reducing friction and keeping momentum: just looking, bad credit, no credit pull, how much down, busy. "
        "Do not ask early for SSN, DOB, full address, or other sensitive data. "
        "Avoid long explanations, lists, and dealership jargon.\n\n"

        f"Dealership context: id={dealership.id}, name={dealership.name}, slug={dealership.slug}. "
        f"{language_instruction}"
    )



def build_greeting_request_prompt(language: str) -> str:
    if language.lower() == "spanish":
        return (
            "Escribe el PRIMER mensaje de texto para un nuevo cliente potencial de un concesionario "
            "Buy Here Pay Here (BHPH). "
            "Objetivo: generar confianza, sonar humano y empezar a precalificar sin presionar. "
            "El mensaje debe:\n"
            "- sonar como un asistente real por SMS, cálido y natural\n"
            "- ser corto (1 a 3 frases, idealmente menos de 160 caracteres si es posible)\n"
            "- mencionar que ayudas con financiamiento BHPH / opciones para crédito difícil\n"
            "- reducir fricción y escepticismo\n"
            "- NO sonar robótico, agresivo ni demasiado vendedor\n"
            "- NO pedir cita\n"
            "- NO pedir SSN, fecha de nacimiento, dirección ni otra información sensible\n"
            "- NO prometer aprobación garantizada\n"
            "- hacer exactamente UNA pregunta de calificación, fácil de responder\n"
            "- preferir una pregunta inicial sobre empleo actual o ingreso mensual estable\n"
            "- devolver solo el texto del mensaje, sin explicación ni comillas\n"
        )
    return (
        "Write the FIRST SMS-style message to a new lead for a Buy Here Pay Here (BHPH) dealership. "
        "Goal: build trust, sound human, and begin soft qualification without pressure. "
        "The message must:\n"
        "- sound like a real texting assistant, warm and natural\n"
        "- be short (1 to 3 sentences, ideally under 160 characters when possible)\n"
        "- mention that you help with BHPH financing / bad-credit-friendly options\n"
        "- reduce friction and skepticism\n"
        "- NOT sound robotic, aggressive, or overly salesy\n"
        "- NOT ask for an appointment\n"
        "- NOT ask for SSN, date of birth, address, or other sensitive personal info\n"
        "- NOT promise guaranteed approval\n"
        "- ask exactly ONE easy qualifying question\n"
        "- prefer an opening qualifier about current employment or steady monthly income\n"
        "- return only the text message, with no explanation and no quotation marks\n"
    )


def build_intent_classifier_system_prompt(language: str) -> str:
    language_instruction = build_language_instruction(language)
    return (
        "You classify user intent for a Buy Here Pay Here (BHPH) dealership conversation. "
        "Use the full context (latest message + history + known lead data).\n\n"
        
        "Intent definitions:\n"
        "- hot: ready or very close to applying/buying (clear urgency, has income/down payment, asks next steps, or agrees to proceed)\n"
        "- warm: interested but not ready (asking questions, sharing partial info, browsing, hesitant, future timeline)\n"
        "- cold: low or no buying intent (just browsing, vague, disengaged, price-only focus, or non-responsive)\n\n"
        
        "Set is_willing=true ONLY if the user shows clear willingness to proceed now (apply, move forward, or take next step).\n"
        
        "Guidelines:\n"
        "- Prioritize signals like employment, income, down payment, and timeline\n"
        "- Consider objections but do not over-penalize (credit concerns can still be warm/hot)\n"
        "- Use conversation momentum, not just the last message\n"
        "- Be conservative: if unsure between categories, choose the lower intent\n\n"
        
        "Return ONLY strict JSON with keys: intent_score, is_willing. "
        "intent_score must be one of: hot, warm, cold. "
        "No extra text, no markdown.\n"
        
        f"{language_instruction}"
    )


def build_intent_classifier_request(
    latest_user_message: str,
    lead_snapshot: dict[str, str | None],
    history: list[dict[str, str]],
) -> str:
    return (
        "Classify user intent for a BHPH financing conversation.\n"
        "Use all provided context.\n\n"
        
        f"latest_user_message: {json.dumps(latest_user_message)}\n"
        f"lead_snapshot: {json.dumps(lead_snapshot)}\n"
        f"history: {json.dumps(history)}\n\n"
        
        "Focus on:\n"
        "- readiness to apply or move forward\n"
        "- presence of qualification signals (income, job, down payment, timeline)\n"
        "- engagement level and responsiveness\n"
    )
