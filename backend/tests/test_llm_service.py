import unittest

from app.services.llm_service import sanitize_customer_reply


class SanitizeCustomerReplyTests(unittest.TestCase):
    def test_removes_internal_updated_summary_lines(self) -> None:
        result = sanitize_customer_reply(
            "\n".join(
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
            )
        )

        self.assertEqual(result, "Thanks, what kind of vehicle are you looking for?")

    def test_returns_fallback_when_reply_only_contains_internal_output(self) -> None:
        result = sanitize_customer_reply("Updated:\n- intent_score: Warm")

        self.assertEqual(result, "Thanks for sharing that.")


if __name__ == "__main__":
    unittest.main()
