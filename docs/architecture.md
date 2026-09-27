# Runtime architecture

| Mode | Classification | Retrieval | Generation | Verification |
|---|---|---|---|---|
| Bailian API Demo (`lite`) | Exact preset → illustrative scores | BM25 + API Dense → RRF → API Reranker over six synthetic records | Qwen-Plus with Evidence Packet | Three live presets + offline HTTP tests |
| Full | Qwen3-4B BF16 LoRA | Same strict Hybrid chain over a matching private index | Qwen-Plus with case/statute evidence | Components tested; private assets and live credentials absent |

React/Vite talks to FastAPI through a same-origin `/api` proxy. Only the backend reads `.env`. `/api/capabilities` checks configuration and asset presence, not provider operational readiness. `/api/analyze` validates 5–8,000 characters and an as-of date. Application code does not persist submitted facts; configured provider calls send redacted query/evidence text to Bailian.

The API Demo loads corpus vectors once per process/configuration; each supported query makes fresh embedding, reranking and generation requests. Both BM25 and Dense apply charge filtering before recall. RRF merges ranks, then the API reranks fused documents. Each stage's ranking, score and timing appears in the trace. Missing candidate charges explicitly skip retrieval. Custom inputs have no fabricated classifier output and skip generation.

Demo statute summaries lack verified source/date metadata and are excluded from the generation packet. This requires low-confidence abstention and manual review. The validator checks schema, citation membership/type and supplied statute metadata; it cannot establish semantic entailment or legal correctness. Provider generation errors or invalid drafts cause an explicitly labelled fallback. Retrieval errors return 503 and never silently select sparse-only results.

Full Mode preflights the matching API embedding model/dimensions in its index manifest and requires the BF16 assets and statute index. Loading is lazy and cached; restart after changes. The traditional sentencing baseline is disabled by default.

The production service never imports the offline mock provider. Stored test outputs and screenshots are explicitly labelled mock API contract previews, with the separate live check documented in [Bailian validation](bailian-live-validation.md).
