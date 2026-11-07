# AI QA & Bug Investigation Agent

An AI-powered QA investigation tool that helps analyze software bug reports using project documentation, requirements, API references, test cases, previous bug reports, and QA guidelines.

The agent retrieves relevant information, evaluates available evidence, and produces a structured investigation with possible causes, recommended tests, and references to supporting documents.

## Problem & Goal

Consider the following bug report:

> Login fails after password reset for some users.

Investigating this issue may require checking authentication requirements, API documentation, previous bug reports, and relevant test cases.

The goal of this project is to build an agent that can:

- Understand a reported software issue.
- Retrieve relevant project documentation.
- Identify similar historical bugs.
- Analyze possible causes using available evidence.
- Recommend relevant test cases.
- Provide source references for its findings.
- Identify when the available evidence is insufficient.

The system is designed to prioritize evidence-grounded analysis rather than unsupported assumptions.

## Core Features

- **Hybrid RAG:** Combines semantic and keyword-based retrieval.
- **Metadata Filtering:** Narrows document retrieval using relevant metadata.
- **Reranking:** Reorders retrieved results to improve relevance.
- **Agent-Based Investigation:** Uses CrewAI and defined tools to investigate issues.
- **Evidence-Based Responses:** Grounds analysis in retrieved and validated documentation.
- **Source References:** Connects findings to their supporting documents.
- **Short-Term Memory:** Maintains relevant context during an investigation.
- **Response Validation:** Checks whether generated responses are supported by retrieved evidence.
- **Observability:** Tracks retrieval scores, latency, token usage, estimated cost, and investigation traces.

## Example Investigation

**Input:**

`Login fails after password reset for some users.`

**Expected Output:**

```text
BUG ANALYSIS

Likely Module: Authentication

Issue Summary:
Some users may be unable to log in after resetting
their passwords.

Similar Issues:
BUG-102, BUG-147

Possible Cause:
Authentication tokens may not be invalidated
correctly after a password reset.

Recommended Tests:
1. Reset the password and log in using the new password.
2. Attempt login using the old password.
3. Verify that active sessions are invalidated.
4. Test login from another device.

Evidence Strength: High

Sources:
AUTH-REQ-002, BUG-102, TC-AUTH-014
```

*This is an illustrative example. Actual findings and references will depend on the retrieved documentation.*

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Programming Language | Python 3.11 | Backend development |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` | Local document and query embeddings |
| Vector Search | `faiss-cpu` | Vector similarity search |
| Keyword Search | BM25 | Keyword-based retrieval |
| Agent Framework | CrewAI | Controlled agent workflow and tool calling |
| Reranking | Cross-Encoder | Improve retrieval relevance |
| LLM | Configured through environment variables | Grounded bug analysis |
| Document Storage | Markdown files | Fictional CallFlow CRM knowledge base |
| Configuration | `.env` | Environment variables and API configuration |
| Testing | pytest | Unit and integration testing |

The embedding model runs locally on CPU. The LLM provider is configured separately and may require an API key and internet access.

## Knowledge Base

The project uses a fictional software product named **CallFlow CRM** to provide a controlled dataset for development and testing.

| Document Category | Planned Documents |
|---|---:|
| Requirements | 5 |
| API Documentation | 5 |
| Test Cases | 8 |
| Previous Bug Reports | 10 |
| QA Guidelines | 3 |
| **Total** | **31** |

Documents include relevant metadata such as project, module, document ID, and priority where applicable.

## System Architecture

The intended investigation workflow:

```text
User Bug Report
      |
      v
Understand the Issue
      |
      v
Hybrid Retrieval
(FAISS + BM25 + Metadata Filtering)
      |
      v
Reranking
      |
      v
Evidence Assessment
      |
      +---- Insufficient Evidence
      |          |
      |          v
      |     Ask for More Information
      |
      v
CrewAI Agent
      |
      v
Tool-Based Investigation
      |
      v
Grounded LLM Analysis
      |
      v
Response Validation
      |
      v
Structured QA Investigation
      |
      v
