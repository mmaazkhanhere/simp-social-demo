# Solution Approach

This solution is built as a dealership-scoped conversational lead qualification system for Buy Here Pay Here flows. The backend keeps each conversation isolated by `dealership_id`, stores messages and lead state in the database, and uses the LLM in three focused places:

1. Generate the assistant greeting and ongoing customer-facing replies.
2. Extract structured lead fields from each incoming customer message.
3. Classify intent (`hot`, `warm`, `cold`) and willingness to proceed.

The main flow in [`backend/app/services/conversation_service.py`](/E:/Web%203.0/Generative%20AI/Github/simp-social-demo/backend/app/services/conversation_service.py) is:

1. Persist the user message.
2. Run structured extraction on only that latest customer message.
3. Score the lead using conversation history plus known lead state.
4. Create or update the dealership-scoped lead record.
5. Generate the assistant reply using dealership context, language, history, and current lead snapshot.
6. Mark the lead `application_ready` and send a notification when readiness criteria are met.

This separation is intentional. Reply generation is open-ended and conversational, while extraction and scoring are narrower tasks with stricter outputs and easier validation.

## Tradeoffs Made

### Deterministic vs LLM-Based Extraction

The current implementation uses LLM-based extraction with deterministic normalization after the model returns structured output.

Why this was chosen:
- It handles natural SMS-style language better than pure regex or rule matching.
- It supports corrections naturally, for example: "actually I make closer to 4k".
- It fits the project requirement to avoid a rigid scripted flow.

Where deterministic logic is still used:
- Field normalization for phone numbers, money amounts, employment labels, and timeline values in [`backend/app/services/extraction_service.py`](/E:/Web%203.0/Generative%20AI/Github/simp-social-demo/backend/app/services/extraction_service.py).
- Fallback scoring heuristics in [`backend/app/services/scoring_service.py`](/E:/Web%203.0/Generative%20AI/Github/simp-social-demo/backend/app/services/scoring_service.py).
- Notification deduplication at the database level through a uniqueness constraint on `(dealership_id, lead_id, event_type)`.

Tradeoff:
- LLM extraction improves recall and robustness on messy language.
- Deterministic extraction would be cheaper and more predictable, but likely misses paraphrases, indirect disclosures, and corrections unless rules become large and brittle.

Practical view:
- For an MVP, this hybrid is the right balance.
- For production, I would move to a tiered approach: deterministic extraction first for obvious values, then call the LLM only when confidence is low or the message is ambiguous.

### Token Usage and Quality

There are two quality/cost profiles in the current backend:

- Assistant reply generation uses full conversation history plus a fairly detailed system prompt.
- Extraction uses only the latest customer message, which keeps cost small and reduces hallucination risk.
- Intent scoring uses history and lead snapshot, which is more expensive than extraction but still narrower than reply generation.

This is a sensible tradeoff:
- Reply quality benefits from conversational context.
- Extraction quality benefits from being constrained to the latest message only.
- Intent scoring benefits from both current message and accumulated context.

Weakness in the current version:
- Reply generation and intent scoring both resend history repeatedly, so token usage grows with long threads.
- There is no context compaction, summarization, or sliding window yet.
- `max_tokens=250` is safe for short SMS replies, but it is still a fixed cap rather than a dynamic budget.

Production direction:
- Keep extraction scoped to one message.
- Cap reply/scoring context to a recent-message window plus a compact running summary.
- Cache stable prompt fragments.
- Track prompt and completion token usage per conversation and per dealership.

### Rate Limit Hitting

Today a single inbound message can trigger multiple model calls:

1. Extraction
2. Intent classification
3. Assistant reply

That is manageable for a demo, but it will become a bottleneck under higher parallel traffic. The code currently has graceful degradation in some places:

- If structured extraction fails or no API key is configured, it returns empty updates.
- If intent classification fails, it falls back to deterministic heuristics.

But the main assistant reply path currently requires the LLM and raises if the provider is unavailable.

