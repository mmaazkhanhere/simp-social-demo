from app.models.entities import Lead, LeadScore


def _filled_fields_count(lead: Lead) -> int:
    fields = [
        lead.employment_status,
        lead.monthly_income_range,
        lead.down_payment_range,
        lead.timeline,
    ]
    return len([field for field in fields if field])


def compute_score(lead: Lead, latest_user_message: str) -> str:
    text = latest_user_message.lower()
    filled = _filled_fields_count(lead)
    willingness = any(token in text for token in ["apply", "ready", "today", "start now"])
    deflection = any(token in text for token in ["just looking", "not now", "later", "busy"])

    if willingness and filled >= 3:
        return LeadScore.HOT.value
    if deflection and filled <= 1:
        return LeadScore.COLD.value
    return LeadScore.WARM.value


def is_application_ready(lead: Lead, latest_user_message: str) -> bool:
    text = latest_user_message.lower()
    filled = _filled_fields_count(lead)
    willing = any(token in text for token in ["apply", "ready", "start now", "i can do it"])
    return lead.intent_score == LeadScore.HOT.value and filled >= 3 and willing

