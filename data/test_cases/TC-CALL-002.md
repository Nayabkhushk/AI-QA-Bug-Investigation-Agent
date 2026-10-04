---
document_id: TC-CALL-002
document_type: TestCase
module: Calls
priority: High
status: Active
tags: [test-case, telephony, webrtc, softphone, inbound-audio]
---

# TC-CALL-002: Inbound Call Ringing & Softphone Pickup Flow

## Preconditions
- Agent logged into CallFlow CRM with softphone state set to "Available".
- WebRTC microphone permissions granted in browser.

## Test Steps
1. Simulate incoming call from external customer to agent's direct routing line.
2. Verify softphone widget shows incoming call dialog with caller ID within 500ms.
3. Click "Accept Call".
4. Verify WebRTC media handshake completes (`RTCPeerConnection` iceConnectionState transitions to `connected`).
5. Verify bidirectional audio stream is audible with latency < 150ms.
6. Click "End Call". Verify call duration and recording metadata are saved to call detail record (CDR).
