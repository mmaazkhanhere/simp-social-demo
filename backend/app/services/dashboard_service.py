from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Contact, Conversation, Dealership, Lead, NotificationEvent
from app.schemas.dashboard import DealershipRollup, SummaryMetric
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

