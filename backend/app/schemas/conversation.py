from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    dealership_id: int
    dealership_name: str
    language: str = Field(default="english")
    user_name: str | None = None
    phone: str | None = None


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageRead(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadRead(BaseModel):
    id: int
    dealership_id: int
    conversation_id: int
    name: str | None
    phone: str | None
    employment_status: str | None
    monthly_income_range: str | None
    down_payment_range: str | None
    timeline: str | None
    intent_score: str
    is_application_ready: bool

    model_config = {"from_attributes": True}


class ConversationRead(BaseModel):
    id: int
    dealership_id: int
    status: str
    stage: str
    language: str
    messages: list[MessageRead]
    lead: LeadRead | None


class MessageExchangeResponse(BaseModel):
    conversation: ConversationRead
    assistant_message: MessageRead
    lead: LeadRead | None

