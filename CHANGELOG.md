# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-11-18

### Fixed

- `webhooks.verify()` now accepts `card_token.created` and `card_token.failed`. Both carry the
  tokenisation and the card it produced, and the server signs all of those fields; this SDK signed
  none of them, so every card-token webhook failed verification. Both events are on by default for
  every integration, so any integrator saving cards was receiving webhooks it could not verify.

### Added

- `CARD_TOKEN_CREATED` and `CARD_TOKEN_FAILED` on `WebhookEventType`.
- The saved card on `WebhookEvent`: `tokenization_id`, `card_token`, `card_brand`, `card_last4`,
  `card_exp_month` and `card_exp_year`.

## [0.2.0]

### Added

- Optional `iframe` parameter on `invoices.create` to request an embedded /
  iframe checkout. Like `payment_mode`, it is sent in the request body but
  excluded from the HMAC signature.

## [0.1.0]

### Added

- Initial release: checkouts (`invoices.create`), payment operations
  (`payments.void` / `refund` / `settle` / `reverse_authorization` /
  `check_status`), server-to-server card charges (`vcc.charge`), card
  tokenization (`cards.tokenize` / `charge` / `revoke`), recurring mandates
  (`recurring.create` / `status` / `cancel` / `pause` / `resume`), and webhook
  signature verification (`webhooks.verify` / `is_valid`).
- Order-sensitive HMAC-SHA256 request signing, proven byte-identical to the PHP
  server and the JS SDK by a shared golden-signature fixture.
- Retry with exponential backoff and full jitter for transient failures (429,
  5xx, connection errors, timeouts), honoring `Retry-After`. Only replay-safe
  requests are retried — GETs, calls carrying an `Idempotency-Key`, and pure
  reads such as `payments.check_status`. Charges are never replayed.
- Typed exception hierarchy (`GetpayinApiError` with `is_idempotency_conflict` /
  `is_rate_limited` / `is_forbidden` and `retry_after_seconds`).
- Zero runtime dependencies (standard-library transport); custom transport
  injection for proxies, pooling, or tests.
- `User-Agent: getpayin-python/<version> python/<version>` on every request.
- PEP 561 typed (`py.typed`).
