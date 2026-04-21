from enum import Enum

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ConversationStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class ConversationStage(str, Enum):
    NEW = "new"
    ENGAGED = "engaged"
    QUALIFYING = "qualifying"
    OBJECTION_HANDLING = "objection_handling"
    READY_TO_APPLY = "ready_to_apply"
    SUBMITTED = "submitted"
    HANDOFF_NEEDED = "handoff_needed"


class LeadScore(str, Enum):
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


class Dealership(Base, TimestampMixin):
    __tablename__ = "dealerships"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    webhook_url: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    language_default: Mapped[str] = mapped_column(String(20), default="english", nullable=False)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="dealership")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="dealership")


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("dealership_id", "phone", name="uq_contact_dealer_phone"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dealership_id: Mapped[int] = mapped_column(ForeignKey("dealerships.id"), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(20), default="english", nullable=False)

    dealership: Mapped["Dealership"] = relationship(back_populates="contacts")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="contact")


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dealership_id: Mapped[int] = mapped_column(ForeignKey("dealerships.id"), nullable=False, index=True)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), default=ConversationStatus.OPEN.value, nullable=False)
    stage: Mapped[str] = mapped_column(String(40), default=ConversationStage.NEW.value, nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="english", nullable=False)

    dealership: Mapped["Dealership"] = relationship(back_populates="conversations")
    contact: Mapped["Contact"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    leads: Mapped[list["Lead"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dealership_id: Mapped[int] = mapped_column(ForeignKey("dealerships.id"), nullable=False, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    contact_id: Mapped[int | None] = mapped_column(ForeignKey("contacts.id"), nullable=True, index=True)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    employment_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    monthly_income_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    down_payment_range: Mapped[str | None] = mapped_column(String(50), nullable=True)
    timeline: Mapped[str | None] = mapped_column(String(50), nullable=True)
    intent_score: Mapped[str] = mapped_column(String(10), default=LeadScore.WARM.value, nullable=False)
    is_application_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="leads")


class NotificationEvent(Base):
    __tablename__ = "notification_events"
    __table_args__ = (UniqueConstraint("dealership_id", "lead_id", "event_type", name="uq_notification_dedup"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dealership_id: Mapped[int] = mapped_column(ForeignKey("dealerships.id"), nullable=False, index=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(20), default="sent", nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
