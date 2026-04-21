import re


EMPLOYMENT_PATTERNS = [
    (re.compile(r"\bfull[-\s]?time\b", re.IGNORECASE), "full time"),
    (re.compile(r"\bpart[-\s]?time\b", re.IGNORECASE), "part time"),
    (re.compile(r"\bself[-\s]?employed\b", re.IGNORECASE), "self employed"),
    (re.compile(r"\bunemployed\b", re.IGNORECASE), "unemployed"),
]

PHONE_PATTERN = re.compile(r"(?:\+?\d[\d\s\-()]{7,}\d)")
AMOUNT_PATTERN = re.compile(r"\b\$?\d{3,5}(?:,\d{3})?(?:\.\d+)?k?\b", re.IGNORECASE)

INCOME_CONTEXT = {"income", "monthly", "salary", "make", "earn", "paycheck", "month"}
DOWNPAYMENT_CONTEXT = {"down", "downpayment", "down-payment", "cash", "put", "putting", "deposit"}



def _normalize_amount(raw: str) -> int | None:
    cleaned = raw.lower().replace("$", "").replace(",", "").strip()
    if not cleaned:
        return None
    multiplier = 1000 if cleaned.endswith("k") else 1
    numeric_part = cleaned[:-1] if cleaned.endswith("k") else cleaned
    try:
        value = float(numeric_part)
    except ValueError:
        return None
    return int(value * multiplier)



def _bucket_income(amount: int) -> str:
    if amount <= 2000:
        return "1000-2000"
    if amount <= 4000:
        return "2500-4000"
    return "4500-6000"



def _bucket_down_payment(amount: int) -> str:
    if amount <= 1000:
        return "500-1000"
    if amount <= 1500:
        return "1000-1500"
    return "2000-3000"



def _token_window(text: str, start: int, end: int) -> str:
    left = max(0, start - 40)
    right = min(len(text), end + 40)
    return text[left:right]



def _extract_financial_ranges(text: str) -> dict[str, str]:
    updates: dict[str, str] = {}
    for match in AMOUNT_PATTERN.finditer(text):
        amount = _normalize_amount(match.group(0))
        if amount is None:
            continue

        window = _token_window(text, match.start(), match.end())
        has_income_context = any(token in window for token in INCOME_CONTEXT)
        has_down_context = any(token in window for token in DOWNPAYMENT_CONTEXT)

        if has_income_context and "monthly_income_range" not in updates:
            updates["monthly_income_range"] = _bucket_income(amount)
            continue

        if has_down_context and "down_payment_range" not in updates:
            updates["down_payment_range"] = _bucket_down_payment(amount)
            continue

        if "monthly_income_range" not in updates:
            updates["monthly_income_range"] = _bucket_income(amount)
        elif "down_payment_range" not in updates:
            updates["down_payment_range"] = _bucket_down_payment(amount)

    return updates



def _extract_timeline(text: str) -> str | None:
    if "today" in text or "this week" in text:
        return "this_week"
    if "few days" in text or "within few days" in text or "in a few days" in text:
        return "within_few_days"
    if "this month" in text:
        return "this_month"
    if "next month" in text:
        return "next_month"
    return None



def _extract_name(text: str) -> str | None:
    match = re.search(r"\b(?:i am|i'm|my name is)\s+([a-zA-Z][a-zA-Z\s]{1,40})", text, re.IGNORECASE)
    if not match:
        return None
    candidate = match.group(1).strip(" .,!?")
    parts = [part.capitalize() for part in candidate.split() if part]
    return " ".join(parts) if parts else None



def _extract_phone(text: str) -> str | None:
    match = PHONE_PATTERN.search(text)
    if not match:
        return None
    phone = re.sub(r"\s+", "", match.group(0))
    return phone



def extract_lead_updates(message: str) -> dict[str, str]:
    text = message.lower()
    updates: dict[str, str] = {}

    for pattern, value in EMPLOYMENT_PATTERNS:
        if pattern.search(text):
            updates["employment_status"] = value
            break

    updates.update(_extract_financial_ranges(text))

    timeline = _extract_timeline(text)
    if timeline:
        updates["timeline"] = timeline

    name = _extract_name(message)
    if name:
        updates["name"] = name

    phone = _extract_phone(message)
    if phone:
        updates["phone"] = phone

    return updates
