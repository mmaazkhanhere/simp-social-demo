from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.dealership import DealershipRead
from app.services.dealership_service import get_dealership_by_slug, list_dealerships

router = APIRouter(prefix="/api/dealerships", tags=["dealerships"])


@router.get("", response_model=list[DealershipRead])
def get_dealerships(db: Session = Depends(get_db)) -> list[DealershipRead]:
    return [DealershipRead.model_validate(item) for item in list_dealerships(db)]


@router.get("/{slug}", response_model=DealershipRead)
def get_dealership(slug: str, db: Session = Depends(get_db)) -> DealershipRead:
    dealership = get_dealership_by_slug(db, slug)
    return DealershipRead.model_validate(dealership)

