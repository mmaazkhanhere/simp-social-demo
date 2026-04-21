from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Dealership


def get_dealership_by_slug(db: Session, slug: str) -> Dealership:
    dealership = db.scalar(select(Dealership).where(Dealership.slug == slug, Dealership.is_active.is_(True)))
    if not dealership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown dealership slug: {slug}")
    return dealership


def get_dealership_by_id(db: Session, dealership_id: int) -> Dealership:
    dealership = db.get(Dealership, dealership_id)
    if not dealership or not dealership.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown dealership id: {dealership_id}")
    return dealership


def list_dealerships(db: Session) -> list[Dealership]:
    return list(db.scalars(select(Dealership).where(Dealership.is_active.is_(True)).order_by(Dealership.id)))

