---
document_id: TC-CALL-008
document_type: TestCase
module: Calls
priority: Medium
status: Active
tags: [test-case, telephony, call-transfer, warm-transfer, softphone]
---

# TC-CALL-008: Warm Call Transfer Between Active Agents

## Preconditions
- Agent A is on an active call with Customer C.
- Agent B is logged in and in "Available" status.

## Test Steps
1. On Agent A's softphone, click "Transfer" and select "Warm Transfer".
2. Select Agent B from the active directory.
3. System places Customer C on hold (hold music audible).
4. System rings Agent B. Agent B accepts call.
5. Agent A briefs Agent B on customer situation via private audio channel.
6. Agent A clicks "Complete Transfer".
7. Verify Agent A is disconnected, Customer C and Agent B are bridged together, and call recording continues seamlessly.
