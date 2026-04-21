from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationRead,
    LeadRead,
    MessageCreate,
    MessageExchangeResponse,
    MessageRead,
)
from app.services.conversation_service import create_conversation, get_conversation_scoped, send_message
from app.services.dealership_service import get_dealership_by_id
from app.services.llm_service import LLMServiceError

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _raise_llm_http_error(exc: LLMServiceError) -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Assistant is temporarily unavailable. {exc}",
    ) from exc


def _to_conversation_read(conversation) -> ConversationRead:
    lead = conversation.leads[0] if conversation.leads else None
    messages = [MessageRead.model_validate(msg) for msg in sorted(conversation.messages, key=lambda item: item.id)]
    return ConversationRead(
        id=conversation.id,
        dealership_id=conversation.dealership_id,
        status=conversation.status,
        stage=conversation.stage,
        language=conversation.language,
        messages=messages,
        lead=LeadRead.model_validate(lead) if lead else None,
    )


@router.post("", response_model=ConversationRead)
def create(payload: ConversationCreate, db: Session = Depends(get_db)) -> ConversationRead:
    try:
        conversation = create_conversation(db, payload)
    except LLMServiceError as exc:
        _raise_llm_http_error(exc)
    db.commit()
    conversation = get_conversation_scoped(db, conversation.id, payload.dealership_id)
    return _to_conversation_read(conversation)


@router.get("/{conversation_id}", response_model=ConversationRead)
def get_conversation(conversation_id: int, dealership_id: int, db: Session = Depends(get_db)) -> ConversationRead:
    get_dealership_by_id(db, dealership_id)
    conversation = get_conversation_scoped(db, conversation_id, dealership_id)
    return _to_conversation_read(conversation)


@router.post("/{conversation_id}/messages", response_model=MessageExchangeResponse)
def create_message(
    conversation_id: int,
    payload: MessageCreate,
    dealership_id: int,
    db: Session = Depends(get_db),
) -> MessageExchangeResponse:
    get_dealership_by_id(db, dealership_id)
    conversation = get_conversation_scoped(db, conversation_id, dealership_id)
    if conversation.status != "open":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation is closed")
    try:
        conversation, assistant_message, lead = send_message(db, conversation, payload.content)
    except LLMServiceError as exc:
        _raise_llm_http_error(exc)
    db.commit()
    conversation = get_conversation_scoped(db, conversation.id, dealership_id)
    return MessageExchangeResponse(
        conversation=_to_conversation_read(conversation),
        assistant_message=MessageRead.model_validate(assistant_message),
        lead=LeadRead.model_validate(lead) if lead else None,
    )
