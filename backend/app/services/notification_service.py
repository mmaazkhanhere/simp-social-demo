import json
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Conversation, Dealership, Lead, NotificationEvent


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _build_payload(event_type: str, dealership: Dealership, conversation: Conversation, lead: Lead, latest_message: str) -> dict:
    return {
        "event": event_type,
        "dealership_id": dealership.id,
        "dealership_name": dealership.name,
        "lead_id": lead.id,
        "conversation_id": conversation.id,
        "score": lead.intent_score,
        "lead_data": {
            "name": lead.name,
            "phone": lead.phone,
            "employment_status": lead.employment_status,
            "monthly_income_range": lead.monthly_income_range,
            "down_payment_range": lead.down_payment_range,
            "timeline": lead.timeline,
        },
        "last_customer_message": latest_message,
    }


def notify_dealership(
    db: Session,
    dealership: Dealership,
    conversation: Conversation,
    lead: Lead,
    event_type: str,
    latest_message: str,
) -> None:
    existing = db.scalar(
        select(NotificationEvent).where(
            NotificationEvent.dealership_id == dealership.id,
            NotificationEvent.lead_id == lead.id,
            NotificationEvent.event_type == event_type,
        )
    )
    if existing:
        return

    payload = _build_payload(event_type, dealership, conversation, lead, latest_message)
    status = "sent"
    try:
        with httpx.Client(timeout=10.0) as client:
            client.post(dealership.webhook_url, json=payload)
    except Exception:
        status = "failed"

    db.add(
        NotificationEvent(
            dealership_id=dealership.id,
            conversation_id=conversation.id,
            lead_id=lead.id,
            event_type=event_type,
            payload_json=json.dumps(payload),
            delivery_status=status,
            sent_at=_now(),
        )
    )