Tradeoff:
- This gives better conversational quality in the happy path.
- It also means rate limiting or provider failure can block the visible customer response even though extraction/scoring have fallbacks.

Production direction:
- Add retries with exponential backoff for transient 429/5xx responses.
- Add request queues and concurrency controls per provider key.
- Add a deterministic fallback reply set for service degradation scenarios.
- Consider splitting real-time reply generation from non-blocking analytics/scoring work where possible.

## How This Scales Across 100+ Dealerships

The current data model already supports multi-tenant behavior at the dealership level:

- `dealership_id` scopes conversations, leads, contacts, and notifications.
- Each dealership can have its own name, slug, default language, and webhook URL.
- Prompt generation injects dealership identity into the assistant behavior without creating separate code paths per store.

That means scaling from 3 dealerships to 100+ is conceptually straightforward, but a few architectural changes are needed for operational scale.

### What Already Scales Reasonably

- Shared application logic across all dealerships.
- Tenant isolation through foreign keys and scoped queries.
- Event deduplication for webhook notifications.
- Configurable dealership metadata instead of hardcoding per-store behavior.

### What Will Break First

- SQLite will become a bottleneck for concurrent writes and operational reliability.
- Synchronous LLM calls inside the request path will increase latency and reduce throughput.
- Re-sending full history on every turn will push token cost and response times up.
- A single provider/API key creates concentrated rate-limit risk.

### Recommended Scaling Path

1. Move from SQLite to Postgres.
2. Add indexes and query review for high-volume tables such as `messages`, `leads`, and `notification_events`.
3. Put webhook delivery and non-critical scoring/analytics behind a job queue.
4. Add per-dealership and global observability for latency, token use, failures, and webhook delivery.
5. Introduce context compaction so long conversations do not scale linearly in prompt size.
6. Support provider failover or key sharding if dealership volume becomes bursty.

With those changes, 100+ dealerships is realistic because the tenancy model is already simple and clean. The bigger concern is not tenant count itself; it is per-message synchronous compute and provider dependency.

## How I Would Improve This In Production

### Reliability

- Add retry/backoff and explicit handling for 429, timeout, and provider outages.
- Queue webhook delivery and store retry state instead of fire-and-forget HTTP inside the request path.
- Add fallback customer-facing responses when the LLM is unavailable.

### Cost and Performance

- Use a hybrid extraction strategy: deterministic first, LLM second.
- Reduce prompt size with a rolling conversation summary.
- Add token and latency telemetry per route, model, and dealership.
- Consider smaller/faster models for extraction and scoring, and reserve the best conversational model for reply generation.

### Quality

- Add confidence scoring per extracted field, not just a global extraction confidence envelope.
- Expand normalization to handle ranges more explicitly, for example `2500-3000` or `500 down today`.
- Add evaluation datasets from real dealership conversations and track precision/recall for extraction and readiness triggers.
- Add guardrails for language quality, repeated-question prevention, and objection-handling consistency.

### Multi-Dealership Operations

- Support dealership-specific prompt overlays, compliance rules, and webhook schemas without branching core logic.
- Add rate limits and quotas per dealership to isolate abuse or traffic spikes.
- Add admin controls for enabling/disabling automation, changing readiness thresholds, and viewing failed webhook deliveries.

### Data and Product Maturity

- Track funnel metrics: conversation started, qualified, ready to apply, submitted, handoff needed.
- Store a compact lead-state change log for auditability.
- Add human handoff triggers and agent takeover tooling for edge cases.
- Add A/B testing for prompt strategies by dealership cohort.

## Bottom Line

This implementation is a solid MVP because it separates conversational generation, structured extraction, scoring, and notification into distinct services and already enforces dealership-level data isolation. The main production gaps are predictable: synchronous LLM dependency, growing token cost with long histories, lack of queueing/retries, and SQLite as the datastore. Those are solvable without changing the core product shape.
