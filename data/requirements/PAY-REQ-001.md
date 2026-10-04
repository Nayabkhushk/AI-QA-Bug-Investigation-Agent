---
document_id: PAY-REQ-001
document_type: Requirement
module: Payments
priority: Critical
status: Active
tags: [billing, payments, subscriptions, stripe, invoices, webhooks]
---

# Billing & Subscription Payment Processing Requirements

## 1. Overview
CallFlow CRM bills business tenants monthly based on seat licenses and metered telephony usage. All financial transactions are processed via Stripe Connect.

## 2. Webhook & Idempotency Rules
1. **Idempotency Enforcement**:
   - All inbound payment webhooks (`invoice.payment_succeeded`, `invoice.payment_failed`, `charge.refunded`) must be checked against an idempotency table `billing_webhook_events`.
   - If an `event_id` has already been processed within the last 72 hours, the service must return `HTTP 200 OK` and ignore duplicate execution to prevent double charging.
2. **Payment Failure & Dunning**:
   - If recurring payment fails, account status transitions to `Grace Period` for 7 days.
   - Retry attempts follow an exponential backoff schedule: Day 1, Day 3, and Day 5.
   - Customer administrators must receive email and in-app banner notifications immediately upon failed charge.
