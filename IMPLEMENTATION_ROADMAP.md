# Implementation Roadmap — AI QA & Bug Investigation Agent

## Project Progress

**Project:** AI QA & Bug Investigation Agent  
**Knowledge Base:** CallFlow CRM  
**Development Approach:** Incremental MVP development

### Current Status

- Phases 1–5: Implemented.
- Phase 6: Next phase — Basic Grounded LLM Response.
- Phases 7–11: Pending.

Only mark a phase or task as completed after implementation and verification.

---

## Original 11 Development Phases

| Phase | Development Area | Status |
|---|---|---|
| 1 | Dataset | Completed |
| 2 | Ingestion, Chunking & Metadata | Completed |
| 3 | Semantic RAG | Completed |
| 4 | Hybrid Retrieval & Metadata Filtering | Completed |
| 5 | Reranking | Completed |
| 6 | Basic Grounded LLM Response | Pending — Next |
| 7 | CrewAI Agent & Tools | Pending |
| 8 | Short-Term Memory | Pending |
| 9 | Response Validation | Pending |
| 10 | UI Development | Pending |
| 11 | Evaluation & Testing | Pending |

---

## Phase 1 — Dataset

**Objective:** Create a fictional software product knowledge base for investigation.

Planned dataset categories:

- Requirements.
- API documentation.
- Test cases.
- Previous bug reports.
- QA guidelines.

**Status:** Completed.

---

## Phase 2 — Ingestion, Chunking & Metadata

**Objective:** Prepare documents for retrieval.

Key tasks:

- Load knowledge-base documents.
- Extract document content.
- Split documents into meaningful chunks.
- Preserve useful metadata.
- Store document IDs and source information.
- Prepare data for indexing.

**Additional requirement:**

- Ensure the embedding model used for indexing is consistent with the model used for query embeddings in Phase 3.

**Status:** Completed.

---

## Phase 3 — Semantic RAG

**Objective:** Retrieve relevant knowledge-base content using semantic similarity.

Key tasks:

- Generate document embeddings.
- Store embeddings in FAISS.
- Generate embeddings for user queries.
- Retrieve relevant chunks using semantic similarity.
- Preserve source references and metadata.
- Verify that indexing and querying use the same embedding model.

**Status:** Completed.

---

## Phase 4 — Hybrid Retrieval & Metadata Filtering

**Objective:** Improve retrieval by combining semantic and keyword-based search.

Key tasks:

- Implement BM25 keyword retrieval.
- Combine semantic and keyword retrieval.
- Apply metadata filtering.
- Improve retrieval relevance.
- Record retrieval scores.
- Track retrieval latency.

**Additional requirements:**

- Implement safe query/result caching.
- Ensure cached results are invalidated when the knowledge base or index changes.
- Record retrieval metrics for investigation and debugging.

**Status:** Completed.

---

## Phase 5 — Reranking

**Objective:** Improve the relevance of retrieved chunks before sending them to the LLM.

Key tasks:

- Integrate a Cross-Encoder reranker.
- Rerank hybrid retrieval results.
- Select the most relevant chunks.
- Set a reasonable maximum number of context chunks.
- Record reranking scores.
- Track reranking latency.
- Compare retrieval results before and after reranking.

**Additional requirements:**

- Preserve source references after reranking.
- Ensure that irrelevant chunks are not included simply to fill the context limit.

**Status:** Completed.

---

## Phase 6 — Basic Grounded LLM Response

**Objective:** Generate an investigation response using validated retrieved context.

Key tasks:

- Connect the selected LLM provider.
- Pass validated retrieved context to the LLM.
- Generate a structured QA investigation.
- Include relevant source references.
- Configure appropriate temperature and token limits.
- Handle LLM errors.

**Additional requirements:**

- Restrict factual investigation claims to validated RAG context.
- Return a short fallback response when evidence is insufficient.
- Configure maximum input and output token limits.
- Apply frequency penalty when supported by the provider.
- Capture actual input and output token usage.
- Capture LLM latency.
- Collect the information required for estimated cost per query.

**Status:** Pending.

---

## Phase 7 — CrewAI Agent & Tools

**Objective:** Build a controlled QA investigation agent that can use relevant tools.

Planned tools:

- `search_knowledge_base`
- `search_bugs`
- `get_document`

Key tasks:

- Configure the CrewAI agent.
- Define its role, goal, and instructions.
- Connect the existing retrieval functionality.
- Implement tool calling.
- Control the number of tool calls.
- Prevent unnecessary repeated calls.
- Handle tool execution failures.

**Additional requirements:**

- Record investigation steps.
- Log tool execution.
- Include trace IDs in relevant logs.
- Centralize error handling and debugging logs.
- Ensure that the agent cannot bypass evidence-grounding rules.

**Status:** Pending.

---

## Phase 8 — Short-Term Memory

**Objective:** Maintain relevant context during an investigation.

Key tasks:

