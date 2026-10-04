---
document_id: AUTH-REQ-002
document_type: Requirement
module: Authentication
priority: Critical
status: Active
tags: [auth, password-reset, token-invalidation, redis, session-lifecycle]
---

# Password Reset & Session Invalidation Requirements

## 1. Overview
When a user updates or resets their password in CallFlow CRM, all existing active sessions, refresh tokens, and cached authentication states must be immediately invalidated across all devices to prevent unauthorized access.

## 2. Password Reset Lifecycle
1. **Reset Request**:
   - The user requests a password reset via `POST /api/v1/auth/password-reset/request`.
   - The system generates a cryptographically secure, single-use reset token with a 15-minute time-to-live (TTL) and emails a link to the registered address.
2. **Password Update**:
   - The user posts the reset token and new password to `POST /api/v1/auth/password-reset/confirm`.
   - The auth service updates the password hash in Postgres.
3. **Mandatory Token Invalidation**:
   - **Token Version Increment**: The authentication service MUST increment the user's `token_version` in the database and flush all matching Redis session keys (`session:{user_id}:*`).
   - **Revocation Broadcast**: A message must be published to the Redis pub/sub channel `auth:revocations` so all running gateway pods purge locally cached token validations.
   - **Subsequent Logins**: The user must immediately be able to log in using the newly created password. Old passwords and old session tokens must be rejected with `HTTP 401 Unauthorized`.
