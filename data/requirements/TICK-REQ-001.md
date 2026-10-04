---
document_id: TICK-REQ-001
document_type: Requirement
module: Tickets
priority: High
status: Active
tags: [tickets, routing, sla, auto-assignment, queues]
---

# Support Ticket Lifecycle & Routing Requirements

## 1. Overview
CallFlow CRM allows tickets to be created from incoming emails, phone calls, web forms, and chat widgets. Tickets must be assigned to available agents according to skill tags and work capacity.

## 2. Assignment Rules
1. **Capacity Limits**:
   - Each support agent has a configured maximum ticket concurrency (default: 5 active tickets).
   - If an agent reaches maximum capacity, the automated assignment engine must skip the agent and assign to the next best match.
   - Manual reassignment to an agent at capacity must display a warning confirmation modal rather than throwing an unhandled exception.
2. **SLA Monitoring**:
   - Priority 1 (Urgent): 1-hour response SLA.
   - Priority 2 (High): 4-hour response SLA.
   - Priority 3 (Medium/Low): 24-hour response SLA.
   - SLA timers pause when ticket status transitions to `Pending Customer Reply`.
