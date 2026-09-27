# Bailian live validation — 2026-09-27

The three provider probes succeeded: `text-embedding-v4` returned 1,024-dimensional vectors, `qwen3-rerank` returned relevance scores, and `qwen-plus` returned JSON. The tested Beijing endpoints were `https://dashscope.aliyuncs.com/compatible-mode/v1` and `https://dashscope.aliyuncs.com/compatible-api/v1/reranks`. No credential is stored in the repository.

## Issue discovered and corrected

Initial live generations sometimes cited synthetic cases as legal authority and were correctly rejected. The grounded-generation policy is now sent as a system message. When the packet contains no statutes, the prompt explicitly requires abstention, empty legal/sentencing claims, low confidence and manual review. The existing validator remains authoritative, with at most one repair followed by a labelled fallback.

After this change, the theft preset passed at three dates (one repair at 2020-01-01, first-pass validation at 2026-01-01 and 2030-01-01). The final three-preset check below uses 2026-01-01 throughout.

| Preset | Hybrid retrieval | Qwen-Plus | Validation | Observed latency |
|---|---|---|---|---:|
| clear-theft | BM25 + Dense → RRF → Reranker | Live, first attempt | Passed | 32.00 s |
| ambiguous-taking | BM25 + Dense → RRF → Reranker | Live, first attempt | Passed | 39.56 s |
| insufficient-facts | Skipped: no supported charge routing | Live, first attempt | Passed | 10.78 s |

Final check: 3/3 valid schemas, 3/3 valid citation membership checks (six cited IDs, zero unknown IDs), zero generation fallbacks. See [machine-readable results](../demo/evaluation/bailian-live-2026-09-27.json).

All three outputs use `insufficient_evidence` and require manual review because no verified statutes are available. This successful execution validates the live API integration over synthetic evidence; it does not establish legal accuracy, classifier quality or useful legal-answer reliability. Empty citation lists pass membership checks vacuously. The BF16 classifier and private corpus remain untested. Timings include the execution environment and network, with mixed cold/warm index state; they are not a performance benchmark.

The 30-request offline regression and screenshots remain explicitly marked mock fixtures. The live three-preset run is recorded separately. The final run is distinct from the earlier diagnostic failures, which are retained in this narrative rather than hidden in aggregate success rates.
