---
document_id: QA-GUIDE-003
document_type: QaGuideline
module: General
priority: Medium
status: Active
tags: [qa, reproduction, isolation, environments, testing-sop]
---

# QA-GUIDE-003: Bug Reproduction & Environment Isolation Guidelines

## 1. Reproduction Best Practices
1. **Isolate Environment Variables**:
   - Confirm whether the defect reproduces in Staging vs. Production.
   - Note browser version, OS, network latency, and tenant configuration flags.
2. **Clear Client Caches**:
   - Always test in both normal and clean state (incognito window, cleared localStorage, cleared cookies).
   - Verify whether issue stems from stale local JWT tokens or server-side state.
3. **Multi-Session & Multi-Device Testing**:
   - For authentication and real-time features, always test with at least two simultaneous client sessions to catch race conditions and cache invalidation flaws.
4. **Document Precise Steps**:
   - Record exact HTTP status codes, request payloads, API response bodies, and console error messages.
