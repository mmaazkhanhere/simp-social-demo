from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Contact, Conversation, Dealership, Lead, NotificationEvent
from app.schemas.dashboard import (
    ConversationRow,
    DealershipRollup,
    LeadRow,
    NotificationRow,
    SummaryMetric,
    UserRow,
)
from app.services.dealership_service import get_dealership_by_id


def aggregate_metrics(db: Session) -> list[SummaryMetric]:
    conversations = db.scalar(select(func.count(Conversation.id))) or 0
    leads = db.scalar(select(func.count(Lead.id))) or 0
    users = db.scalar(select(func.count(Contact.id))) or 0
    notifications = db.scalar(select(func.count(NotificationEvent.id))) or 0
    return [
        SummaryMetric(label="total_conversations", value=conversations),
        SummaryMetric(label="total_leads", value=leads),
        SummaryMetric(label="total_users", value=users),
        SummaryMetric(label="total_notifications", value=notifications),
    ]


def dealership_rollups(db: Session) -> list[DealershipRollup]:
    dealerships = db.scalars(select(Dealership).order_by(Dealership.id)).all()
    results: list[DealershipRollup] = []
    for dealership in dealerships:
        conversations = db.scalar(select(func.count(Conversation.id)).where(Conversation.dealership_id == dealership.id)) or 0
        leads = db.scalar(select(func.count(Lead.id)).where(Lead.dealership_id == dealership.id)) or 0
        users = db.scalar(select(func.count(Contact.id)).where(Contact.dealership_id == dealership.id)) or 0
        results.append(
            DealershipRollup(
                dealership_id=dealership.id,
                dealership_name=dealership.name,
                conversations=conversations,
                leads=leads,
                users=users,
            )
        )
    return results


def dealership_metrics(db: Session, dealership_id: int) -> tuple[Dealership, list[SummaryMetric]]:
    dealership = get_dealership_by_id(db, dealership_id)
    conversations = db.scalar(select(func.count(Conversation.id)).where(Conversation.dealership_id == dealership.id)) or 0
    leads = db.scalar(select(func.count(Lead.id)).where(Lead.dealership_id == dealership.id)) or 0
    users = db.scalar(select(func.count(Contact.id)).where(Contact.dealership_id == dealership.id)) or 0
    hot = db.scalar(select(func.count(Lead.id)).where(Lead.dealership_id == dealership.id, Lead.intent_score == "hot")) or 0
    warm = db.scalar(select(func.count(Lead.id)).where(Lead.dealership_id == dealership.id, Lead.intent_score == "warm")) or 0
    cold = db.scalar(select(func.count(Lead.id)).where(Lead.dealership_id == dealership.id, Lead.intent_score == "cold")) or 0
    return dealership, [
        SummaryMetric(label="total_conversations", value=conversations),
        SummaryMetric(label="total_leads", value=leads),
        SummaryMetric(label="total_users", value=users),
        SummaryMetric(label="hot_leads", value=hot),
        SummaryMetric(label="warm_leads", value=warm),
        SummaryMetric(label="cold_leads", value=cold),
    ]


def dealership_lead_rows(db: Session, dealership_id: int) -> list[LeadRow]:
    rows = db.scalars(select(Lead).where(Lead.dealership_id == dealership_id).order_by(Lead.id.desc())).all()
    return [
        LeadRow(
            name=row.name or "",
            phone=row.phone or "",
            employment_status=row.employment_status or "",
            monthly_income_range=row.monthly_income_range or "",
            down_payment_range=row.down_payment_range or "",
            timeline=row.timeline or "",
            intent_score=row.intent_score or "",
        )
        for row in rows
    ]


def dealership_conversation_rows(db: Session, dealership_id: int) -> list[ConversationRow]:
    rows = db.scalars(
        select(Conversation).where(Conversation.dealership_id == dealership_id).order_by(Conversation.id.desc())
    ).all()
    return [ConversationRow(id=row.id, status=row.status, stage=row.stage, language=row.language) for row in rows]


def dealership_notification_rows(db: Session, dealership_id: int) -> list[NotificationRow]:
    rows = db.scalars(
        select(NotificationEvent)
        .where(NotificationEvent.dealership_id == dealership_id)
        .order_by(NotificationEvent.id.desc())
    ).all()
    return [
        NotificationRow(
            id=row.id,
            event_type=row.event_type,
            delivery_status=row.delivery_status,
            sent_at=row.sent_at.isoformat(),
        )
        for row in rows
    ]


def dealership_user_rows(db: Session, dealership_id: int) -> list[UserRow]:
    contacts = db.scalars(select(Contact).where(Contact.dealership_id == dealership_id).order_by(Contact.id.desc())).all()
    leads = db.scalars(select(Lead).where(Lead.dealership_id == dealership_id).order_by(Lead.id.desc())).all()

    latest_leads_by_contact_id: dict[int, Lead] = {}
    for lead in leads:
        if lead.contact_id is not None and lead.contact_id not in latest_leads_by_contact_id:
            latest_leads_by_contact_id[lead.contact_id] = lead

    return [
        UserRow(
            name=contact.name or "",
            phone=contact.phone or "",
            employment_status=(latest_leads_by_contact_id.get(contact.id).employment_status or "")
            if latest_leads_by_contact_id.get(contact.id)
            else "",
            monthly_income_range=(latest_leads_by_contact_id.get(contact.id).monthly_income_range or "")
            if latest_leads_by_contact_id.get(contact.id)
            else "",
            down_payment_range=(latest_leads_by_contact_id.get(contact.id).down_payment_range or "")
            if latest_leads_by_contact_id.get(contact.id)
            else "",
            timeline=(latest_leads_by_contact_id.get(contact.id).timeline or "")
            if latest_leads_by_contact_id.get(contact.id)
            else "",
            intent_score=(latest_leads_by_contact_id.get(contact.id).intent_score or "")
            if latest_leads_by_contact_id.get(contact.id)
            else "",
        )
        for contact in contacts
    ]
