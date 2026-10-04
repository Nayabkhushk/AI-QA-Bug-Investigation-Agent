---
document_id: QA-GUIDE-002
document_type: QaGuideline
module: General
priority: High
status: Active
tags: [qa, severity, priority, classification, sla]
---

# QA-GUIDE-002: Bug Severity & Priority Matrix

## 1. Severity Levels

| Severity | Definition | Example in CallFlow CRM |
| :--- | :--- | :--- |
| **Critical (P0/P1)** | Complete system outage, data loss, security vulnerability, or revenue impact. | Inability to log in after password reset; double billing on invoices; dropped WebRTC carrier trunks. |
| **Major (P2)** | Core business feature blocked with no immediate workaround. | Ticket reassignment throwing 500 error; call recordings failing to save. |
| **Minor (P3)** | Non-critical feature failure or cosmetic defect with workaround available. | CSV export timeout on large ranges; notification badge count display issue. |
| **Trivial (P4)** | Visual misalignment, typos, minor UI cosmetic discrepancies. | Padding misalignment in account settings modal. |

## 2. Evidence Strength Assessment
- **High**: Supported by direct requirement violation, reproducible test case, and matching prior bug report.
- **Medium**: Supported by requirements and general architecture docs, but lacking exact prior bug precedent.
- **Low**: Incomplete reproduction steps or ambiguous error logs; requires further diagnostic info from user.
