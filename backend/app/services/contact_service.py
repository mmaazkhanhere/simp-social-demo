from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Contact


def get_or_create_contact(
    db: Session,
    dealership_id: int,
    name: str | None,
    phone: str | None,
    preferred_language: str,
) -> Contact | None:
    if phone:
        existing = db.scalar(select(Contact).where(Contact.dealership_id == dealership_id, Contact.phone == phone))
        if existing:
            if name and existing.name != name:
                existing.name = name
            existing.preferred_language = preferred_language
            return existing

    contact = Contact(
        dealership_id=dealership_id,
        name=name,
        phone=phone,
        preferred_language=preferred_language,
    )
    db.add(contact)
    db.flush()
    return contact
