---
document_id: API-CALLS-001
document_type: ApiDocumentation
module: Calls
priority: High
status: Active
tags: [api, telephony, webrtc, softphone, call-sessions]
---

# Telephony & Call Session API Reference

## Base URL
`https://api.callflowcrm.com/v1/calls`

## Endpoints

### 1. `POST /calls/initiate`
Initiates an outbound call from agent softphone to destination phone number.
- **Request Body**:
  ```json
  {
    "agent_id": "usr_991",
    "customer_phone": "+14155552671",
    "caller_id": "+18005550199",
    "record_audio": true
  }
  ```
- **Response `201 Created`**:
  ```json
  {
    "call_id": "call_882910",
    "status": "ringing",
    "webrtc_session_id": "sess_rtc_009a8b"
  }
  ```

### 2. `POST /calls/{call_id}/transfer`
Performs warm or blind transfer of active call to another agent or department.
- **Request Body**:
  ```json
  {
    "target_agent_id": "usr_402",
    "transfer_type": "warm",
    "announcement_message": "Transferring customer regarding billing dispute"
  }
  ```
