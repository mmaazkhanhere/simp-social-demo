from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Dealership


SEED_DEALERSHIPS = [
    {
        "name": "Sunrise Auto",
        "slug": "sunrise-auto",
        "webhook_url": "http://localhost:8000/api/internal/webhooks/lead-ready",
        "language_default": "english",
    },
    {
        "name": "Budget Wheels",
        "slug": "budget-wheels",
        "webhook_url": "http://localhost:8000/api/internal/webhooks/lead-ready",
        "language_default": "english",
    },
    {
        "name": "Metro Motors",
        "slug": "metro-motors",
        "webhook_url": "http://localhost:8000/api/internal/webhooks/lead-ready",
        "language_default": "english",
    },
]


def seed_dealerships(db: Session) -> None:
    existing_slugs = set(db.scalars(select(Dealership.slug)).all())
    for record in SEED_DEALERSHIPS:
        if record["slug"] in existing_slugs:
            continue
        db.add(Dealership(**record))

