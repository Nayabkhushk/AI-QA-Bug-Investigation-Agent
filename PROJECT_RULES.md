# Project Rules — AI QA & Bug Investigation Agent

## 1. Project Objective

Build a beginner-friendly, modular AI QA & Bug Investigation Agent that investigates software bug reports using a documented knowledge base.

The system should retrieve relevant requirements, API documentation, test cases, previous bug reports, and QA guidelines before generating an evidence-grounded investigation.

The project is intended to demonstrate practical understanding of RAG, retrieval, reranking, agent workflows, tool calling, validation, and software testing.

## 2. General Development Rules

- Keep the implementation simple, modular, and understandable.
- Prefer readable code over unnecessary abstractions.
- Do not introduce complex architecture without a clear requirement.
- Do not add unnecessary libraries or dependencies.
- Use free and locally runnable tools wherever practical.
- Avoid overengineering. Build only what the MVP requires.
- Follow the existing project structure unless a change is necessary.
- Reuse existing functions and modules instead of creating duplicate implementations.
- Do not rewrite working code just to make cosmetic improvements.
- Keep the implementation aligned with the README and implementation roadmap.

## 3. Development Workflow

Follow these rules for every development task:

1. Read `README.md`, `PROJECT_RULES.md`, and `IMPLEMENTATION_ROADMAP.md` before starting work.
2. Inspect the existing code and understand the current implementation.
3. Identify the relevant development phase.
4. Explain the planned changes before making significant modifications.
5. Ask for approval before:
   - Installing new dependencies.
   - Changing the project architecture.
   - Deleting or replacing existing files.
   - Modifying environment configuration.
   - Introducing paid services or tools.
   - Making changes that could affect completed phases.
6. Implement one logical task at a time.
7. Explain important code changes in beginner-friendly language.
8. Run relevant tests after implementation.
9. Fix errors before moving to the next task.
10. Update `IMPLEMENTATION_ROADMAP.md` after completing and verifying a task.

Do not mark a feature as completed merely because code has been written. Verify that it works.

## 4. Code Quality and Project Structure

- Use clear and meaningful file, function, and variable names.
- Keep retrieval, embedding, reranking, agent, tools, validation, and UI logic separated.
- Avoid placing the entire application in one Python file.
- Use configuration files and environment variables for settings.
- Avoid hardcoding API keys, passwords, or other secrets.
- Add comments where they help explain non-obvious logic.
- Handle expected errors gracefully.
- Keep dependencies documented in `requirements.txt`.
- Do not introduce a new framework or database without approval.

## 5. RAG and Retrieval Rules

- Use the same embedding model for indexing documents and embedding user queries.
- Preserve document metadata during ingestion and retrieval.
- Apply metadata filtering where appropriate.
- Combine semantic and keyword retrieval as required by the hybrid retrieval phase.
- Apply reranking to improve the relevance of retrieved results.
- Record retrieval and reranking scores.
- Track retrieval and reranking latency.
- Keep caching safe and consistent with the current knowledge-base version.
- Invalidate or refresh cached results when the knowledge base or index changes.
- Do not return irrelevant documents simply to fill a result limit.

## 6. LLM Grounding and Response Rules

- The LLM must use validated retrieved context for factual investigation claims.
- Do not allow the LLM to invent requirements, bug IDs, test results, document contents, or technical explanations.
- Clearly distinguish retrieved evidence from assumptions or recommendations.
- Include source references wherever possible.
- If the retrieved evidence is insufficient, return a short fallback response explaining what information is missing.
- Do not generate confident conclusions from weak or unrelated evidence.
- Apply sensible input and output token limits.
- Use a low temperature for predictable investigation responses.
- Apply frequency penalty only when supported by the selected LLM provider.
- Do not assume that every LLM provider supports identical parameters.

## 7. Agent and Tool-Calling Rules

- Keep the agent's role focused on QA and bug investigation.
- Give the agent access only to the tools required for the task.
- Prefer existing tools over creating duplicate tools.
- Define clear input and output expectations for every tool.
- Limit unnecessary or repeated tool calls.
- Do not allow the agent to bypass retrieval and evidence validation.
- Handle tool failures without crashing the entire application.
- Keep tool execution and investigation steps traceable.
- Use a unique trace ID for each investigation.
- Log important steps using the same trace ID.

## 8. Monitoring and Cost Tracking

Implement monitoring incrementally as the relevant phases are developed.

Track where applicable:

- Retrieval latency.
- Reranking latency.
- LLM response latency.
- Total investigation latency.
- Retrieval scores.
- Reranking scores.
- Input and output token usage.
- Estimated LLM cost per query.

Calculate cost using actual token usage and the selected provider's applicable pricing. Do not invent or hardcode arbitrary pricing.

Display useful metrics in the UI when the relevant functionality is available.

## 9. Error Handling and Logging

- Use consistent error-handling patterns.
- Avoid exposing API keys, credentials, or sensitive configuration in logs.
- Log useful debugging information without unnecessarily printing large document contents.
- Include trace IDs in relevant logs.
- Handle missing files, invalid inputs, retrieval failures, tool errors, and LLM errors gracefully.
- Return understandable error messages to the user.
- Do not silently ignore important failures.

