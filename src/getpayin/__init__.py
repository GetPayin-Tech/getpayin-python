"""Official Python SDK for the GetPayIn / GetPayIn payment integration API.

Wraps every integration endpoint (checkouts, payment operations, card tokens,
recurring mandates) and computes the order-sensitive HMAC-SHA256 signatures for
you, plus webhook signature verification. Server-side only — the ``hash_token``
signing secret must never reach a browser or mobile client.
"""

from __future__ import annotations

from ._version import __version__
from .client import GetpayinClient
from .config import HttpResponse, Transport
from .errors import (
    GetpayinApiError,
    GetpayinConfigError,
    GetpayinConnectionError,
    GetpayinError,
    GetpayinSignatureError,
)
from .types import (
    CardInfo,
    ChargeTokenResult,
    CreateInvoiceResult,
    CreateRecurringResult,
    MandateActionResult,
    MandateStatusResult,
    PaymentResult,
    RefundResult,
    RevokeTokenResult,
    TokenizeCardResult,
    VccChargeResult,
    WebhookEvent,
    WebhookEventType,
)

__all__ = [
    "__version__",
    "GetpayinClient",
    "HttpResponse",
    "Transport",
    "GetpayinError",
    "GetpayinConfigError",
    "GetpayinApiError",
    "GetpayinSignatureError",
    "GetpayinConnectionError",
    "WebhookEvent",
    "WebhookEventType",
    "CreateInvoiceResult",
    "PaymentResult",
    "RefundResult",
    "VccChargeResult",
    "CardInfo",
    "TokenizeCardResult",
    "ChargeTokenResult",
    "RevokeTokenResult",
    "CreateRecurringResult",
    "MandateStatusResult",
    "MandateActionResult",
]