- Implement short-term conversation or investigation memory.
- Preserve relevant information across investigation steps.
- Avoid unnecessary repeated retrieval.
- Control memory size and relevance.
- Prevent unrelated investigation data from mixing.

**Additional requirements:**

- Generate a unique trace ID for each investigation.
- Associate investigation steps and relevant logs with that trace ID.
- Keep memory behaviour predictable and limited to the current investigation.

**Status:** Pending.

---

## Phase 9 — Response Validation

**Objective:** Validate generated responses before returning them to the user.

Key tasks:

- Validate response structure.
- Check source references.
- Verify that claims are supported by retrieved evidence.
- Detect missing or insufficient evidence.
- Handle unsupported conclusions.
- Return a fallback response when validation fails.

**Additional requirements:**

- Reinforce the restriction that factual claims must be grounded in validated RAG context.
- Verify that insufficient evidence produces the expected fallback response.
- Check that source references match retrieved documents.
- Test validation against unsupported or fabricated claims.

**Status:** Pending.

---

## Phase 10 — UI Development

**Objective:** Build an interface for submitting bug reports and viewing investigation results.

Key tasks:

- Create a bug-report input area.
- Display the investigation response.
- Display supporting sources.
- Show relevant bug IDs and retrieved information.
- Display errors and fallback responses clearly.
- Keep the interface simple and user-friendly.

**Additional requirements:**

- Display estimated cost per query.
- Display input and output token usage.
- Display useful investigation metrics where appropriate.
- Display trace ID for investigation tracking.

**Status:** Pending.

**Note:** Final frontend technology and UI implementation details should follow the confirmed project decision.

---

## Phase 11 — Evaluation & Testing

**Objective:** Evaluate the complete application and verify that the MVP behaves reliably.

Key tasks:

- Test retrieval relevance.
- Test metadata filtering.
- Evaluate reranking quality.
- Test grounded LLM responses.
- Test agent tool calling.
- Test short-term memory.
- Test response validation.
- Test UI functionality.
- Test error handling.
- Run end-to-end investigation scenarios.

**Additional requirements:**

- Verify retrieval and reranking scores.
- Verify retrieval, reranking, LLM, and total latency measurements.
- Verify token usage tracking.
- Verify estimated cost calculations.
- Verify trace ID consistency.
- Verify cache invalidation.
- Test insufficient-evidence and unsupported-claim scenarios.

**Status:** Pending.

---

## Additional Requirements — Tracking Summary

These requirements are integrated into the original phases above. They are not separate development phases.

| # | Requirement | Main Phase(s) |
|---|---|---|
| 1 | Same embedding model for indexing and querying | Phase 3 |
| 2 | LLM uses validated RAG context only | Phase 6, Phase 9 |
| 3 | Short fallback when evidence is insufficient | Phase 6, Phase 9 |
| 4 | Maximum input/output token limits | Phase 6 |
| 5 | Frequency penalty, if supported | Phase 6 |
| 6 | Safe query/result caching | Phase 4 |
| 7 | Estimated cost per query | Phase 6–7 collection, Phase 10 display, Phase 11 testing |
| 8 | Retrieval, reranking, LLM, and total latency | Phases 4, 5, 6, 11 |
| 9 | Retrieval and reranking scores | Phases 4, 5 |
| 10 | Input/output token usage | Phase 6 collection, Phase 10 display, Phase 11 testing |
| 11 | Unique trace ID and investigation step tracking | Phases 7, 8 |
| 12 | Centralized error handling and debug logging | Phases 7, 8 |

---

## Development Tracking

Update this section whenever meaningful work is completed.

### Current Development Position

- **Last completed phase:** Phase 5 — Reranking
- **Next phase:** Phase 6 — Basic Grounded LLM Response
- **Current task:** Connect LLM provider, prompt grounding, and response generation with validated context.
- **Blockers:** None.

### Progress Log

| Date | Phase | Work Completed | Verification / Test Result |
|---|---|---|---|
| 2026-11-06 | Phase 4 | Completed missing Phase 4 requirements: retrieval latency tracking (dense, sparse, total), in-memory query/result cache (`RetrievalCache` with TTL and LRU-style eviction), and automatic cache invalidation on index mtime changes. Cleaned up `.env.example` FAISS index path. | 22/22 pytest tests passing (`test_retrieval.py`, `test_bm25_filter.py`, `test_ingestion.py`). |
| 2026-11-07 | Phase 5 | Implemented Cross-Encoder reranker (`DocumentReranker` using `ms-marco-MiniLM-L-6-v2`), diversity filtering (`max_chunks_per_doc`) to avoid context monopolization, score cutoff filtering, and reranking latency/metrics tracking. | 6/6 new tests in `test_reranker.py` passing; comparison demo verified. |

### Important Notes

- Do not change the original 11 phases.
- Do not mark a task complete without verification.
- Update this roadmap after each meaningful milestone.
- Record failed tests and unresolved issues.
- Keep the README focused on the public project overview.
- Keep development instructions in `PROJECT_RULES.md`.
- Use this file as the source of truth for implementation progress.