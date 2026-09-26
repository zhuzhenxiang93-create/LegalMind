# Recruiting release audit — 2026-09-27

## Source integration

Reviewed four repository branches through immutable commit snapshots. Main was `d429411ae43d3e8d6e7f488a9540780c9aeb56e6`; the common research source was `c2b499919d51f631b9fb006e6b518f4ef716d593`. Integrated retrieval work from `f28cab9dea1d96c7ddb96480555fb33395bd5c41` and BF16 loader/evaluator work from `6c9204c7627b844e2124c17fc943d1611422fc82`. The two research tips had diverged by 15 commits each. No existing history was rewritten.

The old README still described active QLoRA training and inconsistent generation defaults. The recruiting README now uses the owner's BF16 training record, marks metrics as Validation, and separates actual runtime modes from historical experiments. No corrected independent BF16 test artifact was found.

Fixed a literal escaped-newline syntax error in the integrated training import. Removed the stale module that conflicted with the pipeline package. Default configuration no longer selects historical classifier thresholds or checkpoint-7530. Full startup requires explicit assets. Historical absolute user paths were replaced with placeholders, and public-facing internal development labels were removed.

## Implementation

- React/Vite evidence workspace with desktop/mobile layouts, presets, score bars, evidence cards, legal-source status, JSON inspection and six-stage trace.
- FastAPI Lite backend, exact-match illustrative scores, live BM25, strict schemas, citation membership checks and explicit legal abstention.
- Full adapter for existing BF16/retrieval/grounded-generation components, with required asset validation and no silent Lite fallback.
- Generation provider failure handling, bounded repair and missing-legal-basis rejection.
- OpenAI-compatible requests omit provider-specific `top_k` unless explicitly configured.
- Three authored cases, six synthetic retrieved records, 30-request regression, expected outputs and screenshot assets.
- CI, Docker files, rewritten README, architecture/evaluation/full-mode documentation and MIT code license.

## Local verification

- `pytest -q`: **150 passed**. One dependency deprecation warning from FastAPI/Starlette test client.
- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `npm run build`: passed.
- Installed package CLI Lite smoke: passed.
- Browser: all three presets completed; no JavaScript errors; 390px viewport had no horizontal overflow.
- Synthetic/demo evaluation: 30/30 pipeline/schema/citation checks; zero unknown IDs across 18 citations; all 30 expected abstentions and reviews. This does not measure legal accuracy or selective review quality.
- Public-tree scan: no private-key/API-key/token patterns, personal cluster paths or model weights detected. Pattern scanning is not a forensic audit of historical commits.

## Remaining external gates

- Repository rename to `LegalMind-RAG`: current connector has no repository-administration mutation; owner action required in Settings → General → Repository name → Rename. Existing GitHub links redirect after rename; update canonical README/UI URLs and badge to the new name afterward.
- Full BF16/real Hybrid/API execution: needs privately held licensed weights, calibrated mapping/thresholds, local indexes and credentials.
- Corrected independent BF16 Test: pending external evaluator run.
- Statute source/time verification: Lite summaries remain unverified and never displayed as approved legal evidence.
- Docker startup: not executed; Docker unavailable in the environment.
- Hosted public URL: not deployed. Local UI is runnable through native setup or supplied Compose configuration.

This release is a runnable CPU recruiting demonstration and an integrated research codebase. These external gates prevent claiming complete Full Mode or legal-validity acceptance.
