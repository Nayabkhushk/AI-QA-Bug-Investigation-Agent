# AI QA & Bug Investigation Agent — MVP PRD

## 1. Goal

Build a production-style AI Agent that helps QA engineers investigate software bugs.

Example input:

> "Login fails after password reset for some users."

The system should retrieve relevant requirements, previous bugs, test cases, and API/product documentation, then use an AI agent to analyze the evidence and generate a grounded bug investigation report.

The system must prioritize **accuracy, traceability, low token usage, controlled agent behavior, and prevention of hallucinations**.

---

## 2. Core Workflow

```text
User enters bug
      ↓
Understand bug
      ↓
Agent decides what information is needed
      ↓
Hybrid RAG
(Dense Search + Keyword Search + Metadata Filters)
      ↓
Top 10 candidates
      ↓
Reranking
      ↓
Top 5 relevant sources
      ↓
Agent analyzes evidence
      ↓
Agent may call tools
      ↓
Evidence validation
      ↓
Grounded structured response
```

---

## 3. Fictional Dataset

Since no real company data is available, create a fictional CRM product called **CallFlow CRM**.

Create approximately **31 documents**:

* 5 Requirements
* 5 API/Product documentation files
* 8 Test Case documents
* 10 Previous Bug Reports
* 3 QA Guidelines

Use Markdown/JSON files initially.

Example modules:

* Authentication
* Users
* Customers
* Calls
* Tickets
* Reports
* Notifications
* Payments

Each document must contain useful metadata such as:

```text
document_id
document_type
module
priority
status
tags
```

---

## 4. RAG System

Implement:

```text
Documents
 ↓
Loader
 ↓
Cleaning
 ↓
Chunking
 ↓
Metadata
 ↓
Embeddings
 ↓
Vector Database
```

Retrieval:

```text
User Query
 ↓
Dense Vector Search
 +
Keyword/BM25 Search
 ↓
Merge Results
 ↓
Metadata Filtering
 ↓
Top 10
 ↓
Reranker
 ↓
Top 5
```

Use a simple local vector database such as **Chroma** .

---

## 5. Agent

The agent should NOT freely execute unlimited actions.

Use a controlled workflow:

```text
START
 ↓
UNDERSTAND
 ↓
RETRIEVE
 ↓
ASSESS EVIDENCE
 ↓
Need more information?
 ├── YES → Ask user
 └── NO
       ↓
     ANALYZE
       ↓
    VALIDATE
       ↓
    RESPOND
```

### MVP Agent Tools — only 3

1. `search_knowledge_base`

   * Search requirements, API docs, test cases and QA documentation.

2. `search_bugs`

   * Search previous bug reports.

3. `get_document`

   * Retrieve the complete content of a specific document.

Do not add Jira, GitHub, browser automation, Selenium, multi-agent systems, etc. in the MVP.

---

## 6. Short-Term Memory

Maintain conversation memory only during the current investigation.

Example:

```text
User: The issue happens in production.
User: Only some users are affected.
```

The agent should remember this during the conversation.

When the conversation/session ends, clear the memory.

Do NOT create permanent user memory.

---

## 7. Anti-Hallucination Rules

The LLM must:

* Only make factual claims supported by retrieved evidence.
* Never invent bug IDs, requirements, test cases, or sources.
* Never claim a root cause is confirmed unless evidence explicitly supports it.
* Clearly distinguish between `Confirmed`, `Likely`, `Possible`, and `Unknown`.
* Say "Insufficient evidence" when appropriate.
* Ask the user for missing information instead of guessing.
* Cite sources for important claims.
* Never fabricate confidence scores.
* Avoid repeating the same information.
* Never repeatedly call the same tool with the same query.

Use low randomness/temperature for investigation and structured output.

---

## 8. Token & Agent Control

Implement hard limits:

```text
Maximum retrieved documents/chunks: 5 after reranking
Maximum agent tool calls: 5
Maximum output tokens: configurable
Maximum conversation history: configurable
Maximum repeated identical tool call: 1
```

Use structured JSON output internally.

Avoid sending unnecessary conversation history or duplicate retrieved context to the LLM.

---

## 9. Example Output

For:

> "Login fails after password reset for some users."

Return:

```text
BUG ANALYSIS

Likely Module:
Authentication

Issue Summary:
Users may be unable to login after resetting their password.

Similar Issues:
BUG-102
BUG-147

Possible Cause:
Authentication tokens may not be invalidated correctly
after password reset.

Recommended Tests:
1. Reset password
2. Login with new password
3. Try old password
4. Verify active sessions
5. Test from another device

Evidence Strength:
High

Sources:
AUTH-REQ-002
BUG-102
TC-AUTH-014
```

Every source must be clickable/viewable.

Avoid generating an arbitrary "87% confidence" ---

## 10. UI
 .

### Screen 1 — Investigation

* App title
* Bug description textarea
* Optional Project
* Optional Module
* Optional Environment
* Optional Priority
* `Investigate Bug` button

### Screen 2 — Investigation Progress

Show:

```text
✓ Understanding bug
✓ Searching previous bugs
✓ Searching requirements
✓ Searching test cases
✓ Reranking evidence
✓ Validating findings
✓ Generating analysis
```

### Screen 3 — Results

Display:

* Bug summary
* Likely module
* Similar bugs
* Possible causes
* Recommended tests
* Evidence strength
* Sources

### Screen 4 — Source Viewer

Allow user to click a source and view its original document content and metadata.

---

## 11. Recommended Architecture

```text
 UI
     ↓
Application/API Layer
     ↓
Agent Controller
     ↓
 ┌──────────────┬──────────────┐
 ↓              ↓              ↓
RAG           Tools          Memory
 ↓              ↓              ↓
Hybrid       3 Tools       Session State
Search
 ↓
Reranker
 ↓
Top Evidence
 ↓
LLM
 ↓
Validator
 ↓
Structured Response
 ↓
UI
```


