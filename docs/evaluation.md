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

## Mock API contract regression

Run `python scripts/evaluate_demo.py --mock-provider`. The [30 requests](../demo/evaluation/e2e_cases.jsonl) contain 24 distinct facts: three presets at three dates and 21 edited/custom/privacy/adversarial inputs. The HTTP mock intercepts the real SDK/client requests; filtering, BM25, vector search, RRF, index mapping, generation parsing and validators execute normally.

See [results.json](../demo/evaluation/results.json) for current results. Outputs explicitly identify `mock_api_contract` execution. All inputs expect legal abstention because no demo statute is verified. Empty-citation responses pass membership vacuously, so the report includes a citation count and a generation-fallback count. These rates do not measure semantic grounding, model inference quality or useful legal answering. Mock latency is not Bailian latency.

Tests also exercise missing keys, embedding/reranker outages with no sparse fallback, provider-error sanitization, invalid citations and one-repair generation fallback. CI makes no paid provider calls. The frontend is built and exercised using visibly labelled mock responses, plus missing-configuration checks.

For a live run, configure `.env` and run `python scripts/evaluate_demo.py`. This consumes provider quota and writes separate ignored `live-results.json` and `live-outputs.jsonl`. A local live run was not possible because no credentials were supplied. Full BF16/private-corpus inference and Docker execution also remain unverified.

## Next evaluation gates

Run the live API contract check, then corrected independent BF16 Test, verify statute snapshots, collect legal-reviewer relevance labels and compare Hybrid against BM25. Keep structural correctness, model quality, useful answering and abstention quality as separate measures.
