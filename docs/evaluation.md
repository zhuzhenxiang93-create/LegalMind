# Evaluation

## Classification — Validation metrics

| Metric | Result |
|---|---:|
| Validation Micro-F1 | 0.9150 |
| Validation Macro-F1 | 0.8394 |
| Micro Precision | 0.9311 |
| Micro Recall | 0.8995 |
| Hamming Loss | 0.001027 |
| Labels | 202 |
| Training cases | 120,468 |

Provenance: project-owner supplied training/run record, associated with Qwen3-4B BF16 LoRA. These figures were not recomputed in this release environment. The complete corrected BF16 independent-test artifact and weights were not present in the audited repository snapshots.

**Independent BF16 test evaluation pending corrected evaluator run.** Historical QLoRA test metrics are separate experiments and must not be substituted.

The BF16 audit loader/evaluator changes have been integrated. The best checkpoint is recorded as `checkpoint-7500`; final update count is 7,530. Full Mode requires a matching label mapping and calibrated thresholds rather than silently selecting a historical calibration file.

## Synthetic/demo E2E regression

Run `python scripts/evaluate_demo.py` after installing the package. Inputs: [30 requests](../demo/evaluation/e2e_cases.jsonl), comprising 24 distinct facts: three presets at three dates, plus 21 custom/edited/privacy/adversarial inputs. This is a contract and fail-closed regression set, not a legal benchmark.

| Measure | Observed result |
|---|---:|
| Pipeline success | 30/30 |
| Pydantic response validity | 30/30 |
| Citation whitelist validity, by response | 30/30 |
| Unknown Evidence IDs | 0 / 18 cited IDs |
| Expected abstention | 30/30 |
| Manual review | 30/30 |
| Custom inputs without fabricated predictions | 21/21 |

All items expect legal abstention because statute metadata is unverified or input classification is unsupported. These rates do **not** establish useful legal answering, balanced abstention quality, review selectivity, classifier accuracy, semantic grounding or production reliability. Empty-citation responses pass the membership check vacuously; the citation denominator above makes this explicit. Negative tests separately inject unknown citations, inconsistent abstention and missing legal support.

Timing values are saved in [results.json](../demo/evaluation/results.json). They measure in-process CPU Lite only, excluding HTTP, UI, model loading, LoRA inference and external LLM latency. They must not be quoted as Full Mode latency.

## Validation scope

- Existing research and new demo tests: recorded in the release report.
- Frontend: production build plus real browser interaction with three presets and mobile overflow check.
- Full BF16 and real API/Hybrid E2E: not run; weights, indexes and credentials absent.
- Docker: configuration supplied, execution unverified because Docker is unavailable locally.

## Next evaluation gates

Obtain licensed provenance, run corrected independent BF16 Test, verify statute snapshots, label charge-confusion/abstention examples with legal reviewers, and compare real Hybrid with the default retriever using human relevance judgments. Keep schema/citation metrics separate from semantic/legal correctness.
