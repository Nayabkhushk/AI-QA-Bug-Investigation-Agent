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

Keep the architecture modular so components can later be replaced.

---

## 12. Development Order

Build in this exact order:

### Phase 1

Create fictional CallFlow CRM dataset.

### Phase 2

Implement document loading, chunking, metadata and vector database.

### Phase 3

Implement basic semantic RAG.

### Phase 4

Add BM25 keyword search + metadata filtering.

### Phase 5

Add reranking.

### Phase 6

Add basic grounded LLM response.

### Phase 7

Convert it into an agent with the 3 tools.

### Phase 8

Add short-term conversation memory.

### Phase 9

Add validation/grounding checks.

### Phase 10

Build UI.

### Phase 11

Create QA/evaluation tests for:

* Retrieval accuracy
* Agent tool selection
* Hallucination
* Source grounding
* Memory clearing
* Repeated tool calls
* Missing information handling

---

## 13. Important Development Rule

Do NOT over-engineer the MVP.

Do NOT initially implement:

* Multi-agent architecture
* Jira integration
* GitHub integration
* Browser automation
* Selenium/Playwright execution
* Voice
* Fine-tuning
* Knowledge graphs
* Microservices
* Kubernetes
* Complex authentication

The MVP should prove:

**Hybrid RAG → Reranking → Agent → Tools → Validation → Grounded QA Analysis**

Build each layer separately and test it before moving to the next layer.

14. Development & Safety Instructions

These instructions are mandatory throughout development.

Approval Before Changes

Before doing any major implementation, installation, configuration change, database change, API integration, or architectural decision:

ASK FOR MY APPROVAL FIRST.

Do not make major changes automatically.

For small safe code changes that are directly required by an already-approved task, implementation can continue, but if there is any uncertainty, ask me first.

Before installing a new package or technology that is not already part of the approved stack, explain:

What it is
Why we need it
Whether there is a free option
What it will change
Whether I approve it

Then wait for my approval.

API Keys & Secrets

NEVER expose, print, hardcode, commit, or display API keys, passwords, tokens, credentials, or other secrets.

Use environment variables and .env files.

Example:

.env
LLM_API_KEY=your_key_here

The actual key must never appear in:

Source code
Git commits
GitHub
Screenshots
Logs
Terminal output
Documentation
Error messages
UI

Create:

.env.example

containing placeholders only:

LLM_API_KEY=

Also create/update:

.gitignore

to ensure .env and other secret files are never committed.

If any API key or external service is required, STOP and tell me exactly what is needed and how I can obtain/configure it. Do not create or use the key yourself.

Explain the setup in beginner-friendly steps.

Free Tools & Services

Use free/open-source options wherever reasonably possible.

Do not introduce paid services without asking me first.

Prefer:

Free/open-source libraries
Local development
Local vector database
Free-tier APIs where appropriate
Free models/services where practical

If something requires payment, subscription, billing, or a credit card:

STOP and ask for my approval before implementing it.

Git Backup

Initialize Git at the beginning of the project so the project can be safely backed up.

Create a clean initial repository.

Recommended process:

git init
git add .
git commit -m "Initial project setup"

Then explain to me how to create a GitHub repository and connect it.

Use meaningful commits during development, for example:

Initial project setup
Add document ingestion pipeline
Add vector search
Add hybrid retrieval
Add reranking
Add agent tools
Add response validation
Add Streamlit UI

Never commit secrets.

Before major architectural changes, create a Git commit so the previous working version can be restored.

Beginner-Friendly Project Structure

Keep the code modular but not over-engineered.

Do not create unnecessary folders or dozens of files.

Use clear names so I can understand the project just by looking at the structure.

Suggested structure:

ai-qa-bug-assistant/
│
├── app/
│   ├── main.py
│   │
│   ├── agent/
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   └── state.py
│   │
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── retrieval.py
│   │   ├── reranker.py
│   │   └── vector_store.py
│   │
│   ├── tools/
│   │   ├── search_knowledge.py
│   │   ├── search_bugs.py
│   │   └── get_document.py
│   │
│   ├── validation/
│   │   └── response_validator.py
│   │
│   └── ui/
│       └── components.py
│
├── data/
│   ├── requirements/
│   ├── api_docs/
│   ├── test_cases/
│   ├── bugs/
│   └── qa_guidelines/
│
├── tests/
│   ├── test_retrieval.py
│   ├── test_agent.py
│   └── test_validation.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── run.py

If a simpler structure can achieve the same result, prefer the simpler structure.

Code Quality

Keep the code:

Modular
Readable
Beginner-friendly
Reusable
Well commented where necessary
Easy to debug

Avoid:

Giant single files
Duplicate code
Unnecessary abstractions
Complex design patterns
Premature optimization
Unnecessary frameworks

Each file should have one clear responsibility.

For example:

retrieval.py
→ retrieval logic

reranker.py
→ reranking logic

search_bugs.py
→ bug search tool

agent.py
→ agent decision workflow
Explain Before Implementing New Components

Whenever a new component is required, explain it to me briefly before implementation.

Use this format:

What:
Why:
Free option:
Files affected:
What I need to configure:

If an API key, account, environment variable, database, model, or external service is required, tell me exactly what I need to do.

Do not assume that I already know how to configure it.

Development Style

I am a beginner, so do not dump a huge amount of code at once.

Build the project incrementally.

Preferred workflow:

Plan
 ↓
Explain
 ↓
Ask approval if required
 ↓
Implement one small component
 ↓
Run/test it
 ↓
Show me the result
 ↓
Git commit
 ↓
Move to next component

Do not build the entire application in one step.

Important

The priority is:

Simple → Modular → Understandable → Testable → Reliable

Not:

Complex → Enterprise-scale → Difficult to understand I have Created a Readme.md file of this whole mvp prd so that you can not forget any detail until the project is completed 
