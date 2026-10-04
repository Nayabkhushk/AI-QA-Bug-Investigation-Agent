---
document_id: TC-AUTH-001
document_type: TestCase
module: Authentication
priority: High
status: Active
tags: [test-case, auth, login, credentials, validation]
---

# TC-AUTH-001: Standard User Login & Credential Validation

## Preconditions
- Active user `agent.smith@callflow.io` with known password.
- Suspended user `agent.inactive@callflow.io`.

## Test Steps
1. Navigate to CallFlow CRM login screen.
2. Enter valid credentials for `agent.smith@callflow.io` and click "Sign In".
3. Verify successful authentication, redirection to dashboard, and storage of JWT access token.
4. Enter incorrect password for `agent.smith@callflow.io`. Verify error message "Invalid email or password" and HTTP 401 response.
5. Attempt login with suspended account `agent.inactive@callflow.io`. Verify message "Account is suspended. Contact your administrator."
