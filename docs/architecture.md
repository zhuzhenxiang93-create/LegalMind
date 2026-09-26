# Runtime architecture

| Mode | Classification | Case retrieval | Generation | Verified in this release |
|---|---|---|---|---|
| Lite | Exact preset match → illustrative scores | Live character-bigram BM25 over six synthetic records | Extractive template and legal abstention | API, browser, regression |
| Full default | Qwen3-4B BF16 LoRA | Existing charge-partitioned BM25 and factual reranking | OpenAI-compatible API | Component/mock tests only; external assets absent |
| Research Hybrid | BF16 classifier | BM25 + Dense, RRF, Reranker | Configured generation | Component tests; real E2E pending |

The React/Vite frontend talks to FastAPI through a same-origin `/api` proxy. Lite has no model or API dependency. `/api/capabilities` checks Full asset configuration, not operational readiness. `/api/analyze` accepts `fact`, `as_of_date` and `mode`. Pydantic bounds text to 5–8,000 characters and validates dates. Requests are not persisted.

Lite scores are authored illustrations rather than measured classifier probabilities. Matching is exact: modifying a preset disables fixture scores. Case retrieval uses BM25 after filtering the synthetic corpus to candidate charges. Raw BM25 values are ranking scores, not normalized confidence.

The Full adapter verifies required configuration, then loads the existing pipeline lazily. Default inference saves no additional model copies. The research sentencing baseline is disabled in the default Full configuration. OpenAI-compatible generation consumes the existing Evidence Packet and output schema.

Checks enforce schema, citation membership, citation types, supplied source/date metadata and some privacy patterns. They do not prove that a generated statement follows logically from the cited source. The generation validator now also rejects `analyzed` responses with no legal basis. A provider error produces safe abstention instead of leaking provider payloads.

Lite article summaries have no certified effective-date snapshot. The UI therefore shows pending source/date checks, withholds legal/sentencing conclusions and requests review. A complete legal-answer demonstration requires verified statutes and a reviewed evaluation set.

The trace is an execution summary, not hidden model reasoning. Lite explicitly labels precomputed classification, live BM25, deterministic generation and live output checks. It does not claim Dense, RRF or Reranker execution.
