---
document_id: AUTH-REQ-001
document_type: Requirement
module: Authentication
priority: Critical
status: Active
tags: [auth, login, mfa, jwt, session]
---

# User Authentication & MFA Specification

## 1. Overview
CallFlow CRM requires all agent, manager, and administrator accounts to authenticate securely using email and password credentials, followed by Time-based One-Time Password (TOTP) Multi-Factor Authentication (MFA) if enabled.

## 2. Authentication Flow
1. **Initial Credential Submission**:
   - The client submits `POST /api/v1/auth/login` containing `email` and `password`.
   - The backend validates password hash using Argon2id.
   - If valid and MFA is not enforced, the service issues an HTTP-only refresh token cookie and a short-lived JSON Web Token (JWT) access token (lifetime: 15 minutes).
2. **MFA Challenge**:
   - If MFA is enabled on the account, the service responds with `HTTP 200` and `status: "mfa_required"` along with a temporary ephemeral ticket (lifetime: 5 minutes).
   - The user must submit a 6-digit TOTP code via `POST /api/v1/auth/mfa-verify`.
   - Upon successful verification, access and refresh tokens are issued.
3. **Session State**:
   - Every active session must maintain a record in the Redis session cache keyed by `session:{user_id}:{session_id}`.
   - Token payload must include `user_id`, `tenant_id`, `role`, and `token_version`.
