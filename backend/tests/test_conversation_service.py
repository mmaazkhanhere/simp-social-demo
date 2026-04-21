import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.init_db import init_db
from app.models import Base
from app.schemas.conversation import ConversationCreate
from app.services.conversation_service import create_conversation, send_message
from app.services.dealership_service import get_dealership_by_slug


class ConversationServiceFieldPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False)
        self.db: Session = self.session_factory()
        init_db(self.engine, self.db)
        self.dealership = get_dealership_by_slug(self.db, "sunrise-auto")

        self.greeting_patcher = patch(
            "app.services.conversation_service.generate_assistant_greeting",
            return_value="Hello, I can help with financing.",
        )
        self.reply_patcher = patch(
            "app.services.conversation_service.generate_assistant_reply",
            return_value="Thanks for that. What would you like to do next?",
        )
        self.notify_patcher = patch("app.services.conversation_service.notify_dealership")
        self.extract_patcher = patch(
            "app.services.conversation_service.extract_lead_updates",
            side_effect=self._extract_updates,
        )

        self.greeting_patcher.start()
        self.reply_patcher.start()
        self.mock_notify = self.notify_patcher.start()
        self.extract_patcher.start()

    def tearDown(self) -> None:
        self.greeting_patcher.stop()
        self.reply_patcher.stop()
        self.notify_patcher.stop()
        self.extract_patcher.stop()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    @staticmethod
    def _empty_updates() -> dict[str, str | None]:
        return {
            "name": None,
            "phone": None,
            "employment_status": None,
            "monthly_income_range": None,
            "down_payment_range": None,
            "timeline": None,
        }

    def _extract_updates(self, message: str) -> dict[str, str | None]:
        normalized = message.lower()

        if "my name is maaz" in normalized and "923444555" in normalized and "1500 down" in normalized and "next week" in normalized:
            return {
                "name": "Maaz",
                "phone": "923444555",
                "employment_status": "full time",
                "monthly_income_range": "3000",
                "down_payment_range": "1500",
                "timeline": "next_week",
            }
        if "work full time and make 3000 monthly" in normalized:
            return {
                **self._empty_updates(),
                "employment_status": "full time",
                "monthly_income_range": "3000",
            }
        if "1500 down" in normalized:
            return {
                **self._empty_updates(),
                "down_payment_range": "1500",
            }
        if "part time now" in normalized and "2500" in normalized:
            return {
                **self._empty_updates(),
                "employment_status": "part time",
                "monthly_income_range": "2500",
            }
        return self._empty_updates()

    def _create_conversation(self):
        conversation = create_conversation(
            self.db,
            ConversationCreate(
                dealership_id=self.dealership.id,
                dealership_name=self.dealership.name,
                language="english",
            ),
        )
        self.db.commit()
        return conversation

    def test_first_message_extracts_fields_and_creates_lead(self) -> None:
        conversation = self._create_conversation()

        _, _, lead = send_message(
            self.db,
            conversation,
            "My name is Maaz, phone 923444555. I work full time, make 3000 monthly, "
            "have 1500 down, and want to buy next week.",
        )

        self.assertIsNotNone(lead)
        assert lead is not None
        self.assertEqual(lead.name, "Maaz")
        self.assertEqual(lead.phone, "923444555")
        self.assertEqual(lead.employment_status, "full time")
        self.assertEqual(lead.monthly_income_range, "3000")
        self.assertEqual(lead.down_payment_range, "1500")
        self.assertEqual(lead.timeline, "next_week")
        self.assertEqual(lead.intent_score, "hot")

    def test_missing_fields_in_later_message_do_not_clear_existing_values(self) -> None:
        conversation = self._create_conversation()

        _, _, lead = send_message(
            self.db,
            conversation,
            "I work full time and make 3000 monthly.",
        )
        self.assertIsNotNone(lead)
        assert lead is not None

        _, _, updated_lead = send_message(
            self.db,
            conversation,
            "I can put 1500 down.",
        )

        self.assertIsNotNone(updated_lead)
        assert updated_lead is not None
        self.assertEqual(updated_lead.employment_status, "full time")
        self.assertEqual(updated_lead.monthly_income_range, "3000")
        self.assertEqual(updated_lead.down_payment_range, "1500")
        self.assertIsNone(updated_lead.timeline)

    def test_new_message_can_overwrite_existing_field_values(self) -> None:
        conversation = self._create_conversation()

        _, _, lead = send_message(
            self.db,
            conversation,
            "I work full time and make 3000 monthly.",
        )
        self.assertIsNotNone(lead)
        assert lead is not None

        _, _, updated_lead = send_message(
            self.db,
            conversation,
            "Actually I am part time now and I make 2500 a month.",
        )

        self.assertIsNotNone(updated_lead)
        assert updated_lead is not None
        self.assertEqual(updated_lead.employment_status, "part time")
        self.assertEqual(updated_lead.monthly_income_range, "2500")

    def test_non_qualifying_message_does_not_create_a_lead(self) -> None:
        conversation = self._create_conversation()

        _, _, lead = send_message(
            self.db,
            conversation,
            "Just looking right now.",
        )

        self.assertIsNone(lead)

    def test_ready_lead_triggers_notification_once_application_ready(self) -> None:
        conversation = self._create_conversation()

        _, _, lead = send_message(
            self.db,
            conversation,
            "My name is Maaz, phone 923444555. I work full time, make 3000 monthly, "
            "have 1500 down, want to buy next week, and I am ready to apply.",
        )

        self.assertIsNotNone(lead)
        assert lead is not None
        self.assertTrue(lead.is_application_ready)
        self.mock_notify.assert_called_once()

    def test_assistant_reply_does_not_store_internal_updated_summary(self) -> None:
        self.reply_patcher.stop()
        self.reply_patcher = patch(
            "app.services.conversation_service.generate_assistant_reply",
            return_value="\n".join(
                [
                    "**Updated:**",
                    "- name: Maaz",
                    "- phone: 923444555",
                    "- employment_status: full time",
                    "- monthly_income_range: 3000",
                    "- down_payment_range: 1500",
                    "- timeline: next week",
                    "- intent_score: Warm",
                    "Thanks, what kind of vehicle are you looking for?",
                ]
            ),
        )
        self.reply_patcher.start()

        conversation = self._create_conversation()
        updated_conversation, assistant_message, _ = send_message(
            self.db,
            conversation,
            "My name is Maaz, phone 923444555. I work full time, make 3000 monthly, have 1500 down.",
        )

        self.assertEqual(assistant_message.content, "Thanks, what kind of vehicle are you looking for?")
        self.assertEqual(updated_conversation.messages[-1].content, "Thanks, what kind of vehicle are you looking for?")


if __name__ == "__main__":
    unittest.main()
