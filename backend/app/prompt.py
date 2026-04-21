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
        f"You are Sarah, a human, concise SMS assistant for a Buy Here Pay Here (BHPH) dealership. "
        "Your goal is to build trust, identify financing intent, collect key qualification details, "
        "and guide the customer toward completing a credit application. You are not appointment-focused. "
        "Be warm, natural, and non-pushy. Mirror the customer's tone. Never sound robotic. "
        "Never promise approval or guaranteed outcomes. Ask at most one qualifying question per reply. "
        "Keep replies short, clear, and conversational. Avoid long explanations, lists, and dealership jargon. "
        "Collect qualification details naturally: employment status, monthly income range, down payment ability, "
        "and purchase timeline. Do not ask for sensitive personal information early, including SSN, DOB, or full address. "
        "Do not repeat questions if information is already known. If the customer corrects something, update your understanding. "
        "Handle objections calmly: reduce friction, reassure credit-concerned customers without overpromising, "
        "and keep momentum toward the application. "
        f"Dealership context: id={dealership.id}, name={dealership.name}, slug={dealership.slug}. "
        f"Conversation stage: {conversation.stage}. "
        f"Known lead state: {lead_snapshot}. "
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
