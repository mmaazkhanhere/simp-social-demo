from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Conversation, Lead, NotificationEvent
from app.schemas.dashboard import DashboardSummaryResponse, DealershipDashboardResponse, DealershipRollup
from app.services.dashboard_service import aggregate_metrics, dealership_metrics, dealership_rollups

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def summary(db: Session = Depends(get_db)) -> DashboardSummaryResponse:
    return DashboardSummaryResponse(metrics=aggregate_metrics(db))


@router.get("/dealerships", response_model=list[DealershipRollup])
def rollups(db: Session = Depends(get_db)) -> list[DealershipRollup]:
    return dealership_rollups(db)


@router.get("/{dealership_id}", response_model=DealershipDashboardResponse)
def dealership_summary(dealership_id: int, db: Session = Depends(get_db)) -> DealershipDashboardResponse:
    dealership, metrics = dealership_metrics(db, dealership_id)
    return DealershipDashboardResponse(dealership_id=dealership.id, dealership_name=dealership.name, metrics=metrics)


@router.get("/{dealership_id}/leads")
def dealership_leads(dealership_id: int, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(Lead).where(Lead.dealership_id == dealership_id).order_by(Lead.id.desc())).all()
    return [
        {
            "id": row.id,
            "name": row.name,
            "phone": row.phone,
            "intent_score": row.intent_score,
            "timeline": row.timeline,
        }
        for row in rows
    ]


@router.get("/{dealership_id}/conversations")
def dealership_conversations(dealership_id: int, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(
        select(Conversation).where(Conversation.dealership_id == dealership_id).order_by(Conversation.id.desc())
    ).all()
    return [{"id": row.id, "status": row.status, "stage": row.stage, "language": row.language} for row in rows]


@router.get("/{dealership_id}/notifications")
def dealership_notifications(dealership_id: int, db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(
        select(NotificationEvent)
        .where(NotificationEvent.dealership_id == dealership_id)
        .order_by(NotificationEvent.id.desc())
    ).all()
    return [
        {
            "id": row.id,
            "event_type": row.event_type,
            "delivery_status": row.delivery_status,
            "sent_at": row.sent_at.isoformat(),
        }
        for row in rows
    ]

