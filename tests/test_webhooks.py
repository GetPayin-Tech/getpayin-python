import json
import unittest

from getpayin import GetpayinClient
from getpayin.errors import GetpayinError, GetpayinSignatureError
from getpayin.signature import build_signature
from getpayin.types import WebhookEventType

HASH = "test_hash_token_abc123"


def _signed(payload: dict, hash_token: str = HASH) -> dict:
    values = [
        str(payload.get("success", "")),
        str(payload.get("invoice_id", "")),
        str(payload.get("invoice_status", "")),
        "" if payload.get("message") is None else str(payload.get("message")),
    ]
    for key in ("mandate_id", "external_reference", "subscription_status"):
        if key in payload:
            values.append("" if payload[key] is None else str(payload[key]))
    return dict(payload, signature=build_signature(values, hash_token))


def _signed_card_token(payload: dict, hash_token: str = HASH) -> dict:
    """Sign a card-token payload the way the server signs one.

    The tokenisation block follows the always-signed four, and
    ``external_reference`` sits after ``tokenization_id`` rather than in the slot
    a mandate gives it.
    """
    keys = ["success", "invoice_id", "invoice_status", "message"]
    keys += [
        key
        for key in (
            "tokenization_id",
            "external_reference",
            "card_token",
            "card_brand",
            "card_last4",
            "card_exp_month",
            "card_exp_year",
        )
        if key in payload
    ]
    values = ["" if payload.get(key) is None else str(payload.get(key)) for key in keys]
    return dict(payload, signature=build_signature(values, hash_token))


CARD_TOKEN_CREATED = {
    "event": "card_token.created",
    "success": 1,
    "invoice_id": 7781,
    "invoice_status": "REVERSED",
    "message": "Card stored for future payments.",
    "tokenization_id": "TKZ-4f21",
    "external_reference": "cust-42",
    "card_token": "CRD-9a07",
    "card_brand": "VISA",
    "card_last4": "4242",
    "card_exp_month": "12",
    "card_exp_year": "2029",
}

class WebhooksTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = GetpayinClient(public_token="p", hash_token=HASH)

    def test_verify_valid_invoice_paid(self) -> None:
        payload = _signed(
            {"event": "invoice.paid", "success": 1, "invoice_id": 123, "invoice_status": "PAID", "message": None}
        )
        event = self.client.webhooks.verify(payload)
        self.assertEqual(event.event, "invoice.paid")
        self.assertTrue(event.success)
        self.assertEqual(event.invoice_id, 123)
        self.assertIsNone(event.message)

    def test_verify_accepts_json_string_and_bytes(self) -> None:
        payload = _signed(
            {"event": "invoice.paid", "success": 1, "invoice_id": 1, "invoice_status": "PAID", "message": "ok"}
        )
        self.assertTrue(self.client.webhooks.is_valid(json.dumps(payload)))
        self.assertTrue(self.client.webhooks.is_valid(json.dumps(payload).encode()))

    def test_subscription_optional_fields_are_signed(self) -> None:
        payload = _signed(
            {
                "event": "subscription.charged",
                "success": 1,
                "invoice_id": 555,
                "invoice_status": "PAID",
                "message": "ok",
                "auth_code": "A1",
                "mandate_id": "M-1",
                "external_reference": "sub_1",
                "subscription_status": "active",
            }
        )
        event = self.client.webhooks.verify(payload)
        self.assertEqual(event.mandate_id, "M-1")
        self.assertEqual(event.subscription_status, "active")
        self.assertEqual(event.auth_code, "A1")

    def test_tampered_payload_rejected(self) -> None:
        payload = _signed(
            {"event": "invoice.paid", "success": 1, "invoice_id": 1, "invoice_status": "PAID", "message": "ok"}
        )
        tampered = dict(payload, invoice_status="UNPAID")
        self.assertFalse(self.client.webhooks.is_valid(tampered))
        with self.assertRaises(GetpayinSignatureError):
            self.client.webhooks.verify(tampered)

    def test_missing_signature_raises(self) -> None:
        with self.assertRaises(GetpayinSignatureError):
            self.client.webhooks.verify(
                {"event": "invoice.paid", "success": 1, "invoice_id": 1, "invoice_status": "PAID"}
            )

    def test_hash_token_override(self) -> None:
        payload = _signed(
            {"event": "invoice.paid", "success": 1, "invoice_id": 9, "invoice_status": "PAID", "message": "ok"},
            hash_token="other_secret",
        )
        # Default client hashToken does not match.
        self.assertFalse(self.client.webhooks.is_valid(payload))
        # Overriding with the correct secret verifies.
        self.assertTrue(self.client.webhooks.is_valid(payload, hash_token="other_secret"))

    def test_invalid_json_raises_getpayin_error(self) -> None:
        with self.assertRaises(GetpayinError):
            self.client.webhooks.verify("{not json")

    def test_card_token_created_exposes_the_saved_card(self) -> None:
        event = self.client.webhooks.verify(_signed_card_token(CARD_TOKEN_CREATED))

        self.assertEqual(event.event, WebhookEventType.CARD_TOKEN_CREATED)
        self.assertEqual(event.tokenization_id, "TKZ-4f21")
        self.assertEqual(event.card_token, "CRD-9a07")
        self.assertEqual(event.card_brand, "VISA")
        self.assertEqual(event.card_last4, "4242")
        self.assertEqual(event.card_exp_month, "12")
        self.assertEqual(event.card_exp_year, "2029")
        self.assertEqual(event.external_reference, "cust-42")

    def test_card_token_failed_carries_no_card(self) -> None:
        payload = _signed_card_token(
            {
                "event": "card_token.failed",
                "success": 0,
                "invoice_id": 7782,
                "invoice_status": "UNPAID",
                "message": "The card could not be stored for future payments.",
                "tokenization_id": "TKZ-4f22",
                "external_reference": "cust-43",
            }
        )
        event = self.client.webhooks.verify(payload)

        self.assertEqual(event.event, WebhookEventType.CARD_TOKEN_FAILED)
        self.assertFalse(event.success)
        self.assertEqual(event.tokenization_id, "TKZ-4f22")
        self.assertIsNone(event.card_token)

    def test_tampered_card_is_rejected(self) -> None:
        payload = _signed_card_token(CARD_TOKEN_CREATED)
        payload["card_last4"] = "1111"

        self.assertFalse(self.client.webhooks.is_valid(payload))

    def test_external_reference_is_not_signed_in_the_mandate_slot(self) -> None:
        payload = _signed_card_token(CARD_TOKEN_CREATED)
        mandate_order = [
            "1",
            "7781",
            "REVERSED",
            "Card stored for future payments.",
            "cust-42",
            "TKZ-4f21",
            "CRD-9a07",
            "VISA",
            "4242",
            "12",
            "2029",
        ]

        self.assertNotEqual(payload["signature"], build_signature(mandate_order, HASH))
        self.assertTrue(self.client.webhooks.is_valid(payload))


if __name__ == "__main__":
    unittest.main()
