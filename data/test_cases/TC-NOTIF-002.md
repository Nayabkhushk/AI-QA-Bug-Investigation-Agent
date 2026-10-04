---
document_id: TC-NOTIF-002
document_type: TestCase
module: Notifications
priority: Medium
status: Active
tags: [test-case, notifications, websocket, real-time, bell-counter]
---

# TC-NOTIF-002: Real-Time Notification Delivery on Ticket Update

## Preconditions
- Agent is logged into the CallFlow CRM dashboard.
- WebSocket connection to `/ws/notifications` is established (`readyState == OPEN`).

## Test Steps
1. An incoming ticket `TICK-4491` is assigned to the agent by another user.
2. Verify WebSocket message `ticket_assigned` arrives in browser console.
3. Verify top navigation notification bell unread counter increments by +1 immediately without page reload.
4. Click bell icon to open notifications popover.
5. Click "Mark all as read".
6. Verify badge count resets cleanly to 0 (never negative).
