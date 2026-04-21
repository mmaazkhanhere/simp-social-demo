import unittest
from unittest.mock import patch

from app.services.extraction_service import (
    LEAD_UPDATE_FIELDS,
    LeadExtractionEnvelope,
    LeadExtractionResult,
    extract_lead_updates,
)


class ExtractLeadUpdatesTests(unittest.TestCase):
    def test_returns_none_for_all_fields_when_llm_returns_no_result(self) -> None:
        with patch("app.services.extraction_service.generate_structured_model", return_value=None):
            result = extract_lead_updates("Just checking inventory.")

        self.assertEqual(result, {field_name: None for field_name in LEAD_UPDATE_FIELDS})

    def test_normalizes_all_supported_fields_from_structured_output(self) -> None:
        with patch(
            "app.services.extraction_service.generate_structured_model",
            return_value=LeadExtractionEnvelope(
                updates=LeadExtractionResult(
                    name="maaz",
                    phone="+92 344 4555",
                    employment_status="full-time",
                    monthly_income_range="$3,000",
                    down_payment_range="$1,500",
                    timeline="next week",
                )
            ),
        ):
            result = extract_lead_updates("My name is Maaz and I can buy next week.")

        self.assertEqual(
            result,
            {
                "name": "maaz",
                "phone": "923444555",
                "employment_status": "full time",
                "monthly_income_range": "3000",
                "down_payment_range": "1500",
                "timeline": "next_week",
            },
        )

    def test_keeps_only_fields_present_in_structured_output(self) -> None:
        with patch(
            "app.services.extraction_service.generate_structured_model",
            return_value=LeadExtractionEnvelope(
                updates=LeadExtractionResult(
                    down_payment_range="2000",
                )
            ),
        ):
            result = extract_lead_updates("I can do 2000 down.")

        self.assertEqual(result["down_payment_range"], "2000")
        self.assertTrue(
            all(
                result[field_name] is None
                for field_name in LEAD_UPDATE_FIELDS
                if field_name != "down_payment_range"
            )
        )


if __name__ == "__main__":
    unittest.main()
