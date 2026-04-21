from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(prefix="/api/internal", tags=["internal"])


@router.post("/webhooks/lead-ready")
def lead_ready_webhook(payload: dict) -> dict:
    return {
        "received": True,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "event": payload.get("event"),
        "dealership_id": payload.get("dealership_id"),
    }

