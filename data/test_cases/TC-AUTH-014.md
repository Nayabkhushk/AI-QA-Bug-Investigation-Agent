---
document_id: TC-AUTH-014
document_type: TestCase
module: Authentication
priority: Critical
status: Active
tags: [test-case, auth, password-reset, session-invalidation, multi-device]
---

# TC-AUTH-014: Password Reset, Session Revocation, and Re-Authentication Test

## Preconditions
- Test user account `qa.tester@callflow.io` exists in active status.
- User has active sessions logged in across two devices: Device A (Chrome on Windows) and Device B (Mobile Safari).

## Test Steps
1. **Reset password**:
   - Request password reset for `qa.tester@callflow.io` from the login screen.
   - Open reset link received via email and submit a new compliant password: `NewTestPassword789!`.
2. **Login with new password**:
   - Navigate to CallFlow CRM login page on Device A.
   - Enter `qa.tester@callflow.io` and `NewTestPassword789!`.
   - Verify login succeeds and dashboard loads with valid JWT token.
3. **Try old password**:
   - Open an incognito browser window.
   - Attempt login with `qa.tester@callflow.io` and the prior password.
   - Verify login fails with `401 Unauthorized` and message "Invalid email or password".
4. **Verify active sessions**:
   - Switch to Device B (which had an active session before the reset).
   - Perform an action that sends an authenticated API request (e.g., refresh ticket list).
   - Verify previous session is invalidated: API returns `401 Unauthorized` and client redirects to login screen.
5. **Test from another device**:
   - On Device B, log in using the new password `NewTestPassword789!`.
   - Verify authentication succeeds without token collision or cache lock.

## Expected Results
- Password is successfully updated in PostgreSQL.
- User's `token_version` is incremented.
- All pre-existing sessions in Redis are purged.
- Logins with new password succeed immediately across all devices.
