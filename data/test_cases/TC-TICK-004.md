---
document_id: TC-TICK-004
document_type: TestCase
module: Tickets
priority: High
status: Active
tags: [test-case, tickets, routing, capacity, auto-assignment]
---

# TC-TICK-004: Automated Ticket Routing & Agent Capacity Limits

## Preconditions
- Agent X has 5 active open tickets (max capacity configured = 5).
- Agent Y has 2 active open tickets (max capacity configured = 5).
- Both agents share the "Billing" skill tag.

## Test Steps
1. Create new ticket via API with category `Billing` and priority `P2`.
2. Trigger the automated routing engine.
3. Verify routing engine skips Agent X due to capacity constraint.
4. Verify ticket is automatically assigned to Agent Y.
5. In UI, attempt manual assignment of the ticket to Agent X.
6. Verify confirmation modal prompts supervisor: "Agent X is at max ticket capacity. Proceed anyway?"