## 10. Security and Secrets

- Keep `.env` out of Git.
- Maintain a `.env.example` containing placeholder values only.
- Never expose API keys in source code, logs, screenshots, or public documentation.
- Do not upload private datasets or credentials to GitHub.
- Review files before committing or pushing.
- Do not use paid APIs or services without approval.

## 11. Testing Requirements

- Test each feature after implementation.
- Write tests for important retrieval, filtering, reranking, agent, and validation behaviour.
- Include normal, edge, and failure scenarios.
- Verify that insufficient evidence triggers the fallback response.
- Verify that unsupported claims are not presented as retrieved facts.
- Test cache invalidation when knowledge-base content changes.
- Verify that token usage, latency, and cost metrics are recorded correctly when available.
- Do not claim that a feature is tested if it has not actually been tested.

## 12. Git and Backup Rules

- Preserve completed work.
- Encourage small, meaningful Git commits after verified milestones.
- Never overwrite or delete working code without explaining the impact.
- Check the Git status before major changes.
- Do not push secrets, temporary files, virtual environments, or generated indexes unless explicitly required.
- Ask before performing destructive Git operations.

## 13. Scope Control

The goal is a working MVP, not an enterprise-scale platform.

Do not introduce the following unless explicitly approved:

- Complex multi-agent architecture.
- Jira or GitHub integrations.
- Browser automation.
- Selenium or Playwright test execution.
- Voice features.
- Model fine-tuning.
- Knowledge graphs.
- Microservices.
- Kubernetes.
- Complex authentication systems.

## 14. Communication Rules

- Explain technical concepts in simple English.
- Assume the project owner is learning the implementation.
- Explain what a change does and why it is needed.
- Provide exact file paths when asking for manual changes.
- Give copy-paste-ready commands when possible.
- Do not skip steps or assume the owner understands unfamiliar tools.
- Clearly identify completed work, pending work, and blockers.

## 15. Phase Documentation, Screenshots & LinkedIn Updates

The project owner wants to document the development journey on LinkedIn. For every development phase, the following documentation workflow must be followed:

- **Pre‑implementation screenshot plan**: Before starting work, list exactly which screenshots (or terminal outputs, logs, metrics, test results) should be captured, when they should be taken, and how to capture them (tools, window size, annotations).

- **Screenshot purpose**: Explain for each screenshot what it demonstrates and why it serves as evidence of the phase.

- **Milestone reminders**: Provide reminders to capture evidence at key milestones during the phase (e.g., after successful indexing, after retrieval test, after agent response validation).

- **Post‑phase LinkedIn draft**: After completing and testing the phase, draft a professional LinkedIn post that accurately describes what was implemented, the challenges faced, lessons learned, and includes the captured evidence.

### Before Starting Each Phase

- Explain what the phase is about in simple language.
- Identify the main features or tasks that will be implemented.
- Tell the project owner exactly which screenshots should be captured during this phase.
- Explain when to take each screenshot and which application, file, terminal, or interface should be visible.
- Explain what the screenshot should demonstrate and why it is useful.
- Provide a suggested screenshot filename.
- Do not ask the owner to capture screenshots that do not provide meaningful evidence.

### During Implementation

- Remind the owner to capture screenshots at important milestones instead of waiting until the entire phase is finished.
- Identify useful evidence such as:
  - Relevant code or configuration (only when it helps explain the implementation).
  - Terminal output showing successful execution.
  - Retrieval results, scores, or other relevant metrics.
  - UI screenshots when a user-facing feature is implemented.
  - Test results showing verified behaviour.
- Explain how to capture a clear screenshot, including what to keep visible and what to avoid.
- Never ask the owner to expose API keys, passwords, personal information, private data, or other secrets.
- Do not fabricate screenshots, results, metrics, or implementation evidence.

### After Completing Each Phase

Provide a short phase summary containing:

1. What was implemented.
2. What problem the implementation solves.
3. Which technologies, libraries, or techniques were used.
4. What was tested and the actual test result.
5. Which screenshots were captured and what each one proves.
6. Any limitations or remaining work.

Then prepare a LinkedIn post draft based only on the work that has actually been implemented and verified.

The LinkedIn draft should:
- Sound natural, professional, and suitable for a developer/QA learning journey.
- Explain the technical work in understandable language.
- Highlight practical learning and challenges.
- Avoid exaggerated claims or suggesting that unimplemented features are complete.
- Avoid presenting AI-generated or illustrative outputs as real test results.
- Include relevant technical hashtags without excessive hashtags.


### Important

Screenshot guidance and LinkedIn documentation are part of every development phase. Do not wait until the end of the entire project to document the work.

The owner should understand what to capture, when to capture it, and what the evidence demonstrates.

## 16. Final Rule

The implementation must remain consistent with the project's README, original 11 development phases, and implementation roadmap.

Do not change the original phase names, order, or scope without explicit approval.

**Build incrementally. Verify before marking complete. Preserve working functionality.**