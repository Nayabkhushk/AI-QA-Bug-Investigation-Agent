---
document_id: TC-PAY-005
document_type: TestCase
module: Payments
priority: High
status: Active
tags: [test-case, payments, stripe, retry-schedule, dunning]
---

# TC-PAY-005: Stripe Subscription Renewal & Failed Charge Retries

## Preconditions
- Tenant `tenant_corp_10` on Professional Tier with attached expired payment method.

## Test Steps
1. Simulate Stripe webhook `invoice.payment_failed` for billing cycle renewal.
2. Verify backend marks subscription status as `Grace Period` and sets `grace_period_end` to +7 days.
3. Verify tenant admin receives email alert: "Action Required: Payment method update needed".
4. Update payment method via UI with valid test card.
5. Trigger manual charge retry endpoint `POST /api/v1/billing/invoices/{id}/pay`.
6. Verify Stripe returns `charge.succeeded` and subscription status transitions back to `Active`.
