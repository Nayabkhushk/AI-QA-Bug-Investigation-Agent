---
document_id: QA-GUIDE-001
document_type: QaGuideline
module: General
priority: High
status: Active
tags: [qa, sop, investigation, root-cause, evidence, triage]
---

# QA-GUIDE-001: Bug Investigation & Root Cause Analysis SOP

## 1. Investigation Protocol
Every reported bug must be investigated systematically following these steps:
1. **Identify the Likely Module**:
   - Determine which subsystem governs the reported failure (e.g., Authentication, Telephony/Calls, Tickets, Billing).
2. **Retrieve Authoritative Requirements**:
   - Review relevant product requirements and functional specifications to establish the expected system behavior.
3. **Inspect Previous Bug Reports**:
   - Check if similar regression or edge cases have occurred before. Note recurring failure modes, especially related to caching, asynchronous queues, or token invalidation.
4. **Correlate with Test Cases**:
   - Locate test cases that cover the affected workflow. Identify gaps in test coverage (e.g., multi-device testing, session race conditions).
5. **Formulate Grounded Hypotheses**:
   - Never speculate without evidence. Categorize causes into `Confirmed`, `Likely`, `Possible`, or `Unknown`.
   - Distinguish symptoms from root causes.
