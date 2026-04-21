from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import Conversation, Lead, Message
from app.schemas.conversation import ConversationCreate
from app.services.contact_service import get_or_create_contact
from app.services.dealership_service import get_dealership_by_id
from app.services.extraction_service import extract_lead_updates
from app.services.llm_service import generate_assistant_reply
from app.services.notification_service import notify_dealership
from app.services.prompt_service import build_system_prompt
from app.services.scoring_service import compute_score, is_application_ready


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_language(language: str) -> str:
    candidate = language.lower()
    if candidate not in {"english", "spanish"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="language must be english or spanish")
    return candidate


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

    lead = Lead(
        dealership_id=dealership.id,
        conversation_id=conversation.id,
        contact_id=contact.id if contact else None,
        name=payload.user_name,
        phone=payload.phone,
    )
    db.add(lead)
    db.flush()
    return conversation


def get_conversation_scoped(db: Session, conversation_id: int, dealership_id: int) -> Conversation:
    conversation = db.scalar(
        select(Conversation)
        .where(Conversation.id == conversation_id, Conversation.dealership_id == dealership_id)
        .options(selectinload(Conversation.messages), selectinload(Conversation.leads))
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found for dealership")
    return conversation


def send_message(db: Session, conversation: Conversation, content: str) -> tuple[Conversation, Message, Lead]:
    user_message = Message(conversation_id=conversation.id, role="user", content=content, created_at=_now())
    db.add(user_message)
    db.flush()

    lead = conversation.leads[0] if conversation.leads else None
    if not lead:
        lead = Lead(dealership_id=conversation.dealership_id, conversation_id=conversation.id)
        db.add(lead)
        db.flush()

    updates = extract_lead_updates(content)
    for field_name, value in updates.items():
        setattr(lead, field_name, value)

    dealership = get_dealership_by_id(db, conversation.dealership_id)
    history = [{"role": m.role, "content": m.content} for m in conversation.messages]
    history.append({"role": "user", "content": content})
    prompt = build_system_prompt(dealership=dealership, conversation=conversation, lead=lead)
    assistant_text = generate_assistant_reply(prompt, history, conversation.language)
    assistant_message = Message(conversation_id=conversation.id, role="assistant", content=assistant_text, created_at=_now())
    db.add(assistant_message)

    lead.intent_score = compute_score(lead, content)
    lead.is_application_ready = is_application_ready(lead, content)
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

    db.flush()
    db.refresh(conversation)
    db.refresh(assistant_message)
    db.refresh(lead)
    return conversation, assistant_message, lead

