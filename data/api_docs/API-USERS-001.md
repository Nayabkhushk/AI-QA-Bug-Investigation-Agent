---
document_id: API-USERS-001
document_type: ApiDocumentation
module: Users
priority: Medium
status: Active
tags: [api, users, roles, permissions, tenants]
---

# User Management & Roles API Reference

## Base URL
`https://api.callflowcrm.com/v1/users`

## Endpoints

### 1. `GET /users/{user_id}`
Retrieves profile, assigned skills, and role memberships.
- **Headers**: `Authorization: Bearer <access_token>`
- **Response `200 OK`**:
  ```json
  {
    "id": "usr_991",
    "name": "Alex Mercer",
    "email": "alex@callflow.io",
    "role": "support_agent",
    "skills": ["billing", "spanish", "tier2"],
    "max_tickets": 5,
    "status": "active"
  }
  ```

### 2. `PATCH /users/{user_id}/role`
Updates user roles and access permissions.
- **Request Body**:
  ```json
  {
    "role": "team_lead"
  }
  ```
- **Note**: Modifying roles triggers a security event that forces the user's current session tokens to refresh within 60 seconds.
