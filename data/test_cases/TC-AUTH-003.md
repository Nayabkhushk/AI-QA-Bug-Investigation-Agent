---
document_id: TC-AUTH-003
document_type: TestCase
module: Authentication
priority: High
status: Active
tags: [test-case, auth, mfa, totp, security]
---

# TC-AUTH-003: Multi-Factor Authentication Verification & Expiration

## Preconditions
- User account `manager@callflow.io` with TOTP MFA configured.

## Test Steps
1. Submit valid email and password for `manager@callflow.io`.
2. Verify system prompts for 6-digit TOTP code and returns temporary ticket.
3. Enter correct 6-digit code from authenticator app. Verify successful login.
4. Test expiration: generate challenge, wait 6 minutes (TTL is 5 minutes), enter valid code.
5. Verify system rejects expired ticket with "MFA verification session expired. Please re-authenticate."
