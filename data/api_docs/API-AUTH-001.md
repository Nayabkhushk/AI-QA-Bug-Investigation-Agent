---
document_id: API-AUTH-001
document_type: ApiDocumentation
module: Authentication
priority: High
status: Active
tags: [api, auth, login, password-reset, tokens, endpoints]
---

# Authentication & Session API Reference

## Base URL
`https://api.callflowcrm.com/v1/auth`

## Endpoints

### 1. `POST /login`
Authenticates a user with email and password.
- **Request Body**:
  ```json
  {
    "email": "agent@callflow.io",
    "password": "SecurePassword123!"
  }
  ```
- **Response `200 OK`**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": { "id": "usr_991", "email": "agent@callflow.io", "role": "agent" }
  }
  ```
- **Error `401 Unauthorized`**: Invalid credentials or invalidated session token.

### 2. `POST /password-reset/confirm`
Completes password reset flow using token from reset email.
- **Request Body**:
  ```json
  {
    "reset_token": "rst_tok_4a89bc...",
    "new_password": "NewSecretPassword456!"
  }
  ```
- **Behavior**:
  - Resets password hash in Postgres database.
  - Revokes all existing access & refresh tokens by incrementing `token_version`.
  - Deletes matching Redis session keys: `session:usr_991:*`.
- **Response `200 OK`**:
  ```json
  {
    "message": "Password updated successfully. Please log in with your new credentials."
  }
  ```

### 3. `POST /refresh`
Exchanges refresh token cookie for new access token.
- Returns `401 Unauthorized` if `token_version` in refresh token does not match active database record.
