import re


INCOME_PATTERNS = [
    (re.compile(r"\b(1k|1000|1500|2000)\b", re.IGNORECASE), "1000-2000"),
    (re.compile(r"\b(2500|3000|3500|4000)\b", re.IGNORECASE), "2500-4000"),
    (re.compile(r"\b(4500|5000|5500|6000)\b", re.IGNORECASE), "4500-6000"),
]

DOWN_PATTERNS = [
    (re.compile(r"\b(500|700|800)\b", re.IGNORECASE), "500-1000"),
    (re.compile(r"\b(1000|1200|1500)\b", re.IGNORECASE), "1000-1500"),
    (re.compile(r"\b(2000|2500|3000)\b", re.IGNORECASE), "2000-3000"),
]


def extract_lead_updates(message: str) -> dict[str, str]:
    text = message.lower()
    updates: dict[str, str] = {}

    if "full time" in text or "full-time" in text:
        updates["employment_status"] = "full_time"
    elif "part time" in text or "part-time" in text:
        updates["employment_status"] = "part_time"
    elif "self employed" in text or "self-employed" in text:
        updates["employment_status"] = "self_employed"
    elif "unemployed" in text:
        updates["employment_status"] = "unemployed"

    for pattern, value in INCOME_PATTERNS:
        if pattern.search(text):
            updates["monthly_income_range"] = value
            break

    for pattern, value in DOWN_PATTERNS:
        if pattern.search(text):
            updates["down_payment_range"] = value
            break

    if "today" in text or "this week" in text:
        updates["timeline"] = "this_week"
    elif "this month" in text:
        updates["timeline"] = "this_month"
    elif "next month" in text:
        updates["timeline"] = "next_month"

    return updates

