---
document_id: API-TICKETS-001
document_type: ApiDocumentation
module: Tickets
priority: High
status: Active
tags: [api, tickets, assignment, capacity, workflow]
---

# Support Ticket Engine API Reference

## Base URL
`https://api.callflowcrm.com/v1/tickets`

## Endpoints

### 1. `POST /tickets`
Creates a new support ticket.
- **Request Body**:
  ```json
  {
    "title": "Unable to export monthly call report",
    "description": "Export crashes when selecting date range larger than 30 days.",
    "customer_id": "cust_551",
    "priority": "P2",
    "category": "technical_support"
  }
  ```

### 2. `PUT /tickets/{ticket_id}/assign`
Assigns or reassigns an existing ticket to an agent.
- **Request Body**:
  ```json
  {
    "agent_id": "usr_772",
    "force_override": false
  }
  ```
- **Error Response `409 Conflict`**: Returned if agent has reached maximum capacity (`max_tickets`), unless `force_override: true` is explicitly provided.
