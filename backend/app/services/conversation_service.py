from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import Contact, Conversation, Lead, Message
from app.prompt import (
    build_assistant_display_name,
    build_greeting_request_prompt,
    build_system_prompt,
)
from app.schemas.conversation import ConversationCreate
from app.services.contact_service import get_or_create_contact
from app.services.dealership_service import get_dealership_by_id
from app.services.extraction_service import extract_lead_updates
from app.services.llm_service import generate_assistant_greeting, generate_assistant_reply
from app.services.notification_service import notify_dealership
from app.services.scoring_service import IntentClassification, compute_score, is_application_ready

SUPPORTED_LANGUAGES = {"english", "spanish"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_language(language: str) -> str:
    candidate = language.lower()
    if candidate not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="language must be english or spanish")
    return candidate


def _build_history(conversation: Conversation, latest_user_message: str | None = None) -> list[dict[str, str]]:
    history = [{"role": message.role, "content": message.content} for message in conversation.messages]
    if latest_user_message is not None:
        history.append({"role": "user", "content": latest_user_message})
    return history


def _sync_contact_and_lead(
    db: Session,
    conversation: Conversation,
    lead: Lead,
    contact: Contact | None,
    updates: dict[str, str],
) -> Contact | None:
    if not contact and (updates.get("name") or updates.get("phone")):
        contact = get_or_create_contact(
            db=db,
            dealership_id=conversation.dealership_id,
            name=updates.get("name"),
            phone=updates.get("phone"),
            preferred_language=conversation.language,
        )
        if contact:
            conversation.contact_id = contact.id
            lead.contact_id = contact.id

    if contact:
        if updates.get("name") and contact.name != updates["name"]:
            contact.name = updates["name"]
        if updates.get("phone") and contact.phone != updates["phone"]:
            contact.phone = updates["phone"]

    for field_name, value in updates.items():
        setattr(lead, field_name, value)

    if contact:
        lead.name = lead.name or contact.name
        lead.phone = lead.phone or contact.phone

    return contact


def create_conversation(db: Session, payload: ConversationCreate) -> Conversation:
    dealership = get_dealership_by_id(db, payload.dealership_id)
    if dealership.name != payload.dealership_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dealership_name does not match dealership_id",
        )

    language = _validate_language(payload.language or dealership.language_default)
    contact = get_or_create_contact(db, dealership.id, payload.user_name, payload.phone, language)

    conversation = Conversation(
        dealership_id=dealership.id,
        contact_id=contact.id if contact else None,
        language=language,
    )
    db.add(conversation)
    db.flush()

    greeting_prompt = build_system_prompt(dealership=dealership, conversation=conversation, lead=None)
    assistant_name = build_assistant_display_name(dealership.name)
    greeting = generate_assistant_greeting(
        system_prompt=greeting_prompt,
        greeting_request=build_greeting_request_prompt(language),
        language=language,
        assistant_name=assistant_name,
    )
    db.add(
        Message(
            conversation_id=conversation.id,
            role="assistant",
            content=greeting,
            created_at=_now(),
        )
    )
    db.flush()
    return conversation


def _resolve_lead(
    db: Session,
    conversation: Conversation,
    lead: Lead | None,
    contact: Contact | None,
    classification: IntentClassification,
) -> Lead | None:
    if lead:
        return lead
    if not classification.is_willing:
        return None

    lead = Lead(
        dealership_id=conversation.dealership_id,
        conversation_id=conversation.id,
        contact_id=contact.id if contact else None,
        name=contact.name if contact else None,
        phone=contact.phone if contact else None,
    )
    db.add(lead)
    db.flush()
    return lead


def _collect_user_updates(history: list[dict[str, str]]) -> dict[str, str]:
    combined: dict[str, str] = {}
    for item in history:
        if item.get("role") != "user":
            continue
        message_content = item.get("content", "")
        updates = extract_lead_updates(message_content)
        for key, value in updates.items():
            combined[key] = value
    return combined


def get_conversation_scoped(db: Session, conversation_id: int, dealership_id: int) -> Conversation:
    conversation = db.scalar(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.dealership_id == dealership_id)
        .options(selectinload(Conversation.messages), selectinload(Conversation.leads), selectinload(Conversation.contact))
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found for dealership")
    return conversation


def send_message(db: Session, conversation: Conversation, content: str) -> tuple[Conversation, Message, Lead | None]:
    user_message = Message(conversation_id=conversation.id, role="user", content=content, created_at=_now())
    db.add(user_message)
    db.flush()

    lead = conversation.leads[0] if conversation.leads else None
    dealership = get_dealership_by_id(db, conversation.dealership_id)
    contact = conversation.contact
    history = _build_history(conversation, latest_user_message=content)

    classification = compute_score(
        lead=lead,
        latest_user_message=content,
        history=history,
        language=conversation.language,
    )
    lead = _resolve_lead(db=db, conversation=conversation, lead=lead, contact=contact, classification=classification)

    if lead:
        updates = _collect_user_updates(history)
        contact = _sync_contact_and_lead(db=db, conversation=conversation, lead=lead, contact=contact, updates=updates)

    prompt = build_system_prompt(dealership=dealership, conversation=conversation, lead=lead)
    assistant_text = generate_assistant_reply(prompt, history, conversation.language)
    assistant_message = Message(conversation_id=conversation.id, role="assistant", content=assistant_text, created_at=_now())
    db.add(assistant_message)

    if lead:
        final_classification = compute_score(
            lead=lead,
            latest_user_message=content,
            history=history,
            language=conversation.language,
        )
        lead.intent_score = final_classification.intent_score
        lead.is_application_ready = is_application_ready(lead, willingness=final_classification.is_willing)
        if lead.is_application_ready:
            conversation.stage = "ready_to_apply"
            notify_dealership(
                db=db,
                dealership=dealership,
                conversation=conversation,
                lead=lead,
                event_type="lead.application_ready",
                latest_message=content,
            )
        else:
            conversation.stage = "qualifying"
    else:
        conversation.stage = "engaged"

    db.flush()
    db.refresh(conversation)
    db.refresh(assistant_message)
    if lead:
        db.refresh(lead)
    return conversation, assistant_message, lead