Source References & Metrics
```

The workflow will use controlled tool access and defined limits to avoid unnecessary or repeated tool calls.

## CrewAI Tools

The planned agent uses three primary tools:

| Tool | Purpose |
|---|---|
| `search_knowledge_base` | Search requirements, API documentation, test cases, and QA guidelines |
| `search_bugs` | Search previous bug reports |
| `get_document` | Retrieve the full content of a specific document by ID |

## Investigation Constraints

| Constraint | Planned Configuration |
|---|---|
| Maximum tool calls per investigation | 5 |
| Maximum retrieved chunks after reranking | 5 |
| Repeated identical tool calls | Limited |
| LLM temperature | Low (approximately 0.1–0.2) |
| Evidence requirements | Retrieved and validated context |
| Response format | Structured analysis with source references |

Exact limits and provider-specific settings will be configurable where appropriate.

## Evidence & Response Grounding

The system is designed to follow these rules:

- Generate factual investigation findings only from validated retrieved context.
- Do not invent bug IDs, requirement IDs, or test case IDs.
- Distinguish between `Confirmed`, `Likely`, `Possible`, and `Unknown`.
- Clearly state when evidence is insufficient.
- Include source references for supported claims.
- Do not fabricate confidence scores.
- Avoid presenting assumptions as confirmed root causes.
- Ask for additional information when the available evidence cannot support a reliable investigation.

## Development Roadmap

The project follows an 11-phase development plan. Reliability, performance, cost-control, and observability requirements are integrated into these existing phases rather than treated as a separate roadmap.

| Phase | Description | Scope |
|---|---|---|
| 1. Dataset | Create the fictional CallFlow CRM knowledge base | Requirements, API docs, test cases, bug reports, and QA guidelines |
| 2. Ingestion & Indexing | Prepare documents for retrieval | Document loading, cleaning, chunking, metadata, embeddings, and FAISS indexing |
| 3. Semantic RAG | Implement semantic retrieval | FAISS search and consistent embedding model usage for indexing and querying |
| 4. Hybrid Retrieval | Improve document retrieval | BM25, metadata filtering, hybrid scoring, safe query/result caching, retrieval latency, and retrieval score tracking |
| 5. Reranking | Improve relevance of retrieved evidence | Cross-encoder reranking, reranking scores, and latency tracking |
| 6. LLM Integration | Generate grounded investigation responses | Validated RAG context, insufficient-evidence fallback, input/output token limits, frequency penalty where supported, token usage, LLM latency, and cost accounting |
| 7. CrewAI Agent & Tools | Build the controlled investigation agent | Three defined tools, tool-call limits, centralized logging, and error handling |
| 8. Short-Term Memory | Maintain investigation context | Session memory, unique trace IDs, and investigation-step tracking |
| 9. Response Validation | Validate generated findings | Evidence grounding, source references, unsupported-claim checks, and fallback handling |
| 10. UI Development | Build the user interface | Bug report input, structured investigation results, source references, and display of token usage and estimated cost |
| 11. Evaluation & Testing | Evaluate the complete system | Retrieval quality, response grounding, functional tests, performance, cost tracking, and observability tests |

### Additional Reliability & Observability Requirements

The following requirements are part of the development plan:

| # | Requirement | Planned Phase |
|---|---|---|
| 1 | Use the same embedding model for document indexing and query embedding | 3 |
| 2 | Restrict LLM responses to validated RAG context | 6 and 9 |
| 3 | Provide a short fallback when evidence is insufficient | 6 and 9 |
| 4 | Configure maximum input and output token limits | 6 |
| 5 | Support frequency penalty if the selected provider allows it | 6 |
| 6 | Implement safe query/result caching | 4 |
| 7 | Track estimated cost per investigation | 6/7; display in 10 and test in 11 |
| 8 | Track retrieval, reranking, LLM, and total latency | 4, 5, 6, and end-to-end evaluation in 11 |
| 9 | Record retrieval and reranking scores | 4 and 5 |
| 10 | Track input and output token usage | 6; display in 10 and test in 11 |
| 11 | Generate a unique trace ID and record investigation steps | 8, integrated with logging in 7 |
| 12 | Centralize error handling and debug logging | 7 and 8 |

These features will be introduced incrementally alongside their corresponding development phases. They are not intended to be implemented all at once.

## Planned Project Structure

The project structure may evolve as development progresses. Components are kept separate according to their responsibilities.

```text
ai-qa-bug-agent/
│
├── app/
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
│   └── main.py
│
├── data/
│   ├── requirements/
│   ├── api_docs/
│   ├── test_cases/
│   ├── bugs/
│   └── qa_guidelines/
│
├── faiss_index/
│
├── tests/
│
├── eval/
│
├── .env.example
├── .gitignore
├── requirements.txt
├── ingest.py
├── README.md
├── PROJECT_RULES.md
└── IMPLEMENTATION_ROADMAP.md
```

Generated files, evaluation files, and additional modules will be added when required by the relevant development phase.

## Setup & Usage

The following commands describe the intended local setup. Run them once the corresponding application components are available.

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai-qa-bug-agent
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac/Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file:

**Windows:**

```bash
copy .env.example .env
```

**Mac/Linux:**

```bash
cp .env.example .env
```

Configure the required LLM provider and API key in `.env` according to the selected provider.

Never commit the actual `.env` file or expose credentials.

### 5. Build the knowledge base index

```bash
python ingest.py
```

This step prepares the documents, generates embeddings, and saves the FAISS index and associated metadata locally.

Rebuild the index when the source documents or relevant indexing configuration change.

### 6. Run the application

The application entry point and run command will be finalized with the UI implementation.

### 7. Run tests

```bash
pytest tests/
```

Evaluation scripts and additional tests will be introduced as the relevant components are implemented.

## Development Scope

The initial version focuses on demonstrating the complete bug investigation workflow without unnecessary infrastructure.

The following are outside the initial MVP scope:

- Multi-agent architecture
- Jira integration
- GitHub integration
- Browser automation
- Selenium/Playwright test execution
- Voice interaction
- Model fine-tuning
- Knowledge graphs
- Microservices
- Kubernetes
- Complex authentication systems

The primary objective is to build a working, testable system that demonstrates:

**Hybrid RAG → Reranking → Controlled Agent → Tool Calling → Memory → Validation → Grounded QA Analysis**

## Project Documentation

Additional project documentation is maintained separately:

| File | Purpose |
|---|---|
| `PROJECT_RULES.md` | Development rules, agent instructions, approval requirements, security, and implementation guidelines |
| `IMPLEMENTATION_ROADMAP.md` | Phase progress, completed tasks, pending tasks, test results, and the next implementation step |

These files help maintain consistent development practices and project continuity.

---

**Project:** AI QA & Bug Investigation Agent  
**Knowledge Base:** Fictional CallFlow CRM  
**Development Approach:** Incremental, modular, and test-driven