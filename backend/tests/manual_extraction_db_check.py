from pathlib import Path
import sys
from unittest.mock import patch

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.init_db import init_db
from app.db.session import SessionLocal, engine
from app.models.entities import Contact, Conversation, Lead
from app.services.contact_service import get_or_create_contact
from app.services.dealership_service import get_dealership_by_slug
from app.services.extraction_service import LeadExtractionEnvelope, LeadExtractionResult, extract_lead_updates


TEST_MESSAGE = (
    "My name is Manual Test User, my phone is 5551234567. "
    "I work full time, make 3200 a month, can put 1500 down, and want to buy next week."
)


def main() -> None:
    db = SessionLocal()
    try:
        init_db(engine, db)
        dealership = get_dealership_by_slug(db, "sunrise-auto")

        mocked_structured_output = LeadExtractionEnvelope(
            updates=LeadExtractionResult(
                name="Manual Test User",
                phone="5551234567",
                employment_status="full-time",
                monthly_income_range="3200",
                down_payment_range="1500",
                timeline="next week",
            ),
            confidence="high",
        )

        with patch(
            "app.services.extraction_service.generate_structured_model",
            return_value=mocked_structured_output,
        ):
            extracted_updates = extract_lead_updates(TEST_MESSAGE)

        contact = get_or_create_contact(
            db=db,
            dealership_id=dealership.id,
            name=extracted_updates["name"],
            phone=extracted_updates["phone"],
            preferred_language="english",
        )
        if not contact:
            raise RuntimeError("Expected contact to be created from extracted name/phone.")

        conversation = Conversation(
            dealership_id=dealership.id,
            contact_id=contact.id,
            language="english",
            stage="qualifying",
        )
        db.add(conversation)
        db.flush()

        lead = Lead(
            dealership_id=dealership.id,
            conversation_id=conversation.id,
            contact_id=contact.id,
            name=contact.name,
            phone=contact.phone,
            employment_status=extracted_updates["employment_status"],
            monthly_income_range=extracted_updates["monthly_income_range"],
            down_payment_range=extracted_updates["down_payment_range"],
            timeline=extracted_updates["timeline"],
            intent_score="hot",
            is_application_ready=False,
        )
        db.add(lead)
        db.commit()

        saved_contact = db.scalar(select(Contact).where(Contact.id == contact.id))
        saved_lead = db.scalar(select(Lead).where(Lead.id == lead.id))
        saved_conversation = db.scalar(select(Conversation).where(Conversation.id == conversation.id))

        print("Database URL:", engine.url)
        print("Message:", TEST_MESSAGE)
        print("Extracted updates:", extracted_updates)
        print("Conversation saved:", saved_conversation.id if saved_conversation else None)
        print(
            "Contact saved:",
            {
                "id": saved_contact.id if saved_contact else None,
                "dealership_id": saved_contact.dealership_id if saved_contact else None,
                "name": saved_contact.name if saved_contact else None,
                "phone": saved_contact.phone if saved_contact else None,
            },
        )
        print(
            "Lead saved:",
            {
                "id": saved_lead.id if saved_lead else None,
                "dealership_id": saved_lead.dealership_id if saved_lead else None,
                "conversation_id": saved_lead.conversation_id if saved_lead else None,
                "contact_id": saved_lead.contact_id if saved_lead else None,
                "name": saved_lead.name if saved_lead else None,
                "phone": saved_lead.phone if saved_lead else None,
                "employment_status": saved_lead.employment_status if saved_lead else None,
                "monthly_income_range": saved_lead.monthly_income_range if saved_lead else None,
                "down_payment_range": saved_lead.down_payment_range if saved_lead else None,
                "timeline": saved_lead.timeline if saved_lead else None,
                "intent_score": saved_lead.intent_score if saved_lead else None,
            },
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
