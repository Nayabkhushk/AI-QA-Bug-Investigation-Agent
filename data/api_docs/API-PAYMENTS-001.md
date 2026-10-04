---
document_id: API-PAYMENTS-001
document_type: ApiDocumentation
module: Payments
priority: Critical
status: Active
tags: [api, payments, billing, stripe, webhooks, idempotency]
---

# Billing & Stripe Webhook Integration API Reference

## Base URL
`https://api.callflowcrm.com/v1/billing`

## Endpoints

### 1. `POST /webhook`
Receives asynchronous event payloads from Stripe.
- **Headers**:
  - `Stripe-Signature`: cryptographic signature header for HMAC validation.
- **Handling**:
  - Validates webhook signature using Stripe webhook secret.
  - Extracts `event.id` and verifies uniqueness against `billing_webhook_events`.
  - Dispatches internal background jobs for `invoice.payment_succeeded` or `invoice.payment_failed`.
- **Response**: `200 OK` with `{"received": true}`.

### 2. `GET /tenants/{tenant_id}/subscription`
Fetches subscription tier, active seat count, current billing cycle, and invoice history.
