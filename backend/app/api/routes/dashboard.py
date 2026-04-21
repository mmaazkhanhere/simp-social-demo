from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dashboard import (
    ConversationRow,
    DashboardSummaryResponse,
    DealershipDashboardResponse,
    DealershipRollup,
    LeadRow,
    NotificationRow,
    UserRow,
)
from app.services.dashboard_service import (
    aggregate_metrics,
    dealership_conversation_rows,
    dealership_lead_rows,
    dealership_metrics,
    dealership_notification_rows,
    dealership_rollups,
    dealership_user_rows,
)

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


@router.get("/{dealership_id}/leads", response_model=list[LeadRow])
def dealership_leads(dealership_id: int, db: Session = Depends(get_db)) -> list[LeadRow]:
    return dealership_lead_rows(db, dealership_id)


@router.get("/{dealership_id}/conversations", response_model=list[ConversationRow])
def dealership_conversations(dealership_id: int, db: Session = Depends(get_db)) -> list[ConversationRow]:
    return dealership_conversation_rows(db, dealership_id)


@router.get("/{dealership_id}/notifications", response_model=list[NotificationRow])
def dealership_notifications(dealership_id: int, db: Session = Depends(get_db)) -> list[NotificationRow]:
    return dealership_notification_rows(db, dealership_id)


@router.get("/{dealership_id}/users", response_model=list[UserRow])
def dealership_users(dealership_id: int, db: Session = Depends(get_db)) -> list[UserRow]:
    return dealership_user_rows(db, dealership_id)
