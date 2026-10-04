---
document_id: CALL-REQ-001
document_type: Requirement
module: Calls
priority: High
status: Active
tags: [telephony, webrtc, softphone, inbound-calls, call-recording]
---

# Inbound & Outbound Telephony Call Handling Requirements

## 1. Overview
CallFlow CRM provides an integrated WebRTC softphone in the browser interface, enabling CRM support agents to place outbound calls and receive inbound phone calls routed from Twilio SIP trunks.

## 2. Technical Requirements
1. **WebRTC Signaling**:
   - The browser softphone client must maintain a bidirectional WebSocket connection to `wss://sip.callflowcrm.com/ws`.
   - Incoming call offers (SDP INVITE) must ring in the agent UI within 500ms of carrier notification.
2. **Audio Streams & Codecs**:
   - Supported audio codecs are Opus (primary, 48kHz) and G.711 PCMU/PCMA (fallback).
   - Microphone access permissions must be verified on initial application load. If blocked, an error banner must notify the agent.
3. **Call Recording**:
   - Dual-channel call recording must capture the customer on channel 0 and the agent on channel 1.
   - When an agent toggles "Mute" or "Hold", recording must continue silence frames rather than terminating the audio stream.
